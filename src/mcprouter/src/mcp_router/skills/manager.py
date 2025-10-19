from __future__ import annotations

import json
import math
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import yaml

from ..redaction import mask_sensitive

SKILLS_DIR_NAME = "skills"
AGENTS_DIR_NAME = "agents"
DEFAULT_CACHE_DIR = Path(".mcp/cache")
DEFAULT_TELEMETRY_DIR = Path("telemetry/skills")
DEFAULT_METADATA_CACHE = "skills_metadata.json"
DEFAULT_EMBEDDING_CACHE = "skills_embeddings.json"


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    word = []
    for ch in text.lower():
        if ch.isalnum():
            word.append(ch)
        else:
            if word:
                tokens.append("".join(word))
                word.clear()
    if word:
        tokens.append("".join(word))
    return tokens


@dataclass(frozen=True)
class SkillMetadata:
    """Minimal metadata captured from SKILL.md frontmatter."""

    name: str
    description: str
    path: Path
    rel_path: str
    frontmatter_hash: str
    mtime: float
    enabled: bool
    allow_exec: bool
    registry_tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "path": self.rel_path,
            "frontmatter_hash": self.frontmatter_hash,
            "mtime": self.mtime,
            "enabled": self.enabled,
            "allow_exec": self.allow_exec,
            "tags": list(self.registry_tags),
        }


@dataclass(frozen=True)
class SkillMatch:
    """Result returned by SkillManager when a match is found."""

    metadata: SkillMetadata
    score: float
    threshold: float
    keyword_score: float
    embedding_score: Optional[float]

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "path": self.metadata.rel_path,
            "score": self.score,
            "threshold": self.threshold,
            "keyword_score": self.keyword_score,
            "enabled": self.metadata.enabled,
            "allow_exec": self.metadata.allow_exec,
        }
        if self.embedding_score is not None:
            payload["embedding_score"] = self.embedding_score
        return payload


class SkillManager:
    """Load Skill metadata, embeddings, and provide match operations."""

    def __init__(
        self,
        *,
        root: Path,
        feature_flags: Mapping[str, Any] | None = None,
        cache_dir: Path | None = None,
        telemetry_dir: Path | None = None,
        embedder: Callable[[Sequence[str]], Sequence[Sequence[float]]] | None = None,
        top_k: int = 3,
        threshold: float = 0.75,
    ) -> None:
        self._root = root
        raw_flags = feature_flags or {}
        self._feature_flags = {k: self._coerce_bool(v) for k, v in raw_flags.items()}
        self._enabled = self._feature_flags.get("skills_v1", False)
        self._skills_exec_enabled = self._feature_flags.get("skills_exec", False)
        self._embedder = embedder
        self._top_k = max(1, top_k)
        self._threshold = max(0.0, min(1.0, threshold))
        self._cache_dir = cache_dir or (self._root / DEFAULT_CACHE_DIR)
        self._telemetry_dir = telemetry_dir or (self._root / DEFAULT_TELEMETRY_DIR)
        self._metadata_cache_path = self._cache_dir / DEFAULT_METADATA_CACHE
        self._embedding_cache_path = self._cache_dir / DEFAULT_EMBEDDING_CACHE
        self._telemetry_path = self._telemetry_dir / "events.jsonl"
        self._telemetry_lock = threading.Lock()

        self._metadata_by_path: dict[str, SkillMetadata] = {}
        self._embeddings: dict[str, list[float]] = {}
        self._bm25_index: dict[str, dict[str, float]] = {}
        self._avg_doc_len = 0.0

        if self._enabled:
            self.refresh_metadata()
            self._load_embeddings()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def exec_enabled(self) -> bool:
        return self._skills_exec_enabled

    def refresh_metadata(self) -> None:
        """Scan Skills directories and write the metadata cache."""

        discovered = {meta.rel_path: meta for meta in self._discover_metadata()}
        self._metadata_by_path = discovered
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        serialized = {rel_path: meta.to_dict() for rel_path, meta in sorted(discovered.items())}
        payload = {"generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"), "skills": serialized}
        self._metadata_cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._build_bm25_index()

    def list_enabled(self) -> list[SkillMetadata]:
        if not self._enabled:
            return []
        return [meta for meta in self._metadata_by_path.values() if meta.enabled]

    def list_all(self) -> list[SkillMetadata]:
        return list(self._metadata_by_path.values())

    def match(self, query: str) -> list[SkillMatch]:
        if not self._enabled:
            return []
        trimmed = query.strip()
        if not trimmed:
            return []
        candidates = self.list_enabled()
        if not candidates:
            return []
        keyword_scores = self._score_keyword(trimmed, candidates)
        embedding_scores = self._score_embeddings(trimmed, candidates)
        results: list[SkillMatch] = []
        for meta in candidates:
            kw_score = keyword_scores.get(meta.rel_path, 0.0)
            emb_score = embedding_scores.get(meta.rel_path)
            if emb_score is not None:
                blended = (emb_score * 0.7) + (kw_score * 0.3)
            else:
                blended = kw_score
            if blended < self._threshold:
                continue
            results.append(
                SkillMatch(
                    metadata=meta,
                    score=blended,
                    threshold=self._threshold,
                    keyword_score=kw_score,
                    embedding_score=emb_score,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        final = results[: self._top_k]
        self._emit_event(
            "skill_selected",
            {
                "query_preview": trimmed[:160],
                "threshold": self._threshold,
                "selected": [item.to_dict() | {"rank": idx + 1} for idx, item in enumerate(final)],
                "available": len(candidates),
                "feature_flag": "skills_v1",
            },
        )
        return final

    def load_body(self, metadata: SkillMetadata, *, max_tokens: int = 5000) -> tuple[str, int, bool]:
        raw = metadata.path.read_text(encoding="utf-8")
        _, body = self._split_frontmatter(raw)
        tokens = 0
        truncated = False
        collected: list[str] = []
        for line in body.splitlines():
            line_tokens = line.split()
            if not line_tokens:
                collected.append(line)
                continue
            projected = tokens + len(line_tokens)
            if projected <= max_tokens:
                collected.append(line)
                tokens = projected
            else:
                remaining = max_tokens - tokens
                if remaining > 0:
                    snippet = " ".join(line_tokens[:remaining])
                    collected.append(snippet)
                    tokens += remaining
                truncated = True
                break
        if not collected:
            payload = ""
        else:
            payload = "\n".join(collected).strip()
        self._emit_event(
            "skill_loaded",
            {
                "path": metadata.rel_path,
                "tokens": tokens,
                "truncated": truncated,
                "allow_exec": metadata.allow_exec and self._skills_exec_enabled,
            },
        )
        return payload, tokens, truncated

    def prepare_payload(self, query: str) -> list[dict[str, Any]]:
        matches = self.match(query)
        prepared: list[dict[str, Any]] = []
        for idx, match in enumerate(matches, start=1):
            body, tokens, truncated = self.load_body(match.metadata)
            prepared.append(
                {
                    "name": match.metadata.name,
                    "description": match.metadata.description,
                    "path": match.metadata.rel_path,
                    "rank": idx,
                    "score": match.score,
                    "threshold": match.threshold,
                    "body": body,
                    "tokens": tokens,
                    "truncated": truncated,
                    "allow_exec": match.metadata.allow_exec and self._skills_exec_enabled,
                }
            )
        return prepared

    # ------------------------------------------------------------------ #
    # Discovery and indexing
    # ------------------------------------------------------------------ #
    def _discover_metadata(self) -> Iterable[SkillMetadata]:
        registry = self._load_registry()
        for skill_path in self._iter_skill_files():
            rel_path = skill_path.relative_to(self._root).as_posix()
            if rel_path not in registry:
                continue
            registry_entry = registry[rel_path]
            frontmatter, _ = self._read_skill(skill_path)
            name = str(frontmatter.get("name", "")).strip()
            description = str(frontmatter.get("description", "")).strip()
            if not name or not description:
                continue
            data = json.dumps(frontmatter, sort_keys=True, ensure_ascii=False)
            digest = sha256(data.encode("utf-8")).hexdigest()
            meta = SkillMetadata(
                name=name,
                description=description,
                path=skill_path,
                rel_path=rel_path,
                frontmatter_hash=digest,
                mtime=skill_path.stat().st_mtime,
                enabled=bool(registry_entry.get("enabled")),
                allow_exec=bool(registry_entry.get("allow_exec")),
                registry_tags=tuple(str(tag) for tag in registry_entry.get("tags", []) if isinstance(tag, str)),
            )
            yield meta

    def _iter_skill_files(self) -> Iterable[Path]:
        shared_root = self._root / SKILLS_DIR_NAME
        if shared_root.exists():
            for path in shared_root.rglob("SKILL.md"):
                if self._should_skip(path):
                    continue
                yield path
        agents_root = self._root / AGENTS_DIR_NAME
        if agents_root.exists():
            for path in agents_root.rglob("skills"):
                if self._should_skip(path):
                    continue
                for skill_file in path.rglob("SKILL.md"):
                    if self._should_skip(skill_file):
                        continue
                    yield skill_file

    @staticmethod
    def _should_skip(path: Path) -> bool:
        return any(part.startswith("_") or part.startswith(".") for part in path.parts)

    def _load_registry(self) -> dict[str, dict[str, Any]]:
        registry_path = self._root / SKILLS_DIR_NAME / "registry.json"
        if not registry_path.exists():
            return {}
        try:
            data = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        skills = data.get("skills")
        if not isinstance(skills, list):
            return {}
        entries: dict[str, dict[str, Any]] = {}
        for entry in skills:
            if not isinstance(entry, dict):
                continue
            rel_path = str(entry.get("path") or "").strip()
            if not rel_path:
                continue
            entries[rel_path] = entry
        return entries

    def _read_skill(self, path: Path) -> tuple[dict[str, Any], str]:
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = self._split_frontmatter(raw)
        data = yaml.safe_load(frontmatter) or {}
        if not isinstance(data, dict):
            data = {}
        return data, body

    @staticmethod
    def _split_frontmatter(raw: str) -> tuple[str, str]:
        if not raw.startswith("---"):
            return "", raw
        parts = raw.split("---", 2)
        if len(parts) < 3:
            return parts[1] if len(parts) > 1 else "", ""
        frontmatter = parts[1].strip("\n")
        body = parts[2]
        return frontmatter, body

    # ------------------------------------------------------------------ #
    # Embedding handling
    # ------------------------------------------------------------------ #
    def _load_embeddings(self) -> None:
        if not self._embedding_cache_path.exists():
            self._embeddings = {}
            return
        try:
            payload = json.loads(self._embedding_cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._embeddings = {}
            return
        vectors = payload.get("embeddings")
        if not isinstance(vectors, dict):
            self._embeddings = {}
            return
        result: dict[str, list[float]] = {}
        for rel_path, vector in vectors.items():
            if not isinstance(vector, list):
                continue
            try:
                normalized = [float(item) for item in vector]
            except (TypeError, ValueError):
                continue
            result[rel_path] = normalized
        self._embeddings = result

    def _score_embeddings(self, query: str, candidates: Sequence[SkillMetadata]) -> dict[str, float]:
        if not self._embedder:
            return {}
        try:
            query_vector = self._embedder([query])[0]
        except Exception:  # pylint: disable=broad-except
            self._emit_event("skill_embedding_fallback", {"reason": "embedder_error"})
            return {}
        if not isinstance(query_vector, Sequence) or not query_vector:
            return {}
        scores: dict[str, float] = {}
        for meta in candidates:
            vector = self._embeddings.get(meta.rel_path)
            if not vector:
                continue
            score = self._cosine_similarity(query_vector, vector)
            normalized = (score + 1.0) / 2.0
            scores[meta.rel_path] = max(0.0, min(1.0, normalized))
        return scores

    @staticmethod
    def _cosine_similarity(lhs: Sequence[float], rhs: Sequence[float]) -> float:
        length = min(len(lhs), len(rhs))
        if length == 0:
            return 0.0
        dot = sum(lhs[i] * rhs[i] for i in range(length))
        norm_l = math.sqrt(sum(lhs[i] * lhs[i] for i in range(length)))
        norm_r = math.sqrt(sum(rhs[i] * rhs[i] for i in range(length)))
        if norm_l == 0.0 or norm_r == 0.0:
            return 0.0
        return dot / (norm_l * norm_r)

    # ------------------------------------------------------------------ #
    # Keyword scoring (BM25-style)
    # ------------------------------------------------------------------ #
    def _build_bm25_index(self) -> None:
        dok: dict[str, dict[str, float]] = {}
        doc_lengths: dict[str, int] = {}
        for rel_path, meta in self._metadata_by_path.items():
            tokens = _tokenize(meta.description)
            doc_lengths[rel_path] = len(tokens)
            counts: dict[str, int] = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1
            dok[rel_path] = {token: float(count) for token, count in counts.items()}
        self._bm25_index = dok
        if doc_lengths:
            self._avg_doc_len = sum(doc_lengths.values()) / len(doc_lengths)
        else:
            self._avg_doc_len = 0.0

    def _score_keyword(self, query: str, candidates: Sequence[SkillMetadata]) -> dict[str, float]:
        query_tokens = _tokenize(query)
        if not self._bm25_index or not query_tokens:
            return {}
        doc_count = len(self._bm25_index)
        token_document_frequency: dict[str, int] = {}
        for index in self._bm25_index.values():
            for token in index.keys():
                token_document_frequency[token] = token_document_frequency.get(token, 0) + 1
        scores: dict[str, float] = {}
        for meta in candidates:
            tf = self._bm25_index.get(meta.rel_path, {})
            doc_len = sum(tf.values())
            score = 0.0
            for token in query_tokens:
                df = token_document_frequency.get(token, 0)
                if df == 0:
                    continue
                idf = math.log((doc_count - df + 0.5) / (df + 0.5) + 1)
                term_freq = tf.get(token, 0.0)
                k1 = 1.5
                b = 0.75
                denom = term_freq + k1 * (1 - b + b * (doc_len / (self._avg_doc_len or 1.0)))
                score += idf * ((term_freq * (k1 + 1)) / (denom or 1.0))
            scores[meta.rel_path] = score
        max_score = max(scores.values(), default=0.0)
        if max_score > 0:
            scores = {path: min(1.0, score / max_score) for path, score in scores.items()}
        return scores

    # ------------------------------------------------------------------ #
    # Telemetry
    # ------------------------------------------------------------------ #
    def _emit_event(self, event: str, data: Mapping[str, Any]) -> None:
        payload = {
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "event": event,
            "data": mask_sensitive(dict(data)),
        }
        serialized = json.dumps(payload, ensure_ascii=False)
        self._telemetry_dir.mkdir(parents=True, exist_ok=True)
        with self._telemetry_lock:
            with self._telemetry_path.open("a", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.write("\n")

    # ------------------------------------------------------------------ #
    # Flag helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _coerce_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"", "0", "false", "off", "no", "none", "null"}:
                return False
            if normalized in {"1", "true", "on", "yes"}:
                return True
        return bool(value)


__all__ = ["SkillManager", "SkillMatch", "SkillMetadata"]

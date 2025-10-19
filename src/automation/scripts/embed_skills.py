#!/usr/bin/env python
"""Generate offline embeddings for Skills metadata."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from mcp_router.skills import SkillManager


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Embed Skill descriptions using a local transformer.")
    parser.add_argument(
        "--model",
        default="BAAI/bge-large-en",
        help="SentenceTransformer model to load (default: BAAI/bge-large-en).",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing skills/ and agents/ directories (default: current directory).",
    )
    return parser


def _load_transformer(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - dependency missing handled at runtime
        raise SystemExit("sentence-transformers package is required for embed_skills.py") from exc
    try:
        return SentenceTransformer(model_name)
    except Exception as exc:  # pragma: no cover - model load failures handled at runtime
        raise SystemExit(f"failed to load SentenceTransformer model '{model_name}': {exc}") from exc


def _encode(transformer, texts: Sequence[str]) -> list[list[float]]:
    vectors = transformer.encode(list(texts), normalize_embeddings=True)
    return [list(map(float, vector)) for vector in vectors]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"repository root not found: {root}")

    mcprouter_src = root / "src/mcprouter/src"
    if mcprouter_src.exists():
        sys.path.insert(0, str(mcprouter_src))

    from mcp_router.skills import SkillManager  # pylint: disable=import-error

    transformer = _load_transformer(args.model)

    manager = SkillManager(
        root=root,
        feature_flags={"skills_v1": True},
        cache_dir=root / ".mcp/cache",
        telemetry_dir=root / "telemetry/skills",
        embedder=lambda payload: _encode(transformer, payload),
    )
    manager.refresh_metadata()

    skills = sorted(manager.list_all(), key=lambda item: item.rel_path)
    if not skills:
        print("No skills discovered; nothing to embed.", file=sys.stderr)
        return 0

    inputs = [f"{skill.name}\n{skill.description}" for skill in skills]
    vectors = _encode(transformer, inputs)

    payload = {
        "model": args.model,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "embeddings": {
            skill.rel_path: vector for skill, vector in zip(skills, vectors, strict=True)
        },
        "frontmatter_hashes": {
            skill.rel_path: skill.frontmatter_hash for skill in skills
        },
    }
    cache_path = root / ".mcp/cache/skills_embeddings.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote embeddings for {len(skills)} skills to {cache_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

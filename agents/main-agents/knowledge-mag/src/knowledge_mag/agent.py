"""KnowledgeMag flow-runner main agent implementation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Topic:
    """Represents a knowledge topic or capability to curate."""

    name: str
    intents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "Topic":
        if "name" not in payload or not str(payload["name"]).strip():
            raise ValueError("Each topic requires a non-empty 'name'.")
        name = str(payload["name"]).strip()
        intents = cls._coerce_list(payload.get("intents", []))
        dependencies = cls._coerce_list(payload.get("dependencies", []))
        gaps = cls._coerce_list(payload.get("gaps", []))
        return cls(name=name, intents=intents, dependencies=dependencies, gaps=gaps)

    @staticmethod
    def _coerce_list(raw: Any) -> List[str]:
        if isinstance(raw, list):
            return [str(item).strip() for item in raw if str(item).strip()]
        if isinstance(raw, str):
            return [segment.strip() for segment in raw.splitlines() if segment.strip()]
        return []


@dataclass
class SourceRecord:
    """Structured reference metadata for knowledge artefacts."""

    source_id: str
    title: str
    uri: str
    doc_type: Optional[str] = None
    last_reviewed: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "SourceRecord":
        required = {"id", "title", "uri"}
        missing = [key for key in required if key not in payload or not str(payload[key]).strip()]
        if missing:
            raise ValueError(f"Knowledge source missing required fields: {', '.join(sorted(missing))}")
        doc_type = payload.get("type")
        return cls(
            source_id=str(payload["id"]).strip(),
            title=str(payload["title"]).strip(),
            uri=str(payload["uri"]).strip(),
            doc_type=str(doc_type).strip() if doc_type else None,
            last_reviewed=str(payload.get("last_reviewed", "")).strip() or None,
        )


@dataclass
class KnowledgeRequest:
    """Wrapper around KnowledgeMag request payloads."""

    id: str
    version: str
    knowledge_domain: str
    title: str
    summary: str
    audience: List[str]
    topics: List[Topic]
    sources: List[SourceRecord]
    tags: List[str] = field(default_factory=list)
    outstanding_questions: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "KnowledgeRequest":
        required = {"id", "version", "knowledge_domain", "title", "summary", "audience", "topics"}
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Knowledge request missing required fields: {', '.join(sorted(missing))}")
        audience_raw = payload.get("audience")
        if isinstance(audience_raw, list):
            audience = [str(item).strip() for item in audience_raw if str(item).strip()]
        elif isinstance(audience_raw, str):
            audience = [segment.strip() for segment in audience_raw.split(",") if segment.strip()]
        else:
            raise ValueError("'audience' must be a list or comma-separated string.")
        topics_payload = payload.get("topics", [])
        if not isinstance(topics_payload, list) or not topics_payload:
            raise ValueError("Knowledge request must include a non-empty 'topics' array.")
        topics = [Topic.from_mapping(topic) for topic in topics_payload]
        sources_payload = payload.get("sources", [])
        if not isinstance(sources_payload, list):
            raise ValueError("'sources' must be an array when provided.")
        sources = [SourceRecord.from_mapping(source) for source in sources_payload]
        tags = Topic._coerce_list(payload.get("tags", []))
        outstanding = Topic._coerce_list(payload.get("outstanding_questions", []))
        return cls(
            id=str(payload["id"]),
            version=str(payload["version"]),
            knowledge_domain=str(payload["knowledge_domain"]),
            title=str(payload["title"]).strip(),
            summary=str(payload["summary"]).strip(),
            audience=audience,
            topics=topics,
            sources=sources,
            tags=tags,
            outstanding_questions=outstanding,
        )


class KnowledgeMag:
    """Flow Runner compatible agent that curates knowledge collections."""

    def __init__(self) -> None:
        pass

    async def run(
        self,
        request: Optional[Dict[str, Any]] = None,
        request_path: Optional[str] = None,
        output_path: Optional[str] = None,
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Entry point invoked by Flow Runner for knowledge management tasks."""

        payload = self._load_request(request=request, request_path=request_path)
        knowledge_request = KnowledgeRequest.from_mapping(payload)

        start = time.perf_counter()
        cards = self._compose_cards(knowledge_request)
        source_index = self._build_source_index(knowledge_request.sources)
        review_notes = self._collect_review_notes(knowledge_request)
        followups = self._collect_followups(knowledge_request, cards)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        confidence = self._estimate_confidence(knowledge_request, review_notes, followups)

        response: Dict[str, Any] = {
            "id": knowledge_request.id,
            "version": knowledge_request.version,
            "knowledge_domain": knowledge_request.knowledge_domain,
            "title": knowledge_request.title,
            "summary": knowledge_request.summary,
            "audience": knowledge_request.audience,
            "tags": knowledge_request.tags,
            "knowledge_cards": cards,
            "source_index": source_index,
            "review_notes": review_notes,
            "follow_up_questions": followups,
            "diagnostics": {
                "latency_ms": latency_ms,
                "confidence": confidence,
                "metrics": {
                    "knowledge.latency_ms": latency_ms,
                    "knowledge.topic_count": len(cards),
                    "knowledge.source_count": len(source_index),
                },
            },
        }

        if output_path:
            self._write_output(Path(output_path), response)

        return response

    # ------------------------------------------------------------------
    def _load_request(
        self,
        *,
        request: Optional[Dict[str, Any]],
        request_path: Optional[str],
    ) -> Dict[str, Any]:
        if request is not None:
            return dict(request)
        if not request_path:
            raise ValueError("Either 'request' or 'request_path' must be provided to KnowledgeMag")
        payload = json.loads(Path(request_path).expanduser().read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Knowledge request JSON must contain an object root")
        return payload

    def _compose_cards(self, req: KnowledgeRequest) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        for index, topic in enumerate(req.topics, start=1):
            overview = self._summarize_topic(topic)
            actions = self._derive_actions(topic)
            references = self._infer_references(topic, req.sources)
            cards.append(
                {
                    "topic": topic.name,
                    "sequence": index,
                    "overview": overview,
                    "key_intents": topic.intents,
                    "recommended_actions": actions,
                    "dependencies": topic.dependencies,
                    "source_refs": references,
                    "gaps": topic.gaps,
                }
            )
        return cards

    def _build_source_index(self, sources: List[SourceRecord]) -> List[Dict[str, Any]]:
        index: List[Dict[str, Any]] = []
        for source in sources:
            index.append(
                {
                    "id": source.source_id,
                    "title": source.title,
                    "uri": source.uri,
                    "type": source.doc_type or "unspecified",
                    "last_reviewed": source.last_reviewed,
                }
            )
        return index

    def _collect_review_notes(self, req: KnowledgeRequest) -> List[str]:
        notes: List[str] = []
        if not req.sources:
            notes.append("No source records supplied; verify knowledge provenance.")
        stale_sources = [source for source in req.sources if not source.last_reviewed]
        if stale_sources:
            missing = ", ".join(source.source_id for source in stale_sources)
            notes.append(f"Update last_reviewed metadata for sources: {missing}.")
        if any(topic.gaps for topic in req.topics):
            notes.append("Topic gaps identified; ensure follow-up owners are assigned.")
        return notes

    def _collect_followups(self, req: KnowledgeRequest, cards: List[Dict[str, Any]]) -> List[str]:
        questions: List[str] = []
        if req.outstanding_questions:
            questions.extend(req.outstanding_questions)
        uncovered_dependencies = [
            dependency
            for card in cards
            for dependency in card["dependencies"]
            if dependency and dependency not in (topic.name for topic in req.topics)
        ]
        if uncovered_dependencies:
            questions.append(
                f"Provide coverage for dependent topics: {', '.join(sorted(set(uncovered_dependencies)))}."
            )
        if len(req.topics) < 2:
            questions.append("Confirm whether additional topics should be captured for completeness.")
        return questions

    def _estimate_confidence(
        self,
        req: KnowledgeRequest,
        review_notes: List[str],
        followups: List[str],
    ) -> float:
        base = 0.88
        if review_notes:
            base -= 0.12
        if followups:
            base -= 0.1
        if any(topic.gaps for topic in req.topics):
            base -= 0.1
        return max(0.3, round(base, 2))

    def _summarize_topic(self, topic: Topic) -> str:
        if topic.intents:
            return "; ".join(topic.intents)
        if topic.dependencies:
            return f"Depends on: {', '.join(topic.dependencies)}"
        return "Topic captured without explicit intents."

    def _derive_actions(self, topic: Topic) -> List[str]:
        actions: List[str] = []
        for intent in topic.intents:
            actions.append(f"Operationalise intent: {intent}")
        for gap in topic.gaps:
            actions.append(f"Resolve gap: {gap}")
        if not actions:
            actions.append("Document ownership and next review date.")
        return actions

    def _infer_references(self, topic: Topic, sources: List[SourceRecord]) -> List[str]:
        matches: List[str] = []
        topic_key = topic.name.lower()
        for source in sources:
            if topic_key in source.title.lower():
                matches.append(source.source_id)
        return matches

    def _write_output(self, path: Path, payload: Dict[str, Any]) -> None:
        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

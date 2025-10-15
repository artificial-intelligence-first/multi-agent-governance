"""DocsSAG flow-runner sub-agent implementation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


@dataclass
class SourceSection:
    """Represents a requested documentation section."""

    heading: str
    key_points: List[str] = field(default_factory=list)
    knowledge_refs: List[str] = field(default_factory=list)
    details: str = ""
    status: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "SourceSection":
        if "heading" not in payload or not str(payload["heading"]).strip():
            raise ValueError("Each section requires a non-empty 'heading'.")
        heading = str(payload["heading"]).strip()
        key_points_raw = payload.get("key_points", [])
        if isinstance(key_points_raw, list):
            key_points = [str(point).strip() for point in key_points_raw if str(point).strip()]
        elif isinstance(key_points_raw, str):
            key_points = [segment.strip() for segment in key_points_raw.splitlines() if segment.strip()]
        else:
            raise ValueError(f"Unsupported type for key_points in section '{heading}'.")
        knowledge_refs_raw = payload.get("knowledge_refs", [])
        if isinstance(knowledge_refs_raw, list):
            knowledge_refs = [str(ref).strip() for ref in knowledge_refs_raw if str(ref).strip()]
        elif isinstance(knowledge_refs_raw, str):
            knowledge_refs = [segment.strip() for segment in knowledge_refs_raw.split(",") if segment.strip()]
        else:
            knowledge_refs = []
        details = str(payload.get("details", "")).strip()
        status = payload.get("status")
        status_str = str(status).strip() if status is not None else None
        return cls(
            heading=heading,
            key_points=key_points,
            knowledge_refs=knowledge_refs,
            details=details,
            status=status_str or None,
        )


@dataclass
class DocumentationRequest:
    """Wrapper around DocsSAG request payloads."""

    id: str
    version: str
    doc_type: str
    title: str
    summary: str
    audience: str
    sections: List[SourceSection]
    style_tone: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "DocumentationRequest":
        required = {"id", "version", "doc_type", "title", "summary", "audience", "sections"}
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Documentation request missing required fields: {', '.join(sorted(missing))}")
        sections_payload = payload.get("sections", [])
        if not isinstance(sections_payload, list) or not sections_payload:
            raise ValueError("Documentation request must include a non-empty 'sections' array.")
        sections = [SourceSection.from_mapping(section) for section in sections_payload]
        constraints_raw = payload.get("constraints", [])
        if isinstance(constraints_raw, list):
            constraints = [str(item).strip() for item in constraints_raw if str(item).strip()]
        elif isinstance(constraints_raw, str):
            constraints = [segment.strip() for segment in constraints_raw.splitlines() if segment.strip()]
        else:
            constraints = []
        references_raw = payload.get("references", [])
        if isinstance(references_raw, list):
            references = [str(item).strip() for item in references_raw if str(item).strip()]
        elif isinstance(references_raw, str):
            references = [segment.strip() for segment in references_raw.splitlines() if segment.strip()]
        else:
            references = []
        style_tone = payload.get("style_tone")
        style = str(style_tone).strip() if style_tone else None
        return cls(
            id=str(payload["id"]),
            version=str(payload["version"]),
            doc_type=str(payload["doc_type"]),
            title=str(payload["title"]),
            summary=str(payload["summary"]).strip(),
            audience=str(payload["audience"]).strip(),
            sections=sections,
            style_tone=style or None,
            constraints=constraints,
            references=references,
        )


class DocsSAG:
    """Flow Runner compatible sub-agent that assembles documentation deliverables."""

    def __init__(self) -> None:
        self._repo_root = Path(__file__).resolve().parents[5]

    async def run(
        self,
        request: Optional[Dict[str, Any]] = None,
        request_path: Optional[str] = None,
        output_path: Optional[str] = None,
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Entry point invoked by Flow Runner for documentation tasks."""

        payload = self._load_request(request=request, request_path=request_path)
        doc_request = DocumentationRequest.from_mapping(payload)

        start = time.perf_counter()
        sections = self._compose_sections(doc_request)
        markdown = self._compose_markdown(doc_request, sections)
        review_notes = self._collect_review_notes(doc_request)
        followups = self._collect_followups(doc_request, sections, review_notes)
        markdown_path = self._persist_markdown(doc_request, markdown)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        confidence = self._estimate_confidence(doc_request, review_notes, followups)

        response: Dict[str, Any] = {
            "id": doc_request.id,
            "version": doc_request.version,
            "doc_type": doc_request.doc_type,
            "title": doc_request.title,
            "audience": doc_request.audience,
            "summary": doc_request.summary,
            "document_markdown": markdown,
            "sections": sections,
            "review_notes": review_notes,
            "follow_up_questions": followups,
            "diagnostics": {
                "latency_ms": latency_ms,
                "confidence": confidence,
                "metrics": {
                    "docs_sag.latency_ms": latency_ms,
                    "docs_sag.doc_type": doc_request.doc_type,
                    "docs_sag.section_count": len(sections),
                },
                "generated_document_path": markdown_path,
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
            raise ValueError("Either 'request' or 'request_path' must be provided to DocsSAG")
        payload = json.loads(Path(request_path).expanduser().read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Documentation request JSON must contain an object root")
        return payload

    def _compose_sections(self, req: DocumentationRequest) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []
        for index, section in enumerate(req.sections, start=1):
            summary = self._summarize_section(section)
            actions = self._prepare_actions(section)
            sections.append(
                {
                    "heading": section.heading,
                    "sequence": index,
                    "summary": summary,
                    "actions": actions,
                    "knowledge_refs": section.knowledge_refs,
                    "status": section.status or "n/a",
                }
            )
        return sections

    def _compose_markdown(self, req: DocumentationRequest, sections: List[Dict[str, Any]]) -> str:
        lines: List[str] = [
            f"# {req.title}",
            "",
            f"**Document Type:** {req.doc_type}",
            f"**Primary Audience:** {req.audience}",
        ]
        if req.style_tone:
            lines.append(f"**Tone & Style:** {req.style_tone}")
        if req.constraints:
            lines.append("")
            lines.append("**Constraints:**")
            for constraint in req.constraints:
                lines.append(f"- {constraint}")
        lines.append("")
        lines.append(req.summary or "Summary unavailable.")
        lines.append("")

        for item in sections:
            lines.append(f"## {item['heading']}")
            lines.append(item["summary"])
            if item["actions"]:
                lines.append("")
                lines.append("Key Actions:")
                for action in item["actions"]:
                    lines.append(f"- {action}")
            if item["knowledge_refs"]:
                lines.append("")
                lines.append("Knowledge References:")
                for ref in item["knowledge_refs"]:
                    lines.append(f"- {ref}")
            lines.append("")

        if req.references:
            lines.append("## References")
            for reference in req.references:
                lines.append(f"- {reference}")
            lines.append("")

        return "\n".join(lines).strip() + "\n"

    def _collect_review_notes(self, req: DocumentationRequest) -> List[str]:
        notes: List[str] = []
        if not req.style_tone:
            notes.append("Style guidance missing; defaulted to neutral tone.")
        if any(not section.details for section in req.sections):
            notes.append("One or more sections lack detailed content; expand before publication.")
        if req.references:
            missing_links = [ref for ref in req.references if "://" not in ref]
            if missing_links:
                notes.append(f"Verify citation formatting for: {', '.join(missing_links)}.")
        return notes

    def _collect_followups(
        self,
        req: DocumentationRequest,
        sections: List[Dict[str, Any]],
        review_notes: List[str],
    ) -> List[str]:
        questions: List[str] = []
        pending = [note for note in review_notes if "expand" in note.lower()]
        if pending:
            questions.append("Provide detailed source material for sections flagged as incomplete.")
        if req.doc_type.lower() == "runbook" and not any("roll" in section["summary"].lower() for section in sections):
            questions.append("Confirm rollback procedures for the runbook.")
        if len(req.sections) < 3:
            questions.append("Should additional sections be added to cover prerequisites or troubleshooting?")
        return questions

    def _estimate_confidence(
        self,
        req: DocumentationRequest,
        review_notes: List[str],
        followups: List[str],
    ) -> float:
        base = 0.85
        if review_notes:
            base -= 0.15
        if followups:
            base -= 0.1
        if any(section.status and section.status.lower() == "draft" for section in req.sections):
            base -= 0.05
        return max(0.3, round(base, 2))

    def _prepare_actions(self, section: SourceSection) -> List[str]:
        if section.key_points:
            return section.key_points
        if section.details:
            sentences = [sentence.strip() for sentence in section.details.split(".") if sentence.strip()]
            return sentences[:3]
        return []

    def _summarize_section(self, section: SourceSection) -> str:
        if section.details:
            return section.details
        if section.key_points:
            return "; ".join(section.key_points)
        return "Content pending expansion."

    def _write_output(self, path: Path, payload: Dict[str, Any]) -> None:
        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    def _persist_markdown(self, req: DocumentationRequest, markdown: str) -> str:
        """Persist generated Markdown under the repository /docs directory."""

        docs_dir = self._repo_root / "docs" / "generated"
        docs_dir.mkdir(parents=True, exist_ok=True)
        filename = self._build_markdown_filename(req)
        target_path = docs_dir / filename
        target_path.write_text(markdown, encoding="utf-8")
        return str(target_path.relative_to(self._repo_root))

    def _build_markdown_filename(self, req: DocumentationRequest) -> str:
        base = f"{req.id}-{req.title}".strip()
        sanitized = re.sub(r"[^A-Za-z0-9_-]+", "-", base).strip("-").lower()
        if not sanitized:
            sanitized = f"docs-sag-{int(time.time())}"
        return f"{sanitized}.md"

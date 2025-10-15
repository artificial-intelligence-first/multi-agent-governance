"""ContextSAG flow-runner sub-agent implementation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


"""Priority mapping for context inputs (lower value = higher priority)."""

IMPORTANCE_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "optional": 4,
}


@dataclass
class ContextInput:
    """Represents a single context artefact candidate."""

    name: str
    type: str
    summary: str
    importance: str = "medium"
    source: Optional[str] = None
    last_updated: Optional[str] = None
    risks: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "ContextInput":
        required = {"name", "type", "summary"}
        missing = [field for field in required if field not in payload or not str(payload[field]).strip()]
        if missing:
            raise ValueError(
                "Context input missing required fields: "
                f"{', '.join(sorted(missing))}. Received keys: {sorted(payload.keys())}"
            )
        importance = str(payload.get("importance", "medium")).strip().lower() or "medium"
        normalized_importance = importance if importance in IMPORTANCE_ORDER else "medium"
        risks = _coerce_list(payload.get("risks", []))
        tags = _coerce_list(payload.get("tags", []))
        return cls(
            name=str(payload["name"]).strip(),
            type=str(payload["type"]).strip(),
            summary=str(payload["summary"]).strip(),
            importance=normalized_importance,
            source=str(payload.get("source", "")).strip() or None,
            last_updated=str(payload.get("last_updated", "")).strip() or None,
            risks=risks,
            tags=tags,
        )


def _coerce_list(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    if isinstance(raw, str):
        return [segment.strip() for segment in raw.splitlines() if segment.strip()]
    return []


@dataclass
class ContextBriefRequest:
    """Wrapper around ContextSAG request payloads."""

    id: str
    version: str
    objective: str
    primary_use_case: str
    context_inputs: List[ContextInput]
    constraints: List[str] = field(default_factory=list)
    evaluation_checks: List[str] = field(default_factory=list)
    target_models: List[str] = field(default_factory=list)
    audience: List[str] = field(default_factory=list)
    notes: Optional[str] = None

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "ContextBriefRequest":
        required = {"id", "version", "objective", "primary_use_case", "context_inputs"}
        missing = [field for field in required if field not in payload]
        if missing:
            raise ValueError(
                "Context brief missing required fields: "
                f"{', '.join(sorted(missing))}. Received keys: {sorted(payload.keys())}"
            )
        context_payload = payload.get("context_inputs", [])
        if not isinstance(context_payload, list) or not context_payload:
            raise ValueError("Context brief must include a non-empty 'context_inputs' array.")
        context_inputs = [ContextInput.from_mapping(item) for item in context_payload]
        constraints = _coerce_list(payload.get("constraints", []))
        evaluation = _coerce_list(payload.get("evaluation_checks", []))
        target_models = _coerce_list(payload.get("target_models", []))
        audience = _coerce_list(payload.get("audience", []))
        notes = str(payload.get("notes", "")).strip() or None
        return cls(
            id=str(payload["id"]),
            version=str(payload["version"]),
            objective=str(payload["objective"]).strip(),
            primary_use_case=str(payload["primary_use_case"]).strip(),
            context_inputs=context_inputs,
            constraints=constraints,
            evaluation_checks=evaluation,
            target_models=target_models,
            audience=audience,
            notes=notes,
        )


class ContextSAG:
    """Flow Runner compatible sub-agent that assembles context plans."""

    def __init__(self) -> None:
        pass

    async def run(
        self,
        request: Optional[Dict[str, Any]] = None,
        request_path: Optional[str] = None,
        output_path: Optional[str] = None,
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Entry point invoked by Flow Runner for context-engineering tasks."""

        payload = self._load_request(request=request, request_path=request_path)
        brief = ContextBriefRequest.from_mapping(payload)

        start = time.perf_counter()
        prioritized_context = self._prioritize_inputs(brief.context_inputs)
        assembly_plan = self._build_assembly_plan(brief, prioritized_context)
        risk_register = self._compile_risks(brief, prioritized_context)
        followups = self._collect_followups(brief, risk_register)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        confidence = self._estimate_confidence(brief, risk_register, followups)

        response: Dict[str, Any] = {
            "id": brief.id,
            "version": brief.version,
            "objective": brief.objective,
            "primary_use_case": brief.primary_use_case,
            "target_models": brief.target_models,
            "audience": brief.audience,
            "context_briefs": prioritized_context,
            "assembly_plan": assembly_plan,
            "risk_register": risk_register,
            "follow_up_questions": followups,
            "diagnostics": {
                "latency_ms": latency_ms,
                "confidence": confidence,
                "metrics": {
                    "context_sag.latency_ms": latency_ms,
                    "context_sag.context_count": len(prioritized_context),
                    "context_sag.risk_count": len(risk_register),
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
            raise ValueError("Either 'request' or 'request_path' must be provided to ContextSAG")
        payload = json.loads(Path(request_path).expanduser().read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Context brief JSON must contain an object root")
        return payload

    def _prioritize_inputs(self, inputs: List[ContextInput]) -> List[Dict[str, Any]]:
        sorted_inputs = sorted(
            inputs,
            key=lambda item: (IMPORTANCE_ORDER.get(item.importance, IMPORTANCE_ORDER["medium"]), item.name.lower()),
        )
        prioritized: List[Dict[str, Any]] = []
        for index, item in enumerate(sorted_inputs, start=1):
            inclusion = self._determine_inclusion(item)
            notes = self._build_notes(item, inclusion)
            prioritized.append(
                {
                    "name": item.name,
                    "sequence": index,
                    "type": item.type,
                    "importance": item.importance,
                    "summary": item.summary,
                    "inclusion": inclusion,
                    "recommended_actions": self._recommended_actions(item, inclusion),
                    "notes": notes,
                    "tags": item.tags,
                }
            )
        return prioritized

    def _determine_inclusion(self, item: ContextInput) -> str:
        if any(risk.lower() in {"deprecated", "exclude", "high risk"} for risk in item.risks):
            return "defer"
        if item.importance in {"critical", "high"}:
            return "retain"
        if item.importance == "medium":
            return "retain-trim"
        return "defer"

    def _build_notes(self, item: ContextInput, inclusion: str) -> List[str]:
        notes: List[str] = []
        if not item.source:
            notes.append("Missing provenance: provide source reference.")
        if not item.last_updated:
            notes.append("Last updated date not supplied.")
        if inclusion == "defer" and item.importance in {"medium", "low"}:
            notes.append("Consider summarising key points before inclusion.")
        if item.risks:
            notes.append("Risks: " + "; ".join(item.risks))
        return notes

    def _recommended_actions(self, item: ContextInput, inclusion: str) -> List[str]:
        actions: List[str] = []
        if inclusion == "retain":
            actions.append("Include full context block.")
        elif inclusion == "retain-trim":
            actions.append("Summarise key points and include truncated context.")
        else:
            actions.append("Archive for on-demand retrieval; exclude from primary prompt.")
        if item.tags:
            actions.append("Tag with: " + ", ".join(item.tags))
        if item.risks:
            actions.append("Mitigate risks before deployment.")
        return actions

    def _build_assembly_plan(
        self,
        brief: ContextBriefRequest,
        prioritized_context: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        plan: List[Dict[str, Any]] = []
        plan.append(
            {
                "sequence": 1,
                "step": "Normalise inputs",
                "description": "Convert context inputs into consistent schema with provenance and freshness metadata.",
            }
        )
        plan.append(
            {
                "sequence": 2,
                "step": "Assemble primary bundle",
                "description": "Combine 'retain' items first, followed by 'retain-trim' summaries respecting token budget.",
            }
        )
        if any(item["inclusion"] == "defer" for item in prioritized_context):
            plan.append(
                {
                    "sequence": 3,
                    "step": "Stage deferred material",
                    "description": "Store deferred items in retrieval index or sidecar memory with searchable tags.",
                }
            )
        plan.append(
            {
                "sequence": len(plan) + 1,
                "step": "Verify constraints and evaluation",
                "description": "Check constraints and evaluation checks are reflected in packaging instructions prior to rollout.",
            }
        )
        if brief.notes:
            plan.append(
                {
                    "sequence": len(plan) + 1,
                    "step": "Operator notes",
                    "description": brief.notes,
                }
            )
        return plan

    def _compile_risks(
        self,
        brief: ContextBriefRequest,
        prioritized_context: List[Dict[str, Any]],
    ) -> List[str]:
        risks: List[str] = []
        for item in prioritized_context:
            if "Missing provenance" in " ".join(item["notes"]):
                risks.append(f"{item['name']}: provenance not documented.")
            if "Last updated date not supplied." in item["notes"]:
                risks.append(f"{item['name']}: freshness unknown.")
            for note in item["notes"]:
                if note.startswith("Risks:"):
                    risks.append(f"{item['name']}: {note[len('Risks: '):]}")
        if not brief.constraints:
            risks.append("Constraints missing; risk of misaligned packaging.")
        return sorted(set(risks))

    def _collect_followups(
        self,
        brief: ContextBriefRequest,
        risk_register: List[str],
    ) -> List[str]:
        followups: List[str] = []
        if not brief.constraints:
            followups.append("Provide packaging or policy constraints to avoid misaligned context usage.")
        if not brief.evaluation_checks:
            followups.append("Define evaluation checks (e.g., regression prompts, human review cadence).")
        missing_provenance = [
            item.name for item in brief.context_inputs if not item.source or not item.last_updated
        ]
        if missing_provenance:
            followups.append(
                "Add provenance metadata (source/last_updated) for: " + ", ".join(sorted(set(missing_provenance)))
            )
        if len(risk_register) > 3:
            followups.append("Confirm mitigation owners for the identified risks.")
        return followups

    def _estimate_confidence(
        self,
        brief: ContextBriefRequest,
        risk_register: List[str],
        followups: List[str],
    ) -> float:
        confidence = 0.9
        if risk_register:
            confidence -= 0.15
        if followups:
            confidence -= 0.1
        if not brief.constraints:
            confidence -= 0.05
        if not brief.evaluation_checks:
            confidence -= 0.04
        return max(0.35, round(confidence, 2))

    def _write_output(self, path: Path, payload: Dict[str, Any]) -> None:
        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

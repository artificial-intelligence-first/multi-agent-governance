"""PromptSAG flow-runner sub-agent implementation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PromptComponent:
    """Represents a component of the resulting prompt."""

    role: str
    content: str

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "PromptComponent":
        if "role" not in payload or "content" not in payload:
            raise ValueError("Prompt components require 'role' and 'content' fields.")
        role = str(payload["role"]).strip()
        content = str(payload["content"]).strip()
        if not role or not content:
            raise ValueError("Prompt component fields cannot be empty.")
        return cls(role=role, content=content)


@dataclass
class PromptRequest:
    """Incoming request wrapper for PromptSAG."""

    id: str
    version: str
    objective: str
    constraints: List[str]
    references: List[str]
    context: str = ""
    target_models: List[str] = field(default_factory=list)
    evaluation: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Dict[str, Any]) -> "PromptRequest":
        required = {"id", "version", "objective"}
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Prompt request missing required fields: {', '.join(sorted(missing))}")
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
        models_raw = payload.get("target_models", [])
        if isinstance(models_raw, list):
            models = [str(item).strip() for item in models_raw if str(item).strip()]
        elif isinstance(models_raw, str):
            models = [segment.strip() for segment in models_raw.split(",") if segment.strip()]
        else:
            models = []
        evaluation_raw = payload.get("evaluation", [])
        if isinstance(evaluation_raw, list):
            evaluation = [str(item).strip() for item in evaluation_raw if str(item).strip()]
        elif isinstance(evaluation_raw, str):
            evaluation = [segment.strip() for segment in evaluation_raw.splitlines() if segment.strip()]
        else:
            evaluation = []

        return cls(
            id=str(payload["id"]),
            version=str(payload["version"]),
            objective=str(payload["objective"]).strip(),
            constraints=constraints,
            references=references,
            context=str(payload.get("context", "")).strip(),
            target_models=models,
            evaluation=evaluation,
        )


class PromptSAG:
    """Flow Runner compatible sub-agent that assembles prompt packages."""

    def __init__(self) -> None:
        pass

    async def run(
        self,
        request: Optional[Dict[str, Any]] = None,
        request_path: Optional[str] = None,
        output_path: Optional[str] = None,
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Entry point invoked by Flow Runner."""

        payload = self._load_request(request=request, request_path=request_path)
        prompt_request = PromptRequest.from_mapping(payload)

        start = time.perf_counter()
        components = self._generate_components(prompt_request)
        guardrails = self._collect_guardrails(prompt_request)
        evaluation_steps = self._gather_evaluation(prompt_request)
        followups = self._collect_followups(prompt_request, guardrails)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        review_flag = bool(followups)

        response: Dict[str, Any] = {
            "id": prompt_request.id,
            "version": prompt_request.version,
            "objective": prompt_request.objective,
            "context": prompt_request.context,
            "target_models": prompt_request.target_models,
            "prompt_components": [component.__dict__ for component in components],
            "guardrails": guardrails,
            "evaluation": evaluation_steps,
            "follow_up_questions": followups,
            "diagnostics": {
                "latency_ms": latency_ms,
                "review_flag": review_flag,
                "metrics": {
                    "prompt_sag.latency_ms": latency_ms,
                    "prompt_sag.prompt_count": len(components),
                    "prompt_sag.review_flag": int(review_flag),
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
            raise ValueError("Either 'request' or 'request_path' must be provided to PromptSAG")
        payload = json.loads(Path(request_path).expanduser().read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Prompt request JSON must contain an object root")
        return payload

    def _generate_components(self, req: PromptRequest) -> List[PromptComponent]:
        components: List[PromptComponent] = []
        system_lines: List[str] = [
            "You are an AI coding assistant operating within the Multi Agent Governance repository.",
            "Follow AGENTS.md policies: run tests, avoid destructive commands, respect file boundaries.",
        ]
        if req.constraints:
            system_lines.append("Constraints:")
            system_lines.extend(f"- {item}" for item in req.constraints)

        if req.references:
            system_lines.append("Reference material:")
            system_lines.extend(f"- {item}" for item in req.references)

        components.append(
            PromptComponent(
                role="system",
                content="\n".join(system_lines),
            )
        )

        user_lines: List[str] = [
            req.objective,
        ]
        if req.context:
            user_lines.append("")
            user_lines.append("Context:")
            user_lines.append(req.context)

        if req.target_models:
            user_lines.append("")
            user_lines.append("Target models: " + ", ".join(req.target_models))

        if req.evaluation:
            user_lines.append("")
            user_lines.append("Verification expectations:")
            user_lines.extend(f"- {item}" for item in req.evaluation)

        components.append(
            PromptComponent(
                role="user",
                content="\n".join(user_lines).strip(),
            )
        )
        return components

    def _collect_guardrails(self, req: PromptRequest) -> List[str]:
        guardrails = [
            "Run tests or linters specified in the prompt before completion.",
            "Do not modify files outside the listed targets.",
            "Explain reasoning briefly when deviating from suggested steps.",
        ]
        for item in req.constraints:
            if "no" in item.lower() or "avoid" in item.lower():
                guardrails.append(item)
        return guardrails

    def _gather_evaluation(self, req: PromptRequest) -> List[str]:
        if req.evaluation:
            return req.evaluation
        return ["Report tests/lint commands and their outcomes.", "Provide a summary of changes with file references."]

    def _collect_followups(self, req: PromptRequest, guardrails: List[str]) -> List[str]:
        questions: List[str] = []
        if not req.constraints:
            questions.append("Are there file or tooling restrictions that must be enforced?")
        if not req.evaluation:
            questions.append("Confirm required verification steps or CI commands.")
        if "Do not modify files" not in guardrails:
            questions.append("Clarify the list of allowed files for this prompt.")
        return questions

    def _write_output(self, path: Path, payload: Dict[str, Any]) -> None:
        path = path.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

#!/usr/bin/env python
"""Evaluate Skills matching quality against a curated dataset."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass
class Sample:
    sample_id: str
    query: str
    expected: set[str]
    expected_allow_exec: dict[str, bool]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute Skills matching metrics for the pilot dataset.")
    parser.add_argument(
        "--dataset",
        default="skills/pilot/phase1/dataset.jsonl",
        help="Path to JSONL dataset with fields id, query, expected_skills.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing skills/ and agents/ directories.",
    )
    parser.add_argument(
        "--model",
        default="BAAI/bge-large-en",
        help="SentenceTransformer model to use when --use-embeddings is enabled.",
    )
    parser.add_argument(
        "--use-embeddings",
        action="store_true",
        help="Enable local embedding model when available (falls back to keyword-only if not installed).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Maximum number of matches to consider (default: 3).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Match threshold passed to SkillManager (default: 0.75).",
    )
    parser.add_argument(
        "--skills-exec",
        action="store_true",
        help="Enable skills_exec feature flag when evaluating allow_exec behaviour (Phase 2 pilot).",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write detailed JSON results.",
    )
    return parser


def _load_dataset(path: Path) -> list[Sample]:
    samples: list[Sample] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        data = json.loads(line)
        sample_id = data.get("id")
        query = data.get("query")
        expected_names = data.get("expected_skills", [])
        names: set[str] = set()
        if isinstance(expected_names, (list, tuple, set)):
            for entry in expected_names:
                if isinstance(entry, str) and entry.strip():
                    names.add(entry.strip())
        allow_exec_mapping: dict[str, bool] = {}
        raw_allow_exec = data.get("expected_allow_exec", {})
        if isinstance(raw_allow_exec, dict):
            for key, value in raw_allow_exec.items():
                if not isinstance(key, str):
                    continue
                trimmed_key = key.strip()
                if not trimmed_key:
                    continue
                allow_exec_mapping[trimmed_key] = bool(value)
        if not sample_id or not query:
            continue
        samples.append(
            Sample(
                sample_id=sample_id,
                query=query,
                expected=names,
                expected_allow_exec=allow_exec_mapping,
            )
        )
    return samples


def _load_embedder(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError:
        return None
    try:
        transformer = SentenceTransformer(model_name)
    except Exception:  # pylint: disable=broad-except
        return None

    def _encode(texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return transformer.encode(list(texts), normalize_embeddings=True)

    return _encode


def _prepare_skill_manager(
    root: Path,
    *,
    threshold: float,
    top_k: int,
    use_embeddings: bool,
    model_name: str,
    skills_exec: bool,
):
    mcprouter_src = root / "src/mcprouter/src"
    if mcprouter_src.exists():
        sys.path.insert(0, str(mcprouter_src))
    from mcp_router.skills import SkillManager  # pylint: disable=import-error

    embedder = None
    if use_embeddings:
        embedder = _load_embedder(model_name)
        if embedder is None:
            print("[skills] sentence-transformers not available; falling back to keyword-only matching.", file=sys.stderr)

    feature_flags = {"skills_v1": True}
    if skills_exec:
        feature_flags["skills_exec"] = True
    manager = SkillManager(
        root=root,
        feature_flags=feature_flags,
        embedder=embedder,
        threshold=threshold,
        top_k=top_k,
    )
    manager.refresh_metadata()
    return manager


def _evaluate(samples: Iterable[Sample], manager, *, top_k: int) -> tuple[dict[str, object], list[dict[str, object]]]:
    total_tp = total_fp = total_fn = 0
    top1_correct = 0
    allow_exec_checks = 0
    allow_exec_mismatches = 0
    detailed: list[dict[str, object]] = []
    for sample in samples:
        matches = manager.prepare_payload(sample.query)[:top_k]
        predicted = [entry["name"] for entry in matches]
        predicted_allow_exec = {entry["name"]: bool(entry.get("allow_exec")) for entry in matches}
        expected = sample.expected
        tp = len(set(predicted) & expected)
        fp = len([name for name in predicted if name not in expected])
        fn = len([name for name in expected if name not in predicted])
        total_tp += tp
        total_fp += fp
        total_fn += fn
        if predicted:
            if predicted[0] in expected:
                top1_correct += 1
        sample_allow_exec_checks = 0
        sample_allow_exec_mismatches = {}
        for skill_name, expected_flag in sample.expected_allow_exec.items():
            if skill_name not in predicted_allow_exec:
                continue
            sample_allow_exec_checks += 1
            allow_exec_checks += 1
            actual_flag = predicted_allow_exec[skill_name]
            if actual_flag != expected_flag:
                allow_exec_mismatches += 1
                sample_allow_exec_mismatches[skill_name] = {
                    "expected": expected_flag,
                    "actual": actual_flag,
                }
        detailed.append(
            {
                "id": sample.sample_id,
                "query": sample.query,
                "expected": sorted(expected),
                "predicted": predicted,
                "threshold": manager._threshold,  # pylint: disable=protected-access
                "allow_exec": [entry["allow_exec"] for entry in matches],
                "expected_allow_exec": sample.expected_allow_exec,
                "allow_exec_mismatches": sample_allow_exec_mismatches,
                "allow_exec_checks": sample_allow_exec_checks,
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }
        )
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if precision + recall else 0.0
    coverage = top1_correct / len(detailed) if detailed else 0.0
    summary = {
        "samples": len(detailed),
        "top_k": top_k,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "top1_accuracy": round(coverage, 4),
        "matches_evaluated": sum(len(item["predicted"]) for item in detailed),
        "allow_exec_checks": allow_exec_checks,
        "allow_exec_mismatches": allow_exec_mismatches,
    }
    if allow_exec_checks:
        summary["allow_exec_accuracy"] = round(
            (allow_exec_checks - allow_exec_mismatches) / allow_exec_checks,
            4,
        )
    return summary, detailed


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"[skills] repository root not found: {root}", file=sys.stderr)
        return 2

    dataset_path = Path(args.dataset).expanduser()
    if not dataset_path.is_absolute():
        dataset_path = (root / dataset_path).resolve()
    if not dataset_path.exists():
        print(f"[skills] dataset not found: {dataset_path}", file=sys.stderr)
        return 2

    samples = _load_dataset(dataset_path)
    if not samples:
        print("[skills] dataset empty; nothing to evaluate.", file=sys.stderr)
        return 1

    manager = _prepare_skill_manager(
        root=root,
        threshold=args.threshold,
        top_k=args.top_k,
        use_embeddings=args.use_embeddings,
        model_name=args.model,
        skills_exec=args.skills_exec,
    )
    summary, detailed = _evaluate(samples, manager, top_k=args.top_k)
    available_metadata = {meta.name: meta for meta in manager.list_all()}
    missing_skills: set[str] = set()
    disabled_skills: set[str] = set()
    for sample in samples:
        for skill in sample.expected | set(sample.expected_allow_exec.keys()):
            if skill not in available_metadata:
                missing_skills.add(skill)
                continue
            if not available_metadata[skill].enabled:
                disabled_skills.add(skill)
    if missing_skills:
        print(
            "[skills] expected skills missing from registry: "
            + ", ".join(sorted(missing_skills)),
            file=sys.stderr,
        )
        summary["missing_skills"] = sorted(missing_skills)
    if disabled_skills:
        print(
            "[skills] expected skills are present but disabled: "
            + ", ".join(sorted(disabled_skills)),
            file=sys.stderr,
        )
        summary["disabled_skills"] = sorted(disabled_skills)
    print(json.dumps(summary, indent=2))
    if args.output:
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = (root / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_payload = {"summary": summary, "results": detailed}
        output_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")
        print(f"[skills] wrote detailed results to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

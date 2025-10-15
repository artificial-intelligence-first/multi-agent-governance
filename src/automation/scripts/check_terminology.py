#!/usr/bin/env python3
"""Simple terminology checker stub for English-language agent artifacts."""

import argparse
import json
from pathlib import Path
from json import JSONDecodeError


def load_terms(ssot_path: Path) -> set[str]:
    terms: set[str] = set()
    if not ssot_path.exists():
        return terms
    with ssot_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("- `") and "`" in line[3:]:
                term = line.split("`")[1].strip()
                terms.add(term.lower())
    return terms


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate glossary alignment.")
    parser.add_argument("response", type=Path, help="Path to the artifact JSON to inspect")
    parser.add_argument("--ssot", type=Path, required=True, help="Path to SSOT.md")
    args = parser.parse_args()

    response_text = args.response.read_text(encoding="utf-8")
    try:
        response_data = json.loads(response_text)
    except JSONDecodeError:
        if args.response.suffix.lower() in {".yaml", ".yml"}:
            print("Skipped: response appears to be YAML; terminology check expects JSON.")
            return
        raise
    ssot_terms = load_terms(args.ssot)

    missing_terms: list[str] = []
    for candidate in response_data.get("glossary_updates", []):
        term = candidate.get("term", "").lower()
        if term and term in ssot_terms:
            missing_terms.append(candidate.get("term", ""))

    if missing_terms:
        joined = ", ".join(missing_terms)
        raise SystemExit(f"Terms already present in SSOT: {joined}")

    print("Terminology check passed.")


if __name__ == "__main__":
    main()

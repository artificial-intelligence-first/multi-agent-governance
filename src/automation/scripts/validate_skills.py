"""Skills lint and validation checks.

Validates shared `/skills/` and agent-specific `skills/` directories:
- Frontmatter must contain only `name` and `description` with length limits.
- Body token budget must stay within the 5k guideline.
- Flags dangerous shell command patterns in instructions.
- Ensures registry and allowlist scaffolding are structurally sound.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
REGISTRY_PATH = SKILLS_DIR / "registry.json"
ALLOWLIST_PATH = SKILLS_DIR / "ALLOWLIST.txt"

DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bpip\s+install\b",
    r"\bnpm\s+install\b",
    r"\bgit\s+clone\b",
    r"\bbash\s+-c\b",
    r"\bpython\s+-c\b",
    r"\bnode\s+-e\b",
    r"\bInvoke-WebRequest\b",
    r"\bStart-Process\b",
]


class SkillValidationError(Exception):
    """Aggregated validation failures."""


def load_registry() -> Dict[str, dict]:
    if not REGISTRY_PATH.exists():
        raise SkillValidationError(f"Missing registry file: {REGISTRY_PATH}")
    try:
        data = json.loads(REGISTRY_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise SkillValidationError(f"Invalid JSON in {REGISTRY_PATH}: {exc}") from exc

    if not isinstance(data, dict) or "skills" not in data:
        raise SkillValidationError("registry.json must contain a top-level 'skills' list.")

    skills = data["skills"]
    if not isinstance(skills, list):
        raise SkillValidationError("'skills' entry in registry.json must be a list.")

    registry: Dict[str, dict] = {}
    required_fields = {"name", "path", "owner", "tags", "enabled", "allow_exec"}
    for entry in skills:
        if not isinstance(entry, dict):
            raise SkillValidationError("Each registry entry must be an object.")
        missing = required_fields - entry.keys()
        if missing:
            raise SkillValidationError(
                f"Registry entry for {entry.get('name', '<unknown>')} missing fields: {sorted(missing)}"
            )
        registry[entry["path"]] = entry
    return registry


def load_allowlist() -> Dict[str, Tuple[str, str]]:
    allowlist: Dict[str, Tuple[str, str]] = {}
    if not ALLOWLIST_PATH.exists():
        return allowlist
    for raw_line in ALLOWLIST_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3:
            raise SkillValidationError(
                f"Malformed allowlist entry (need path sha256 args-pattern): {raw_line}"
            )
        rel_path, sha256, args_pattern = parts[0], parts[1], " ".join(parts[2:])
        allowlist[rel_path] = (sha256, args_pattern)
    return allowlist


def iter_skill_files() -> Iterable[Path]:
    # Shared skills
    if SKILLS_DIR.exists():
        for skill_file in SKILLS_DIR.glob("**/SKILL.md"):
            if _should_skip(skill_file):
                continue
            yield skill_file
    # Agent-specific overrides
    if AGENTS_DIR.exists():
        for skill_file in AGENTS_DIR.glob("**/skills/**/SKILL.md"):
            if _should_skip(skill_file):
                continue
            yield skill_file


def _should_skip(path: Path) -> bool:
    return any(part.startswith("_") or part.startswith(".") for part in path.parts)


def parse_frontmatter(path: Path) -> Tuple[Dict[str, str], str]:
    text = path.read_text()
    if not text.startswith("---"):
        raise SkillValidationError(f"{path}: Missing YAML frontmatter.")
    sections = text.split("---", 2)
    if len(sections) < 3:
        raise SkillValidationError(f"{path}: Unterminated YAML frontmatter.")
    frontmatter_block = sections[1].strip("\n")
    body = sections[2]
    metadata: Dict[str, str] = {}
    lines = frontmatter_block.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not line.strip():
            idx += 1
            continue
        if ":" not in line:
            raise SkillValidationError(f"{path}: Invalid frontmatter line '{line}'.")
        key, remainder = line.split(":", 1)
        key = key.strip()
        value = remainder.strip()
        if value in {"|", ">"}:
            idx += 1
            collected: List[str] = []
            while idx < len(lines) and lines[idx].startswith("  "):
                collected.append(lines[idx][2:])
                idx += 1
            if value == ">":
                metadata[key] = " ".join(collected).strip()
            else:
                metadata[key] = "\n".join(collected).strip()
            continue
        metadata[key] = value
        idx += 1
    allowed_keys = {"name", "description"}
    extra = set(metadata) - allowed_keys
    if extra:
        raise SkillValidationError(f"{path}: Unsupported frontmatter keys {sorted(extra)}.")
    missing = allowed_keys - set(metadata)
    if missing:
        raise SkillValidationError(f"{path}: Missing required frontmatter keys {sorted(missing)}.")
    return metadata, body


def check_frontmatter(path: Path, metadata: Dict[str, str]) -> List[str]:
    errors: List[str] = []
    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if "\n" in name or not name:
        errors.append(f"{path}: 'name' must be a single line.")
    if len(name) > 64:
        errors.append(f"{path}: 'name' exceeds 64 characters ({len(name)}).")
    if len(description) > 1024:
        errors.append(f"{path}: 'description' exceeds 1024 characters ({len(description)}).")
    if not description.strip():
        errors.append(f"{path}: 'description' must not be empty.")
    return errors


def check_body(path: Path, body: str) -> List[str]:
    errors: List[str] = []
    tokens = body.split()
    if len(tokens) > 5000:
        errors.append(f"{path}: body contains {len(tokens)} tokens (>5000 guideline).")
    text_lower = body.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text_lower):
            errors.append(f"{path}: found dangerous command pattern '{pattern}'.")
    errors.extend(_check_links(path, body))
    return errors


def _check_links(path: Path, body: str) -> List[str]:
    errors: List[str] = []
    pattern = re.compile(r"\[(?:[^\]]+)\]\(([^)]+)\)")
    directory = path.parent
    for match in pattern.finditer(body):
        target = match.group(1).strip()
        if not target or target.startswith("#"):
            continue
        if "://" in target or target.startswith("mailto:"):
            continue
        if target.startswith("`") and target.endswith("`"):
            continue
        candidate_path = target
        anchor = ""
        if "#" in candidate_path:
            candidate_path, anchor = candidate_path.split("#", 1)
        if not candidate_path:
            continue
        if candidate_path.startswith("/"):
            resolved = ROOT / candidate_path.lstrip("/")
        else:
            resolved = (directory / candidate_path).resolve()
        if not resolved.exists():
            display = target if not anchor else f"{candidate_path}#{anchor}"
            errors.append(f"{path}: broken link target '{display}'")
    return errors


def check_scripts(path: Path, allowlist: Dict[str, Tuple[str, str]]) -> List[str]:
    errors: List[str] = []
    scripts_dir = path.parent / "scripts"
    if not scripts_dir.exists():
        return errors
    for script in scripts_dir.glob("*"):
        if script.is_dir():
            continue
        rel = script.relative_to(ROOT).as_posix()
        if rel not in allowlist:
            errors.append(
                f"{rel}: script missing from skills/ALLOWLIST.txt (register path, sha256, args-pattern)."
            )
    return errors


def main() -> int:
    errors: List[str] = []
    registry = {}
    allowlist = {}
    try:
        registry = load_registry()
        allowlist = load_allowlist()
    except SkillValidationError as exc:
        errors.append(str(exc))

    seen_paths: List[str] = []
    for skill_file in iter_skill_files():
        # Normalise path
        rel_path = skill_file.relative_to(ROOT).as_posix()
        seen_paths.append(rel_path)
        try:
            metadata, body = parse_frontmatter(skill_file)
            errors.extend(check_frontmatter(skill_file, metadata))
            errors.extend(check_body(skill_file, body))
            errors.extend(check_scripts(skill_file, allowlist))
        except SkillValidationError as exc:
            errors.append(str(exc))

    # Registry cross-check (only for entries that point to real files)
    for rel_path, entry in registry.items():
        resolved = ROOT / rel_path
        if not resolved.exists():
            errors.append(f"Registry entry path missing: {rel_path}")

    if errors:
        for err in errors:
            print(f"[skills] {err}", file=sys.stderr)
        return 1
    print("Skills validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

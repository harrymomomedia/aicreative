#!/usr/bin/env python3
"""Verify that always-loaded instructions and Claude project memory stay lean."""

from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
HOME = Path.home()
MEMORY = HOME / ".claude/projects/-Users-harry-aicreative/memory"

FILE_BUDGETS = {
    REPO / "AGENTS.md": (60, 4_096),
    REPO / "CLAUDE.md": (120, 8_192),
    HOME / ".codex/AGENTS.md": (30, 2_048),
    MEMORY / "MEMORY.md": (40, 4_096),
}
CAMPAIGN_BUDGET = (60, 6_144)
MEMORY_FILE_LIMIT = 12
MEMORY_BYTE_LIMIT = 32_768

STALE_PATTERNS = {
    "obsolete Poyo Veo default": re.compile(r"Veo 3\.1 Fast\s*=\s*Poyo default", re.I),
    "recursive generated anchors": re.compile(r"clip 1\s*\(or early clips\)", re.I),
    "obsolete planning override": re.compile(r"skip writing-plans", re.I),
    "frozen-frame rescue": re.compile(r"frozen-plate rescue", re.I),
    "obsolete video-link formatting": re.compile(r"backticked inline paths", re.I),
    "obsolete OpenAI image fallback": re.compile(r"OpenAI-direct fallback", re.I),
}


def metrics(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    return len(data.splitlines()), len(data)


def check_budget(
    path: Path,
    limits: tuple[int, int],
    errors: list[str],
) -> None:
    if not path.exists():
        errors.append(f"missing required instruction file: {path}")
        return
    lines, size = metrics(path)
    max_lines, max_size = limits
    if lines > max_lines or size > max_size:
        errors.append(
            f"over budget: {path} is {lines} lines/{size} bytes "
            f"(limit {max_lines}/{max_size})"
        )


def main() -> int:
    errors: list[str] = []

    for path, limits in FILE_BUDGETS.items():
        check_budget(path, limits, errors)

    memory_files = sorted(MEMORY.glob("*.md")) if MEMORY.exists() else []
    feedback_files = sorted(MEMORY.glob("feedback_*.md")) if MEMORY.exists() else []
    if feedback_files:
        errors.append(
            "standalone feedback memories found: "
            + ", ".join(path.name for path in feedback_files)
        )
    if len(memory_files) > MEMORY_FILE_LIMIT:
        errors.append(
            f"active memory has {len(memory_files)} files "
            f"(limit {MEMORY_FILE_LIMIT})"
        )

    memory_bytes = sum(path.stat().st_size for path in memory_files)
    if memory_bytes > MEMORY_BYTE_LIMIT:
        errors.append(
            f"active memory is {memory_bytes} bytes (limit {MEMORY_BYTE_LIMIT})"
        )

    for path in memory_files:
        if path.name != "MEMORY.md":
            check_budget(path, CAMPAIGN_BUDGET, errors)

    scanned = [
        REPO / "AGENTS.md",
        REPO / "CLAUDE.md",
        HOME / ".codex/AGENTS.md",
        *memory_files,
    ]
    for path in scanned:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in STALE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} found in active instructions: {path}")

    mirrored = 0
    for repo_skill in sorted((REPO / "skills").glob("*/SKILL.md")):
        linked_agent_skill = REPO / ".agents/skills" / repo_skill.parent.name / "SKILL.md"
        if linked_agent_skill.exists():
            continue
        live_skill = HOME / ".codex/skills" / repo_skill.parent.name / "SKILL.md"
        if not live_skill.exists():
            continue
        mirrored += 1
        if repo_skill.read_bytes() != live_skill.read_bytes():
            errors.append(f"live skill mirror differs: {repo_skill.parent.name}")

    print(
        f"root={metrics(REPO / 'AGENTS.md')[1] + metrics(REPO / 'CLAUDE.md')[1]} bytes "
        f"memory={len(memory_files)} files/{memory_bytes} bytes "
        f"mirrors={mirrored}"
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PASS: instruction and memory budgets are clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

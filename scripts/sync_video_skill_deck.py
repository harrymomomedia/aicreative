#!/usr/bin/env python3
"""Validate the canonical SkillDeck registry and generate its readable index."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
REFERENCES = SKILLS_ROOT / "video-skill-deck" / "references"
REGISTRY_PATH = REFERENCES / "skill-map.json"
MARKDOWN_PATH = REFERENCES / "skill-map.md"

CALL_NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]{1,31}$")
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def skill_name_from_frontmatter(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def display_name_from_agent(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\s*display_name:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip("\"'") if match else None


def repository_skill_ids() -> set[str]:
    return {
        path.name
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    }


def validate_registry(registry: dict) -> list[str]:
    errors: list[str] = []
    skills = registry.get("skills")
    recipes = registry.get("recipes")
    if registry.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(skills, list) or not isinstance(recipes, list):
        return errors + ["skills and recipes must be lists"]

    actual_ids = repository_skill_ids()
    registered_ids: list[str] = []
    calls: dict[str, str] = {}

    for index, entry in enumerate(skills):
        label = f"skills[{index}]"
        call_name = entry.get("call_name", "")
        skill_id = entry.get("skill_id", "")
        group = entry.get("group", "")
        purpose = entry.get("purpose", "")
        if not CALL_NAME_RE.fullmatch(call_name):
            errors.append(f"{label} has invalid call_name: {call_name!r}")
        if not SKILL_ID_RE.fullmatch(skill_id):
            errors.append(f"{label} has invalid skill_id: {skill_id!r}")
        if not group or not purpose:
            errors.append(f"{label} requires group and purpose")
        normalized = call_name.casefold()
        if normalized in calls:
            errors.append(
                f"duplicate call name {call_name!r}: {calls[normalized]} and {skill_id}"
            )
        calls[normalized] = skill_id
        registered_ids.append(skill_id)

        skill_dir = SKILLS_ROOT / skill_id
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            frontmatter_name = skill_name_from_frontmatter(skill_file)
            if frontmatter_name != skill_id:
                errors.append(
                    f"{skill_id} frontmatter name is {frontmatter_name!r}"
                )
        agent_file = skill_dir / "agents" / "openai.yaml"
        if agent_file.exists() and not skill_dir.is_symlink():
            display_name = display_name_from_agent(agent_file)
            if display_name != call_name:
                errors.append(
                    f"{skill_id} display_name is {display_name!r}; "
                    f"expected call name {call_name!r}"
                )

    if len(registered_ids) != len(set(registered_ids)):
        errors.append("a stable skill ID is registered more than once")

    registered_set = set(registered_ids)
    for missing in sorted(actual_ids - registered_set):
        errors.append(f"repository skill is missing from SkillDeck: {missing}")
    for stale in sorted(registered_set - actual_ids):
        errors.append(f"SkillDeck points to a missing repository skill: {stale}")

    for index, entry in enumerate(recipes):
        label = f"recipes[{index}]"
        call_name = entry.get("call_name", "")
        parent = entry.get("parent_skill", "")
        purpose = entry.get("purpose", "")
        if not CALL_NAME_RE.fullmatch(call_name):
            errors.append(f"{label} has invalid call_name: {call_name!r}")
        normalized = call_name.casefold()
        if normalized in calls:
            errors.append(
                f"duplicate call name {call_name!r}: {calls[normalized]} and recipe"
            )
        calls[normalized] = f"recipe:{parent}"
        if parent not in registered_set:
            errors.append(f"{label} has unknown parent skill: {parent!r}")
        if not purpose:
            errors.append(f"{label} requires purpose")

    return errors


def render_markdown(registry: dict) -> str:
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for entry in registry["skills"]:
        groups.setdefault(entry["group"], []).append(entry)

    lines = [
        "# Video SkillDeck",
        "",
        "Generated from `skill-map.json` by `scripts/sync_video_skill_deck.py`.",
        "Call names are conversational aliases; stable skill IDs remain unchanged.",
        "",
    ]
    for group, entries in groups.items():
        lines.extend(
            [
                f"## {group}",
                "",
                "| Call name | Stable skill ID | Use it for |",
                "|---|---|---|",
            ]
        )
        for entry in entries:
            lines.append(
                f"| **{entry['call_name']}** | `{entry['skill_id']}` | "
                f"{entry['purpose']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Named Recipes",
            "",
            "| Call name | Parent skill | Use it for |",
            "|---|---|---|",
        ]
    )
    for entry in registry["recipes"]:
        lines.append(
            f"| **{entry['call_name']}** | `{entry['parent_skill']}` | "
            f"{entry['purpose']} |"
        )

    lines.extend(
        [
            "",
            "## Invocation",
            "",
            "- `Use StreetPunch and Redwood for this edit.`",
            "- `Open SkillDeck and choose the best interview route.`",
            "- `Run ForgeSync on the lessons from this batch.`",
            "",
        ]
    )
    return "\n".join(lines)


def searchable_entries(registry: dict) -> list[dict]:
    entries = [dict(entry, kind="skill") for entry in registry["skills"]]
    entries.extend(
        {
            "call_name": entry["call_name"],
            "skill_id": entry["parent_skill"],
            "purpose": entry["purpose"],
            "kind": "recipe",
        }
        for entry in registry["recipes"]
    )
    return entries


def find_entries(registry: dict, term: str) -> int:
    query = term.casefold()
    matches = [
        entry
        for entry in searchable_entries(registry)
        if query
        in " ".join(
            (
                entry["call_name"],
                entry["skill_id"],
                entry["purpose"],
                entry["kind"],
            )
        ).casefold()
    ]
    if not matches:
        print(f"no SkillDeck match for: {term}")
        return 1
    for entry in matches:
        print(
            f"{entry['call_name']}\t{entry['kind']}\t"
            f"{entry['skill_id']}\t{entry['purpose']}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="regenerate skill-map.md")
    mode.add_argument("--check", action="store_true", help="verify skill-map.md is current")
    mode.add_argument("--find", metavar="TERM", help="search call names, IDs, and purposes")
    args = parser.parse_args()

    registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.find:
        return find_entries(registry, args.find)

    expected = render_markdown(registry)
    if args.write:
        MARKDOWN_PATH.write_text(expected, encoding="utf-8")
        action = "wrote"
    else:
        current = (
            MARKDOWN_PATH.read_text(encoding="utf-8")
            if MARKDOWN_PATH.exists()
            else ""
        )
        if current != expected:
            print(
                f"ERROR: {MARKDOWN_PATH.relative_to(ROOT)} is stale; run with --write",
                file=sys.stderr,
            )
            return 1
        action = "checked"

    print(
        f"{action} SkillDeck: {len(registry['skills'])} skills, "
        f"{len(registry['recipes'])} recipes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

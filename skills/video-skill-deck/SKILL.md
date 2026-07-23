---
name: video-skill-deck
description: Recall, select, and register video-production skills and recipes by memorable call names while preserving stable skill IDs. Use when the user says SkillDeck, asks what a video skill is called, asks to list available video workflows, names a registered call such as VideoPilot, CutSmith, StreetPunch, or Redwood, wants an end-to-end skill route, or creates a reusable video technique that needs a unique name.
---

# SkillDeck

SkillDeck is the naming and discovery layer for the video system. Human-facing call names stay
memorable; stable kebab-case skill IDs remain unchanged so links, scripts, and routing do not break.

## Resolve A Call

1. Read [skill-map.md](references/skill-map.md), or search it with
   `.venv/bin/python scripts/sync_video_skill_deck.py --find <term>`.
2. Resolve an exact call name first, then recipe name, stable ID, purpose, or related term.
3. Load the stable skill ID and only the specialists needed for the task.
4. In the first working update, tell the user the selected route once:
   `Using StreetPunch through ShotCraft for landscape-to-vertical speaker cuts.`
5. Continue in normal language. Do not repeat the route in every update.

If a name is ambiguous, present the two or three closest matches with one-line purposes. Never
silently reinterpret a known call name.

## Build A Route

- Start with `VideoPilot` for end-to-end production.
- Add the smallest set of generation, format, post, caption, domain, or delivery calls needed.
- A recipe call such as `DuoLock` loads its parent skill and the recipe-specific reference.
- Treat call names as user vocabulary, not replacement directory names.

## Register A New Name

1. Search the deck and routed skills for an existing capability.
2. Use a recipe when the behavior is a variation of an existing workflow. Create a skill only
   when it has an independent trigger and substantial reusable procedure.
3. Choose a short, pronounceable, globally unique PascalCase call name that hints at the result.
4. Keep the stable skill ID lowercase kebab-case.
5. Update `references/skill-map.json`, then run:
   `.venv/bin/python scripts/sync_video_skill_deck.py --write`.
6. Validate the deck and the changed skill. When GitHub persistence was requested, finish with
   `ForgeSync`.
7. Tell the user the new call name, literal meaning, parent or stable ID, and when to invoke it.

Do not rename stable skill folders merely to improve recall. Rename a call name only when the old
name is misleading, and preserve the old term as a searchable synonym during the transition.

## References

- [skill-map.md](references/skill-map.md): generated human-readable deck.
- [skill-map.json](references/skill-map.json): canonical registry; edit this file, not the
  generated table.

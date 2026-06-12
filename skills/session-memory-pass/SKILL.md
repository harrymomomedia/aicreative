---
name: session-memory-pass
description: Extract and save durable learnings after a completed work session so future sessions avoid repeating mistakes. Use when the user asks to update learnings, save memory, create rules, make a skill, remember what happened, prevent future mistakes, write a rulebook, or commit/push session lessons.
---

# Session Memory Pass

Use this skill at the end of a meaningful work session. The goal is not to save everything; it is to preserve the lessons most likely to prevent repeated mistakes.

## What To Extract

Use judgment. Look for:

- User preferences, corrections, rejected directions, and approved patterns.
- Exact wording rules, phrases to use, and phrases to avoid.
- Prompting lessons: structures that worked, words that failed, model mishearings, moderation triggers, and ways to rewrite around them.
- Production workflow lessons: provider/model routing, batching strategy, QA gates, stitching, captions, disclaimers, final deliverables, and asset paths.
- Tooling or script lessons: new scripts, changed defaults, fragile commands, and known failure modes.
- Campaign-specific facts versus global rules.
- Anything that cost time, money, quality, or caused a user rejection.

## Where To Save

Choose the smallest durable home that will make the lesson useful later:

- Campaign-specific notes: `inventory/<campaign>_learnings.md` or a learnings file in the relevant `outputs/<campaign>/` folder.
- Project-wide behavior: `CLAUDE.md`.
- Codex project/default behavior: repo `AGENTS.md` and, when needed, `~/.codex/AGENTS.md`.
- Reusable workflow: a skill under `~/.codex/skills/<skill-name>/SKILL.md`, mirrored into repo `skills/<skill-name>/SKILL.md`.
- Tool/style inventory: the relevant inventory file, README, script docstring, or style registry.

If a live skill is updated, mirror the same change into the repo `skills/` copy before committing.
If Codex's live `~/.codex/AGENTS.md` is updated for a project-specific rule, mirror the project version into repo `AGENTS.md` too so the rulebook is versioned.

## Memory Quality

- Write explicit "do not repeat" notes for rejected outputs and painful mistakes.
- Keep broad rules separate from one-off campaign details.
- Prefer practical rules over long narrative.
- Include the reason when it matters: "prevents flashing captions on sensitive legal ads," "prevents Veo mishearing form as forum."
- Do not turn every detail into a global rule. Promote only lessons likely to recur.

## Git Hygiene

- Inspect `git status` before staging.
- Re-check branch + status again immediately before pushing. In this repo, concurrent Codex sessions can checkout branches, commit the same dirty files, or push while a memory pass is in progress.
- If expected dirty files disappear or the branch changes mid-task, stop and inspect `git status`, recent `git log`, `git reflog`, and the relevant branch diff before staging or pushing. Another session may already have committed the work.
- Run a secret scan over exactly what will be committed or pushed before publishing, especially when API tokens or ad-platform launch configs were discussed in the session.
- Commit only memory, skill, rulebook, or learning-file changes.
- Do not stage unrelated dirty files, generated outputs, secrets, or the user's unrelated work.
- If a file has unrelated existing edits, stage only the memory hunk.
- Push after a successful commit when the user asked for GitHub persistence.

## Final Report

Tell the user:

- What was saved.
- Where it was saved.
- What future mistake each major note prevents.
- Commit hash and pushed branch, if committed.
- Which unrelated dirty files were left untouched.

# ForgeSync Publish Checklist

Use this checklist after `SkillForge` has classified the evidence.

## Content

- Search the target skill, references, scripts, `CLAUDE.md`, `AGENTS.md`, `inventory/`, and active
  campaign memory before adding a rule.
- Confirm each lesson has a trigger, decision or procedure, rejection gate, and useful reason.
- Remove campaign nouns and IDs only when the lesson still makes sense across projects.
- If creating a skill or recipe, register a unique call name through `SkillDeck`.
- Keep exact legal text in its domain skill or campaign configuration.

## Validation

Run the checks that apply:

```bash
.venv/bin/python /Users/harry/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-id>
.venv/bin/python scripts/sync_video_skill_deck.py --write
.venv/bin/python scripts/sync_video_skill_deck.py --check
.venv/bin/python scripts/catalog_video_workflows.py
.venv/bin/python scripts/audit_instruction_bloat.py
git diff --check
```

Also run syntax checks and media QA for any changed executable or production workflow. Mirror each
changed repo-owned skill to `~/.codex/skills/<skill-id>/`, then rerun the mirror audit.

## Git

1. Recheck `git status --short --branch` and confirm the branch did not change.
2. Stage explicit intended paths, not the entire worktree.
3. Inspect `git diff --cached --stat`, `git diff --cached`, and `git diff --cached --check`.
4. Run `gitleaks git --staged --redact --no-banner .`.
5. Commit with a message describing the reusable capability, not the campaign incident.
6. Fetch the upstream. Rebase the clean committed branch if the remote advanced.
7. Push the current branch.
8. Fetch once more and verify local `HEAD`, the configured upstream, and the remote ref match.

If expected changes disappear, the branch changes, or unrelated staged files appear, inspect
status, recent log, reflog, and the relevant diff before continuing. Another session may have
committed or changed the same worktree.

## Final Report

Report the saved lesson, durable home, call names, validators run, commit, branch, remote
verification, and unrelated files deliberately left untouched.

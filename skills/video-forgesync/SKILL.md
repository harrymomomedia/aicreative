---
name: video-forgesync
description: Promote new video-production learnings into the correct general skill, named recipe, reusable script, provider reference, campaign record, or project instruction; then mirror, validate, commit, rebase, push, and verify the update on GitHub. Call name ForgeSync. Use when the user says ForgeSync, update all new learnings to the repo, save video learnings and commit/push, learning update to GitHub, make sure we never repeat this, or asks for a complete post-production learning pass with repository synchronization.
---

# ForgeSync

ForgeSync turns the current production's evidence into a clean, published capability update. It
invokes `SkillForge` for classification and `SkillDeck` for naming, then completes Git persistence.

## End-To-End Pass

1. **Snapshot**
   - Recheck branch, worktree, upstream, and recent commits.
   - Identify evidence created in this session: outputs, user verdicts, rerolls, QA, and fixes.
   - Separate the intended learning changes from concurrent or unrelated work.

2. **Forge**
   - Run `video-skillforge`.
   - Search before writing and promote only lessons that pass its promotion gate.
   - Preserve useful alternatives as named recipes instead of replacing one valid flow with
     another.

3. **Name**
   - Run `SkillDeck` when a new recipe or independently triggered skill is warranted.
   - Prefer an existing call name. If a new one is necessary, register it, validate uniqueness,
     and report it to the user.

4. **Place**
   - Put reusable craft in the narrowest applicable skill or reusable script.
   - Put project-wide routing defaults in `CLAUDE.md` or `AGENTS.md` only when they must load every
     session.
   - Put campaign copy, people, assets, IDs, compliance, and launch state in the existing campaign
     record.
   - Replace superseded guidance; do not append near-duplicates.

5. **Synchronize and validate**
   - Update the versioned repo copy, mirror changed repo-owned skills to the live Codex directory,
     regenerate SkillDeck and repository catalogs, and run the relevant validators.
   - Run instruction-budget, syntax, media, and staged-secret checks appropriate to the change.
   - Do not publish a lesson that contradicts a locked provider, legal, identity, native-speed,
     approval, or framewise-QA rule.

6. **Publish**
   - Stage only intended paths and inspect the exact staged patch.
   - Commit with a descriptive learning-system message.
   - Fetch and rebase onto the current upstream when needed, then push.
   - Verify local `HEAD`, upstream, and remote branch resolve to the same commit.

7. **Report**
   - State what was learned, where it lives, the call names affected or created, validation results,
     commit hash, pushed branch, and any unrelated files left untouched.

Complete the full pass in the current session unless Git conflicts, missing evidence, failed
validation, or permissions genuinely block publication. Never claim a push or mirror succeeded
without verifying it.

## Guardrails

- Do not create one skill, rule, memory file, or commit per clip.
- Do not stage generated media, secrets, or unrelated concurrent edits.
- Do not rewrite history or discard another session's work.
- Do not use a new call name until SkillDeck accepts it as unique.
- Do not turn campaign-specific facts into general technique by merely deleting the campaign name.

Read [publish-checklist.md](references/publish-checklist.md) before staging or publishing.

---
name: video-skillforge
description: Promote evidence from generated videos, edits, user corrections, rejected assets, and successful fixes into a durable video-production knowledge system. Use after each meaningful video output, reroll, approval, rejection, completed batch, or final delivery when the user asks to save learnings, update the repo, prevent repeated mistakes, generalize a campaign technique, create a memorable format recipe, or improve future video agents.
---

# Video SkillForge

Turn production evidence into reusable capability without filling root instructions or memory with
one-off notes. Capture every output verdict, but promote only durable lessons.

## When To Run

- Record a brief evidence card after every generated clip or rendered revision.
- Run the full promotion pass immediately after a costly failure, explicit user correction, or
  validated new workflow.
- Run it again at batch completion or final delivery to consolidate related observations.

Do not commit one rule per clip. Keep provisional evidence in the job's output manifest, then
promote proven lessons at meaningful checkpoints.

## Forge Loop

1. **Capture evidence**
   - Record input, provider/tool, result, user verdict, defect or advantage, attempted repair, and
     validation evidence.
   - Separate observation from inference. One odd render is evidence, not yet a universal rule.

2. **Search before writing**
   - Search routed skills, their references, reusable scripts, `inventory/`, campaign configuration,
     and active campaign memory.
   - Update an existing home when the lesson strengthens or corrects it.

3. **Classify the lesson**

| Lesson | Durable home |
|---|---|
| Cross-format generation invariant | `ai-video-generation` |
| Cross-format editing, audio, caption, or QA technique | `video-post-production` |
| Distinct repeatable visual grammar with its own trigger | A format skill or named recipe |
| Repeated deterministic transformation | Reusable script in `scripts/` |
| Provider behavior or cost constraint | Provider reference under `ai-video-generation` |
| Ad strategy or regulated domain behavior | Domain skill such as `admachin-video-ads` |
| Campaign copy, people, IDs, assets, compliance, or launch state | `inventory/`, campaign config, or concise campaign memory |
| Superseded narrative | Archive outside auto-loaded memory |

4. **Generalize**
   - Remove campaign names, people, products, copy, IDs, and legal text.
   - State the trigger, choice, procedure, rejection gate, and reason.
   - Preserve meaningful alternatives. If several methods work under different conditions, add a
     selection table and named recipes instead of replacing them with one rigid flow.

5. **Name for recall**
   - Give reusable format recipes a short memorable name plus a literal descriptor.
   - Prefer names such as `DuoLock: true two-person generated shot` over opaque codes such as `v4b`.
   - Create a new skill only when the workflow has an independent trigger and enough substance to
     load separately. Otherwise add a recipe or reference to the nearest existing skill.

6. **Operationalize**
   - Add or improve a script when the same deterministic code would otherwise be rewritten.
   - Link the skill to that script and specify inputs, outputs, and QA.
   - Keep campaign scripts as examples, not as the canonical implementation.

7. **Validate and publish**
   - Validate changed skills.
   - Mirror repo-owned skills to their live Codex copies.
   - Regenerate the workflow and skill catalogs.
   - Run `scripts/audit_instruction_bloat.py`, syntax checks, relevant media QA, and a secret scan.
   - Commit only the intended learning-system changes unless the user requested a full sync.

## Promotion Gate

Promote when at least one is true:

- The user explicitly locked the behavior.
- The same failure or advantage appeared in more than one asset or workflow.
- A controlled before/after check verified the fix.
- The lesson prevents material credit waste, identity drift, legal risk, or delivery failure.

Keep it campaign-specific when removing campaign nouns changes its meaning.

## References

Read [promotion-examples.md](references/promotion-examples.md) for evidence cards, classification
examples, recipe naming, and the distinction between a rule, recipe, script, and campaign note.

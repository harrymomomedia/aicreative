# Promotion Examples

## Evidence Card

```yaml
asset: clip-or-final-path
stage: generation | assembly | captions | delivery
attempt: provider, model, script, or edit route
observed: what actually happened
verdict: accepted | rejected | rerolled | superseded
fix: what changed
validation: transcript, frames, measurements, or user approval
scope: universal | format | provider | domain | campaign
```

Store provisional cards with the job output. Promote the distilled result, not the full incident
story.

## Classification Examples

### Universal Rule

Observation: several image-to-video clips changed the approved person's face after prompts repeated
her appearance.

Promotion: update `ai-video-generation` so the anchor is the visual truth and prompts describe
action, voice, dialogue, camera behavior, and intentional change only.

Do not keep the person's ethnicity, diagnosis, room, or campaign copy in the reusable rule.

### Post-Production Rule

Observation: a one-frame host flash appeared between adjacent B-roll cuts.

Promotion: update `video-post-production` with frame-quantized boundaries and transition QA. Add a
deterministic checker when possible.

### Named Format Recipes

Observation: a real two-shot looks natural but multi-character generation sometimes causes
cross-talk or identity drift. A shared wide master cropped into solo angles is more reliable but
less physically interactive.

Promotion: preserve both under `interview-shotcraft`:

- `DuoLock`: true two-person generated shot.
- `WideSplit`: one approved landscape composition split into matched solo anchors.

The selection condition is the lesson. Neither recipe replaces the other.

### Reusable Script

Observation: several street interviews require the same frame-accurate horizontal-to-vertical
active-speaker crop.

Promotion: add a parameterized post-processing script and reference it from the format skill.
Campaign-specific crop coordinates stay in job plans, not in the script.

### Campaign Note

Observation: one medical campaign requires an exact diagnosis phrase and qualification window.

Promotion: keep exact wording and criteria in that campaign's configuration or inventory. Do not
put them in general generation or post-production skills.

## New Skill Test

Create a separate skill only when all are true:

1. It has a clear phrase or task that should trigger it.
2. It owns a repeatable end-to-end decision or production grammar.
3. Loading it separately avoids burdening unrelated work.
4. It is not just one provider call, one campaign, or one correction.

Otherwise add a named recipe, reference, or reusable script to an existing skill.

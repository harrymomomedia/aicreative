# Cost And Transcript QA

## Efficient Generation

- Generate the highest-risk clip first.
- Preserve every accepted clip.
- Reroll only the failed unit.
- Generate sequentially when guardrail failures consume credits or submission throttles are strict.
- Persist prompt, model, provider, anchor, task ID, and intended dialogue beside each output.
- A killed local process does not necessarily cancel a server-side job; resume polling before resubmitting.

## Transcript QA

Use ElevenLabs Scribe with biased keywords for names and medical/product terms.

Canonicalize both intended and heard text before rejection:

- punctuation and case
- digits versus words
- hyphenation
- harmless contractions
- known homophones such as `Depo`/`Depot`

Then inspect the kept word span for:

- missing or substituted qualifying words
- inserted filler or reactions
- stutters
- repeated phrases
- trailing improvisation
- wrong names or diagnoses

Leading/trailing extras can be trimmed by word timestamps at native speed. This includes a single
transition word appended after the completed intended sentence: end on an exact frame after the
intended final word only when that word is fully spoken and the cut does not clip its final
phoneme. Mid-claim insertions should usually be rerolled; remove them only when meaning remains
exact and an approved visual covers the native-speed cut.

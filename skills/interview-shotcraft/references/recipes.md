# Interview Shotcraft Recipes

## PodSolo

One visible host or guest carries the spoken track. Use `podcast-video` for register, gaze, mic,
reactions, proof cuts, and pacing.

Choose it for a monologue, testimony, explainer, or audience notice. Keep the voice conversational
and use proof media when a static host would overstay the beat.

## DuoLock

Generate a real two-shot with both people visible.

Use when:

- physical proximity and shared reactions are central
- dialogue is short
- a model has passed a pilot with these anchors
- the silent person's behavior can remain simple

Method:

1. Approve one two-person anchor.
2. Generate one speaker per clip.
3. Tell the silent listener only to listen, blink, and keep the mouth naturally closed.
4. Keep gestures restrained and avoid object handoffs.
5. Check each person's face and mouth throughout, not only the active speaker.

If cross-talk, shared voice timbre, face drift, or mic mutation repeats, switch architecture rather
than making the prompt progressively longer.

## WideSplit

Create one high-resolution landscape composition containing both people in their correct positions,
then derive matching portrait anchors for each side.

Use when:

- both people must clearly inhabit the same place
- generated two-shots fail speaker attribution
- the final can use conventional question/reaction cutaways

Method:

1. Approve the landscape master with enough side space around both faces.
2. Crop subject-specific 9:16 anchors while preserving source pixels and outward-looking eyelines.
3. Keep shared landmarks, color, lens height, and light in both crops.
4. Animate each crop as a single-person clip.
5. Assemble question, answer, and reaction angles; optionally return to the original wide master as
   a short orientation shot.

Use a 4K or similarly detailed master when delivering 1080x1920. A 1920x1080 master provides only
about 608 source pixels across a full-height 9:16 crop and may look soft after enlargement.

## StreetPunch

Start from one accepted landscape interview video containing the complete performance. Build the
vertical cut by alternating fixed crops around the active speaker and occasional centered resets.

Use when:

- the landscape master already has good speech, identity, and interaction
- source resolution supports portrait extraction
- reshooting or regenerating singles would introduce continuity risk

Keep every crop interval contiguous and frame-quantized. Use fixed punch-in cuts by default; a
continuous synthetic pan or zoom should be motivated and separately approved.

## SoloRelay

Generate each speaker independently using approved solo anchors and a shared scene specification.

Use when:

- dialogue is long or legally sensitive
- voices must remain distinct
- `DuoLock` failed repeatedly
- a two-shot is optional

Match camera height, lens feel, color, background landmarks, and complementary eyelines. A brief
static or separately generated two-shot may establish the location, but do not let that reintroduce
the same dialogue-control failure.

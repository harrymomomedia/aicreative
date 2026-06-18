# CIW Private Form Ad Learnings

Date: 2026-06-10

## Generation

- For Veo Lite UGC, verify `clip01` first, then batch the remaining clips in parallel once the persona/voice/framing passes.
- Use a clean clip-1 anchor rotation for clips 2-N: eyes open, forward gaze, no blink frames.
- Avoid source anchors with a hand close to the camera. Generate or pick a video-safe medium-close anchor where hands are low or out of frame.
- If a clip boundary looks like a soft dissolve, it is usually not ffmpeg. It is often Veo producing a ghosty/blurred end-of-clip settle. Fix by trimming the tail or rerolling the dense clip shorter, then rebuild with hard jump cuts.
- Dense 8-second dialogue can cause end-of-clip wobble. Shorten the line rather than trying to hide the transition.

## Script / Speech

- Keep the compensation hook in the first line: sexual abuse + CIW Chino / California women's prison + significant potential compensation.
- For this campaign, do not let story texture delay the offer. The first 5 seconds should establish that this is for former CIW Chino / California women's-prison inmates and that staff sexual abuse may qualify for significant potential compensation.
- Veo/Scribe repeatedly confused "form" with "forum" on this ad. If the spoken word matters, either test it directly or dodge with a clearer phrase such as "page" or "private questions."
- Avoid "private check" for eligibility-page copy because it can sound like a payment/check instead of a private eligibility form.
- When the user wants "Black LA voice" or community-specific voice, keep the language plain, direct, and spoken. Do not overdo slang; the realism comes from cadence and simplicity.

## Creative / Prompting

- The user rejected too many same-sounding testimonial formats. Future concept batches should vary the format and speaker: direct eligibility notice, comment debate, story cold open, checklist/document angle, family-member perspective, advocate/case-worker tone, and commentary/news-adjacent formats.
- When pitching concepts for a 35-55 second ad, include at least the first 2-3 sentences of the hook so the user can judge the opening, not just the title.
- Mention the women's-prison context early. Concepts that do not say the ad is about women's prisons can lose people before the compensation point lands.
- For video-model prompting, avoid forcing words that the model keeps mishearing. Rewrite around the concept instead of burning repeated generations.

## Captions

- Do not default to per-word yellow highlight captions for sensitive legal UGC. They can read as flashy because the highlight changes every spoken word.
- Preferred calm choices for this ad type:
  - `nick` for a clean, less creator-heavy testimonial look.
  - `hormozi3_no_emoji` for punchy creator captions without emojis or per-word flashing.
  - simple `caption.py` phrase captions when the least distracting style is needed.
- Real Submagic/API captions can alter wording. For regulated legal copy, prefer in-house styles where we control text and can bias/fix Scribe terms.

## Deliverables

- Keep clean masters separate from captioned/disclaimer versions.
- Free Google Flow Veo may add a bottom-right watermark; crop/scale the master before captioning.

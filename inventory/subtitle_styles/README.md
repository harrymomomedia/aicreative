# Subtitle Style Inventory

This folder is the central list of subtitle/caption styles we have built or used so far.

- `styles.json` is the machine-readable registry.
- `samples/` contains symlinks to representative renders and comparison stills.
- Keep style IDs stable so batch scripts can reference them by name.

## Current CA JDC News Choice

Use `news_bbc_center_medium` for the current CA JDC cobalt lower-third news
batch unless the user chooses another style. `news_bbc_left` is still an
approved alternate; the user liked the left-aligned version visually, but the
approved ad02-ad08 render batch used `BBC Center Medium`.

## Sensitive Legal UGC Choice

For direct-to-camera legal UGC about sexual abuse, do **not** default to the
per-word yellow highlight styles. They can read as flashy because the highlight
changes every spoken word. Prefer:

1. `nick` for the calmest readable testimonial look.
2. `hormozi3_no_emoji` for a punchier creator-caption look without emojis or
   per-word flashing.
3. `caption.py` / simple phrase captions for the least distracting in-house
   option.

Use `yellow_text_submagic` or `yellow_box_submagic` only when the user
explicitly asks for that active-word TikTok/Submagic look.

For CA JDC reporter videos, the normal render order is:

1. Start from a clean master with no burned captions and no lower-third.
2. Apply the cobalt broadcast lower-third.
3. Apply `news_bbc_center_medium` subtitles.
4. Apply the legal disclaimer at the top for 6 seconds.

```bash
ffmpeg -y -i <clean.mp4> \
  -i outputs/ca_jdc_tv_reporter/lower_third/broadway_style_lower_third_overlay.png \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 18 -c:a copy \
  <tmp_bluebar.mp4>

.venv/bin/python scripts/caption_news_subtitle.py <tmp_bluebar.mp4> \
  --out <tmp_bluebar_bbc_center_medium.mp4> \
  --style bbc --vertical-pos 0.585 --font-ratio 0.035 \
  --max-width-ratio 0.78 --max-words 8 --font-index 10

.venv/bin/python scripts/burn_disclaimer.py <tmp_bluebar_bbc_center_medium.mp4> <final.mp4> \
  --vertical-pos 0.17 --secs 6.0
```

## Style IDs

### News / Broadcast Subtitles

- `news_bbc_left` - left-aligned BBC-style black box. User pointed back to this one as preferred.
- `news_bbc_center_bold` - centered BBC-style black box, bold.
- `news_bbc_center_medium` - centered BBC-style black box, lighter.
- `news_youtube_classic` - centered white text with black outline, no box.
- `news_youtube_box` - centered white text with translucent black box.

### UGC / Creator Captions

- `hormozi3` - in-house Hormozi 3 clone with rotating yellow/green/red line accents and animated emojis.
- `hormozi3_submagic_match` - Hormozi 3 with Submagic card grouping and captured emoji positions/motion.
- `hormozi3_no_emoji` - Hormozi 3 text system, emoji disabled.
- `yellow_text_submagic` - all-caps TikTok/Submagic style with active word in yellow text.
- `yellow_box_submagic` - all-caps TikTok/Submagic style with yellow box behind active word.
- `nick` - internal clone of Submagic Nick: sentence case, white text, dark rounded box.
- `nick_high_news_legacy` - Nick-style rounded box moved higher for old news/lower-third layouts.

### External API Caption Styles

- `submagic_builtin_template` - Submagic API built-in templates such as Hormozi 3, Lewis, Dan 2, Kelly 2, Jack, Claire, Matt.
- `submagic_lewis_template` - specific Submagic Lewis render path with a Lewis sample.
- `submagic_matt_l1_theme` - custom Submagic theme ID `de96476a-c235-410a-a3db-fa52a9265537`.

## Companion Overlays

These are not subtitles, but are commonly paired with subtitle renders:

- `ca_news_top_disclaimer` - Pulaski/Jones legal disclaimer at top for CA news videos.
- `pulaski_jones_bottom_disclaimer` - same disclaimer at bottom for videos without a lower-third.
- `broadcast_blue_lower_third` - cobalt `BREAKING NEWS` lower-third.

## Samples

Key sample files:

- `samples/news_bbc_left.mp4`
- `samples/news_bbc_center_bold.mp4`
- `samples/news_bbc_center_medium.mp4`
- `samples/news_youtube_classic.mp4`
- `samples/news_youtube_box.mp4`
- `samples/hormozi3_emoji.mp4`
- `samples/hormozi3_text.mp4`
- `samples/nick_internal.mp4`
- `samples/nick_high.mp4`
- `samples/submagic_hormozi3_api.mp4`
- `samples/submagic_lewis_api.mp4`
- `samples/yellow_or_box_styled.mp4`

## Notes

- In-house styles use ElevenLabs Scribe timestamps and preserve source resolution.
- Submagic API styles auto-transcribe and can change wording, so use in-house styles for legal/regulatory copy when exact text matters.
- Active-word yellow styles (`yellow_text_submagic`, `yellow_box_submagic`) can
  feel like flashing on serious legal UGC. Do not choose them by default for
  sexual-abuse/prison ads.
- Do not apply styles to already-captioned or already-lower-thirded videos unless intentionally stacking layers.
- Keep clean masters separate from processed outputs.

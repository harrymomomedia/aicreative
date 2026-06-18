# CA JDC News Reporter Learnings

Date: 2026-06-12

Scope: California / L.A. County juvenile facility sexual-abuse legal lead-gen ads in a TV reporter / news update style.

## Campaign Rules

- This campaign is CA JDC / L.A. County juvenile facility sexual abuse. Do not tag, upload, or describe it as women's prison, Chowchilla, CIW, or CCWF.
- AdMachin project/subproject: `Tort` (`e15c60bd-95c2-47b9-9730-c29fb5325461`) / `CA JDC` (`f1ce41d8-4098-4f92-80ff-e65d08ed01a1`).
- Recent blue-bar/BBC-center creative rows: `#657`-`#662`; existing CA creative `#656` was also used in that final-ad batch.
- Final ads from that batch: `#364`-`#370`; later CA ads `#371`-`#372` used the same CA copy. Re-check `list_ads` before saying whether anything is launched because launch state changed after creation.
- The qualifying harm is sexual abuse. Do not use generic "abuse" alone as the core claim because generic abuse is not qualifying.
- Keep legal language careful: "may qualify," "claims," "legal claims," "significant compensation." Do not promise an outcome.
- Existing primary copy row `#465` has a typo (`an California`) and stronger wording (`paid millions`, `owed`). Do not copy those issues into new CA scripts/copy unless legal explicitly approves.
- Script tests should vary structure. Do not make five ads with the same hook/body/facility/CTA pattern. The CTA can stay present, but even CTA phrasing should vary when testing.
- Facility mentions are optional if the ad already says L.A. County juvenile hall / juvenile facility. When listing facilities, prefer this order and use 2-4 names: Barry J. Nidorf Juvenile Hall, Eastlake / East Lake Central Juvenile Hall, Los Padrinos Juvenile Hall, Challenger Memorial Youth Center.
- Lower-third title should be short. The approved direct title was "Sexual Abuse Legal Claims"; avoid reverting to long originals.

## Next Creative Gaps

- The current CA set is clustered around news/reporter proof, L.A. County scale, facility lists, and compensation CTA. Future tests should target different decision moments, not just new wording.
- Strong next buckets: form walkthrough, no old report needed, privacy-first, family/brother perspective, facility-memory trigger, too-long-ago myth, and wrong-claim filter (general mistreatment vs sexual abuse).

## Clean Reporter Videos

These were the recent news-style clean previews the user asked to list and continue from:

| Ad | Final clean preview | Duration | Notes |
|---|---|---:|---|
| ad02 | `outputs/ca_jdc_news_reporter_40s/ad02_avatar01/clean_trim_preview.mp4` | 38.87s | Trimmed trailing "The la-" style ghost tail. One clip omitted a leading "The"; meaning still held. |
| ad03 | `outputs/ca_jdc_news_reporter_40s/ad03_avatar02/clean_trim_preview.mp4` | 37.77s | Clean exact trim. |
| ad05 | `outputs/ca_jdc_news_reporter_40s/ad05_avatar05/clean_trim_preview.mp4` | 37.56s | Scribe heard "Barry J. Nidorf" like "Neidorff"; reroll/check pronunciation if facility pronunciation matters. |
| ad06 | `outputs/ca_jdc_news_reporter_40s/ad06_avatar06/clean_trim_preview.mp4` | 32.55s | Main fix was removing long silent/music tails between clips. |
| ad08 | `outputs/ca_jdc_news_reporter_40s/ad08_avatar08/clean_trim_preview.mp4` | 34.66s | Main fix was cutting the repeated opening phrase/voice duplicate. |

Related review file: `outputs/ca_jdc_tv_reporter/news_video_master_review/MANIFEST.md` lists older Veo and Replicate p-video candidates. It explicitly excludes `outputs/ca_jdc_news_reporter_urgent/story_ca_jdc_news_reporter_final.mp4` as a source because it has an old lower-third baked in.

AdMachin creative transcriptions are often `null` for newer uploads. When auditing ideas, use local Scribe JSON/transcript files first, then AdMachin copy/ad structure as secondary evidence.

## Generation And QA

- For generated video chunks or finals, post the clickable video path/link in chat immediately after generation, before verification, trimming, captioning, or post-production.
- Do not use frozen-frame pads, slowed video/audio, stabilization, forced zoom/crop fixes, or other ffmpeg "make it look stable" tricks unless the user explicitly approves. These were rejected as unnatural. Prefer rerolling the bad clip or changing prompt/provider.
- For Veo reporter clips, raw chunks often contain silence tails, repeated phrases, or ghost words. Fix with word-aware Scribe trimming against the intended line, then listen to boundaries. Do not trim off the first word just to make the cut tighter.
- If the video says the intended sentence clearly but drops a harmless leading article, do not reroll automatically. If it cuts a meaningful word, repeats a phrase, or creates weird audio, reroll the specific clip.
- If a sensitive prompt starts hitting "prominent person" or policy issues, switch to a different avatar first. If not enough avatars work, generate new avatars.

## Replicate p-video Notes

- Use image-to-video / native audio for p-video tests. Do not provide an external audio input by default.
- ElevenLabs Voice Design reporter voices sounded fake to the user. Do not use those for this reporter style unless explicitly requested.
- Keep p-video prompts short. Long instructions confused the model.
- Prompt requirements that helped: fixed camera, fixed frame, no zoom, no panning, no camera movement, no crop change, keep exact first-frame composition, natural mouth movement, small blinks, clean native audio.
- Always include a no-text instruction for p-video: "No screen text, no graphics, no labels, no logos." Asking for subtitles, lower-thirds, or news graphics caused hallucinated baked text.
- p-video still creates subtle camera "breathing." The user accepted this as a model limit after prompt attempts, but do not add ffmpeg stabilization unless approved.
- 10s chunks were safer when lip-sync/audio failed. 20s chunks can work but are more likely to leak instructions or produce weird audio.
- `ca_btvrep06` / avatar6 was more prone to fake text/lower-third artifacts in this session. Use with caution for p-video reporter ads.

## Voice Design Rejection

- Voice previews were saved under `outputs/ca_jdc_voice_design/reporter_f_v1/` and `outputs/ca_jdc_voice_design/reporter_f_v2_lower_anchor/`.
- The user rejected the ElevenLabs Voice Design direction as not realistic enough: "seems kind of fake, it doesn't have that realism." Keep native model audio first for reporter-avatar tests.
- The account had a 30/30 ElevenLabs voice-slot limit. Do not delete voices to make room unless the user approves.

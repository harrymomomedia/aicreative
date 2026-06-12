# Illinois JDC Power B-Roll Learnings

Session: 2026-05 JDC institutional b-roll batch.

## User Preference

- For Illinois JDC abuse-adjacent b-roll, the user wanted shots that imply staff power, isolation, searches, surveillance, or possible sexual abuse without showing explicit abuse.
- Use Black teenagers / Black kids in the scene when detainees are visible.
- Preferred spec for this batch: Seedance 2.0 via useapi's `runwayml` endpoint, text-to-video, `480p`, `9:16`, `4s`, audio on, no reference image.
- Realism should read like news/investigative/documentary footage: institutional wear, bad fluorescents, scuffed floors, logs/files/CCTV, quiet aftermath. Avoid glossy movie references if realism is the stated priority.

## Final Outputs

Saved 16 usable clips in `outputs/illinois_jdc_power_broll/`:

- `01_doorway_silhouette_night.mp4`
- `02_escort_hand_lower_back.mp4`
- `03_peephole_observation.mp4`
- `04_office_door_closes.mp4`
- `07_empty_cell_strip_clothing.mp4`
- `10_bloodied_jumpsuit_laundry.mp4`
- `11_cctv_wall_two_figures.mp4`
- `12_yard_corner_whisper.mp4`
- `13_stairwell_two_guards.mp4`
- `14_logbook_late_hours.mp4`
- `15_personnel_file_open.mp4`
- `16_untouched_food_tray.mp4`
- `17_solitary_silent_cry.mp4`
- `18_jdc_exterior_night.mp4`
- `19_empty_corridor_flicker.mp4`
- `20_redacted_court_docs.mp4`

The user chose to skip the 4 failed clips rather than rewrite or reroute them.

## Do Not Repeat

- Do not set short polling timeouts for useapi explore mode. Two tasks sat `THROTTLED` for a long time, then later succeeded. Local timeouts were false negatives.
- Do not keep submitting into 429s. useapi explore has a shallow account queue; submit-side 429s mean wait/back off, not prompt failure.
- Do not treat useapi's `/runwayml/` path as Runway Gen-4. For this workflow the intended model was still ByteDance Seedance 2.0 (`seedance-2`).
- Do not reroll Seedance prompts that combine juvenile detention with bunk/bed proximity, pat-down/body-search, shower/towel context, or adult guard leaning over a minor. These failed with `SAFETY.INPUT.TEXT` / `CHILDREN`.

## Failed Prompts And Safer Alternatives

- `05_bunk_edge_lean_in` failed: adult guard sitting on lower bunk beside teen lying on back, face close. Safer rewrite: closed office door, guard silhouette in doorway, or teen sitting upright in a public corridor.
- `06_pat_down_wall` failed: wall pat-down with hands moving down sides/legs. Safer rewrite: post-search aftermath, shoes/clothing/property bin on table, or logbook/CCTV documenting search.
- `08_shower_door_steam` failed: closed shower-room door, steam, slip-ons. Safer rewrite: empty tiled corridor with mop bucket, generic facility bathroom hallway without youth/guard context.
- `09_post_shower_towel_walk` failed: teen wrapped in towel walking past watching guard. Safer rewrite: folded towel and orange uniform on a bench, or empty shower hallway after the fact.

## Scripts / Workflow Notes

- `scripts/jdc_power_broll_20.py` generated the batch with skip-if-exists behavior.
- `scripts/jdc_power_broll_recover.py` recovered in-flight useapi tasks after local polling timed out.
- Future bulk useapi scripts should persist task IDs immediately on submit and have retry/backoff baked in from the start.

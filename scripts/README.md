# Scripts

`scripts/` contains reusable command-line tools and stable legacy campaign entry points.

## Organization

- Canonical reusable tools stay in `scripts/`.
- New campaign orchestration belongs in `jobs/<campaign>/<concept>/`.
- Existing campaign scripts remain at their current paths until they are deliberately migrated;
  many historical jobs import one another by filename.
- Compatibility wrappers preserve old commands after a campaign-specific script receives a more
  honest name.
- Generated media belongs in `outputs/`; campaign facts and learnings belong in `inventory/`.

## Catalog

Regenerate the complete workflow and skill inventory:

```bash
.venv/bin/python scripts/catalog_video_workflows.py
```

Outputs:

- `inventory/video_workflow_catalog.md`
- `inventory/video_workflow_catalog.json`
- `inventory/skill_catalog.md`

The catalog scans every Python workflow in `scripts/` plus the root provider/client modules,
records campaign, lifecycle status, provider signals, and reusable techniques, and flags
unassigned files for review.

## Instruction And Memory Audit

Check root-manual budgets, active Claude memory, stale rules, and live skill mirrors:

```bash
.venv/bin/python scripts/audit_instruction_bloat.py
```

## Canonical Video Utilities

- `pick_clean_anchors.py`: eyes-open clip-1 anchor selection and manifest
- `framewise_video_qa.py`: flashes, black frames, freezes, and transition review
- `audio_match.py`: loudness and spectral checks
- `voice_consistency.py`: speaker and pitch consistency
- `trim_silence.py`: transcript-timed native-speed trimming
- `crop_4x5.py`: letterbox-aware feed conversion
- `caption_styled.py`, `caption_hormozi3.py`, `caption_nick.py`, `caption_redwood.py`: caption engines
- `scan_burned_text.py`: unintended burned-text detection

Provider routes and quality rules live in the general video skills, not in this README.

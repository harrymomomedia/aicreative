# Vertical Interview Reframing

Use `scripts/reframe_interview.py` to build a native-speed 9:16 interview edit from one landscape
master.

## Plan Format

```json
{
  "width": 1080,
  "height": 1920,
  "shots": [
    {"label": "wide reset", "start_frame": 0, "end_frame": 48, "x": 0.50, "y": 0.50, "zoom": 1.00},
    {"label": "interviewer", "start_frame": 48, "end_frame": 144, "x": 0.27, "y": 0.48, "zoom": 1.08},
    {"label": "guest", "start_frame": 144, "end_frame": 288, "x": 0.74, "y": 0.48, "zoom": 1.12}
  ]
}
```

- `start_frame` is inclusive and `end_frame` is exclusive.
- Every shot must start on the previous shot's exact `end_frame`.
- `x` and `y` are normalized subject centers in the source frame.
- `zoom=1.0` is the widest full-height portrait crop; values above 1 make a tighter fixed crop.
- Crop changes are hard cuts. The script does not slow, freeze, interpolate, or time-stretch.

## Command

```bash
.venv/bin/python scripts/reframe_interview.py \
  landscape-master.mp4 \
  shot-plan.json \
  vertical-edit.mp4
```

The script writes `vertical-edit.reframe.json` with source metadata, quantized boundaries, crop
geometry, and any upscale warning.

## Source Resolution

For a landscape source of width `W` and height `H`, a full-height 9:16 crop contains roughly
`H * 9 / 16` source pixels across.

- 3840x2160 master: about 1215 pixels across, suitable for 1080x1920 delivery.
- 1920x1080 master: about 608 pixels across, better suited to 720x1280 or an approved upscale.

Inspect faces at delivery size. A technically valid crop can still be too soft.

#!/usr/bin/env python3
"""Cut a landscape interview master into fixed, frame-accurate vertical punch-ins."""

from __future__ import annotations

import argparse
import json
import math
import shlex
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def even_ceil(value: float) -> int:
    result = int(math.ceil(value))
    return result if result % 2 == 0 else result + 1


def even_clamped(value: float, maximum: int) -> int:
    result = max(0, min(int(round(value)), maximum))
    if result % 2:
        result -= 1
    return max(0, result)


def parse_rate(value: str) -> Fraction:
    rate = Fraction(value)
    if rate <= 0:
        raise ValueError(f"invalid frame rate: {value}")
    return rate


def probe_video(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    video_stream = next(
        (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
        None,
    )
    if not video_stream:
        raise ValueError(f"no video stream found: {path}")

    rotation = int(video_stream.get("tags", {}).get("rotate", 0) or 0)
    if rotation % 360:
        raise ValueError("normalize rotation metadata before interview reframing")

    rate_text = video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")
    rate = parse_rate(rate_text)
    duration_text = video_stream.get("duration") or payload.get("format", {}).get("duration")
    duration = float(duration_text) if duration_text else None
    frame_count = video_stream.get("nb_frames")

    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "rate": rate,
        "rate_text": rate_text,
        "duration": duration,
        "frame_count": int(frame_count) if frame_count and frame_count != "N/A" else None,
        "has_audio": any(
            stream.get("codec_type") == "audio" for stream in payload.get("streams", [])
        ),
    }


def frame_value(shot: dict[str, Any], key: str, rate: Fraction) -> int:
    frame_key = f"{key}_frame"
    if frame_key in shot:
        return int(shot[frame_key])
    if key in shot:
        return int(round(float(shot[key]) * float(rate)))
    raise ValueError(f"shot is missing {frame_key!r} or {key!r}")


def load_plan(path: Path, source: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    width = int(payload.get("width", 1080))
    height = int(payload.get("height", 1920))
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("output width and height must be positive even integers")

    raw_shots = payload.get("shots")
    if not isinstance(raw_shots, list) or not raw_shots:
        raise ValueError("plan must contain a non-empty shots list")

    shots: list[dict[str, Any]] = []
    previous_end: int | None = None
    for index, raw in enumerate(raw_shots):
        if not isinstance(raw, dict):
            raise ValueError(f"shot {index + 1} must be an object")
        start_frame = frame_value(raw, "start", source["rate"])
        end_frame = frame_value(raw, "end", source["rate"])
        if start_frame < 0 or end_frame <= start_frame:
            raise ValueError(f"shot {index + 1} has invalid frame boundaries")
        if previous_end is not None and start_frame != previous_end:
            raise ValueError(
                f"shot {index + 1} starts at frame {start_frame}; "
                f"expected contiguous frame {previous_end}"
            )

        x = float(raw.get("x", 0.5))
        y = float(raw.get("y", 0.5))
        zoom = float(raw.get("zoom", 1.0))
        if not 0 <= x <= 1 or not 0 <= y <= 1:
            raise ValueError(f"shot {index + 1} x/y must be between 0 and 1")
        if zoom < 1 or zoom > 4:
            raise ValueError(f"shot {index + 1} zoom must be between 1 and 4")

        shots.append(
            {
                "label": str(raw.get("label", f"shot-{index + 1:02d}")),
                "start_frame": start_frame,
                "end_frame": end_frame,
                "x": x,
                "y": y,
                "zoom": zoom,
            }
        )
        previous_end = end_frame

    available_frames = source["frame_count"]
    if available_frames is None and source["duration"] is not None:
        available_frames = int(math.floor(source["duration"] * float(source["rate"]) + 0.5))
    if available_frames is not None and shots[-1]["end_frame"] > available_frames + 1:
        raise ValueError(
            f"plan ends at frame {shots[-1]['end_frame']}, "
            f"but source has about {available_frames} frames"
        )

    return {"width": width, "height": height, "shots": shots}


def crop_geometry(
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
    x: float,
    y: float,
    zoom: float,
) -> dict[str, Any]:
    scale = max(target_width / source_width, target_height / source_height) * zoom
    scaled_width = even_ceil(source_width * scale)
    scaled_height = even_ceil(source_height * scale)
    crop_x = even_clamped(x * scaled_width - target_width / 2, scaled_width - target_width)
    crop_y = even_clamped(y * scaled_height - target_height / 2, scaled_height - target_height)
    return {
        "scaled_width": scaled_width,
        "scaled_height": scaled_height,
        "crop_x": crop_x,
        "crop_y": crop_y,
        "upscale": max(scaled_width / source_width, scaled_height / source_height),
    }


def build_filter(
    source: dict[str, Any],
    plan: dict[str, Any],
) -> tuple[str, list[dict[str, Any]], float]:
    shots = plan["shots"]
    count = len(shots)
    filters: list[str] = []
    geometries: list[dict[str, Any]] = []

    if count == 1:
        filters.append("[0:v]null[vin0]")
        if source["has_audio"]:
            filters.append("[0:a]anull[ain0]")
    else:
        video_inputs = "".join(f"[vin{index}]" for index in range(count))
        filters.append(f"[0:v]split={count}{video_inputs}")
        if source["has_audio"]:
            audio_inputs = "".join(f"[ain{index}]" for index in range(count))
            filters.append(f"[0:a]asplit={count}{audio_inputs}")

    max_upscale = 0.0
    for index, shot in enumerate(shots):
        geometry = crop_geometry(
            source["width"],
            source["height"],
            plan["width"],
            plan["height"],
            shot["x"],
            shot["y"],
            shot["zoom"],
        )
        max_upscale = max(max_upscale, geometry["upscale"])
        geometries.append({**shot, **geometry})

        filters.append(
            f"[vin{index}]"
            f"trim=start_frame={shot['start_frame']}:end_frame={shot['end_frame']},"
            "setpts=PTS-STARTPTS,"
            f"scale={geometry['scaled_width']}:{geometry['scaled_height']}:flags=lanczos,"
            f"crop={plan['width']}:{plan['height']}:{geometry['crop_x']}:{geometry['crop_y']},"
            f"setsar=1,format=yuv420p[v{index}]"
        )
        if source["has_audio"]:
            start = shot["start_frame"] / float(source["rate"])
            end = shot["end_frame"] / float(source["rate"])
            filters.append(
                f"[ain{index}]"
                f"atrim=start={start:.9f}:end={end:.9f},"
                f"asetpts=PTS-STARTPTS,aresample=48000[a{index}]"
            )

    if count == 1 and source["has_audio"]:
        filters.append("[v0]null[vout]")
        filters.append("[a0]anull[aout]")
    elif count == 1:
        filters.append("[v0]null[vout]")
    elif source["has_audio"]:
        concat_inputs = "".join(f"[v{index}][a{index}]" for index in range(count))
        filters.append(f"{concat_inputs}concat=n={count}:v=1:a=1[vout][aout]")
    else:
        concat_inputs = "".join(f"[v{index}]" for index in range(count))
        filters.append(f"{concat_inputs}concat=n={count}:v=1:a=0[vout]")

    return ";".join(filters), geometries, max_upscale


def render(
    source_path: Path,
    output_path: Path,
    filter_complex: str,
    has_audio: bool,
    overwrite: bool,
) -> list[str]:
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]
    command.append("-y" if overwrite else "-n")
    command.extend(["-i", str(source_path), "-filter_complex", filter_complex])
    command.extend(["-map", "[vout]"])
    if has_audio:
        command.extend(["-map", "[aout]"])
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
        ]
    )
    if has_audio:
        command.extend(["-c:a", "aac", "-b:a", "192k"])
    else:
        command.append("-an")
    command.extend(["-movflags", "+faststart", str(output_path)])
    subprocess.run(command, check=True)
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cut a landscape interview master into frame-accurate vertical crops."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--max-upscale",
        type=float,
        default=2.0,
        help="Reject crop plans that enlarge source pixels beyond this factor (default: 2.0).",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        parser.error("ffmpeg and ffprobe must be installed")
    if not args.input.is_file():
        parser.error(f"input does not exist: {args.input}")
    if not args.plan.is_file():
        parser.error(f"plan does not exist: {args.plan}")
    if args.output.exists() and not args.overwrite and not args.dry_run:
        parser.error(f"output exists; use --overwrite: {args.output}")
    if args.max_upscale < 1:
        parser.error("--max-upscale must be at least 1")

    source = probe_video(args.input)
    plan = load_plan(args.plan, source)
    filter_complex, geometries, max_upscale = build_filter(source, plan)
    if max_upscale > args.max_upscale:
        parser.error(
            f"plan requires {max_upscale:.2f}x enlargement; "
            f"limit is {args.max_upscale:.2f}x"
        )

    if max_upscale > 1.05:
        print(f"WARNING: tightest crop enlarges source pixels {max_upscale:.2f}x")

    preview_command = [
        "ffmpeg",
        "-i",
        str(args.input),
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
    ]
    if source["has_audio"]:
        preview_command.extend(["-map", "[aout]"])
    preview_command.append(str(args.output))

    if args.dry_run:
        print(shlex.join(preview_command))
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = render(
        args.input,
        args.output,
        filter_complex,
        source["has_audio"],
        args.overwrite,
    )
    manifest = {
        "source": {
            "path": str(args.input.resolve()),
            "width": source["width"],
            "height": source["height"],
            "frame_rate": source["rate_text"],
            "duration": source["duration"],
            "has_audio": source["has_audio"],
        },
        "output": {
            "path": str(args.output.resolve()),
            "width": plan["width"],
            "height": plan["height"],
        },
        "native_speed": True,
        "max_upscale": round(max_upscale, 6),
        "shots": geometries,
        "ffmpeg": command,
    }
    manifest_path = args.output.with_suffix(".reframe.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered: {args.output}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

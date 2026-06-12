---
name: personal-iot-hardware
description: Use when Harry asks about personal-use IoT hardware builds, especially cameras, RTSP/ONVIF, smart feeders, pet training devices, local-vs-cloud setup, Raspberry Pi, or low-cost smart-home automation.
---

# Personal IoT Hardware

Use this skill for personal hardware brainstorms where the user wants practical build architecture, not an ad-production workflow. Keep the discussion grounded in what can actually be bought and scripted.

## User Preferences

- The user prefers cheap, practical, off-the-shelf setups before custom hardware.
- The user is comfortable discussing custom code and APIs, but not eager to solder or build mechanical hardware unless necessary.
- For personal pet/camera projects, the user cares about privacy but is fine with a camera aimed only at a pee pad or bounded target area.
- The user likes the audio-marker approach for dog training: detect the behavior, play a distinct in-room sound, and notify the human to deliver the treat. Do not default back to an automatic dispenser unless they ask for full autonomy.

## Dog Pee-Pad Detector Notes

- Environment selected: indoor potty pad / litter-box style area. This is a bounded camera view and the easiest computer-vision case.
- Avoid proposing a pure cloud-only system unless the camera itself can push snapshots/events. A normal home camera stream needs something on the home LAN to pull frames and forward them to a vision API. A Mac at another office cannot see the home camera without VPN/tunnel setup.
- Cheapest reliable home compute path: Raspberry Pi Zero 2 W or similar always-on local box. A Pi handles low-res OpenCV motion gating plus occasional cloud VLM calls.
- Detection approach: use cheap local motion gating first, then call a cloud VLM only when there is activity on the pad. Do not poll the VLM continuously every few seconds all day.
- For marker training, trigger on confirmed pee posture as soon as possible rather than waiting for "dog finished and walked away"; the marker bridges the delay before the human-delivered treat.
- Suggested non-dispenser build: RTSP camera + Pi + USB or Bluetooth speaker + phone push notification such as ntfy. This is cheaper and simpler than integrating a feeder.
- If the user later wants automatic dispensing, Tuya/Smart Life feeders via `tinytuya` are the likely off-the-shelf route, but smallest portions are usually not one-treat precise. Use tiny training treats if trying it.

## Camera Rules Of Thumb

- RTSP means "video stream in" only. It lets code read frames via OpenCV/ffmpeg, but does not imply pan/tilt/control.
- ONVIF or a vendor HTTP API is needed for control: pan/tilt/zoom, snapshots, settings, motion events.
- Snapshot APIs are useful for VLM calls because a single JPEG is cheaper than continuously decoding a full RTSP stream.
- For one cheap indoor camera aimed at a pad, Tapo C200-style cameras are a strong fit if current models still support official RTSP. Reolink E1-style cameras are the safer standards/ONVIF pick, but not automatically better for a one-camera low-cost build.
- Xiaomi cameras are model-dependent. Many newer Mi/Xiaomi cameras are locked to the Mi Home app and do not expose RTSP without hacks. Ask for the exact model before assuming it can be used.
- Avoid assuming Ring, Nest, Arlo, Blink, Furbo, or Petcube are scriptable; they are usually cloud/app-locked and poor fits for custom local CV.

## Do Not Repeat

- Do not over-recommend Reolink when the user's stated goal is cheapest workable hardware; explain why Tapo may be enough.
- Do not describe "remote cloud" as simple if the camera sits behind a home NAT. Name the local-frame-capture requirement early.
- Do not assume all-in-one pet cameras have usable APIs. Most are manual treat tossers plus notifications, not programmable behavior-triggered dispensers.
- Do not push an automatic treat dispenser after the user has accepted audio notification/marker training as the better first version.
- Do not save these pet/IoT notes into campaign-specific ad-learning files.

## Currentness Check

Before giving final buy links or current prices, verify current model availability and API support. Camera firmware and RTSP/ONVIF support can change.

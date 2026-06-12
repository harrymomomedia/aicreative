#!/usr/bin/env python3
"""List subtitle/caption style presets from inventory/subtitle_styles/styles.json."""
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "inventory/subtitle_styles/styles.json"


def load_registry():
    return json.loads(REGISTRY.read_text())


def main():
    ap = argparse.ArgumentParser(description="List known subtitle style presets.")
    ap.add_argument("--style", default=None, help="Print one style entry by id.")
    ap.add_argument("--commands", action="store_true", help="Include render command for each style.")
    ap.add_argument("--json", action="store_true", help="Print raw JSON.")
    args = ap.parse_args()

    registry = load_registry()
    if args.json:
        print(json.dumps(registry, indent=2))
        return

    styles = registry["styles"]
    if args.style:
        match = next((style for style in styles if style["id"] == args.style), None)
        if match is None:
            raise SystemExit(f"unknown style id: {args.style}")
        print(json.dumps(match, indent=2))
        return

    print(f"registry: {REGISTRY}")
    print(f"default_for_ca_jdc_news: {registry.get('default_for_ca_jdc_news')}")
    for style in styles:
        sample = style.get("sample") or "-"
        print(f"{style['id']:<28} {style['name']:<28} {style['script']}  sample={sample}")
        if args.commands:
            print(f"  {style['command']}")


if __name__ == "__main__":
    main()


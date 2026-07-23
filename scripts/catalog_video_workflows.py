#!/usr/bin/env python3
"""Catalog every repository skill and Python workflow without moving legacy entry points.

The repository accumulated campaign jobs in a flat scripts directory. Moving them wholesale
would break imports, docs, and reproducible reruns. This scanner classifies every script and skill
so reusable tools, campaign jobs, experiments, and compatibility wrappers remain visible while
new work adopts the organized jobs/ layout.
"""

import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
SKILLS = ROOT / "skills"
INVENTORY = ROOT / "inventory"

CAMPAIGN_PREFIXES = (
    ("adswipe_1564_", "adswipe-1564"),
    ("cosmechef_", "cosmechef"),
    ("chowchilla_", "california-womens-prison"),
    ("cawp_", "california-womens-prison"),
    ("ccwf_", "california-womens-prison"),
    ("ciw_", "california-womens-prison"),
    ("il_jdc_", "illinois-jdc"),
    ("il_juvie_", "illinois-jdc"),
    ("jdc_", "juvenile-detention"),
    ("jds_", "juvenile-detention"),
    ("depo_", "depo-provera"),
    ("trimrx_", "trimrx"),
    ("cilocala_", "cilocala"),
    ("k4_", "california-womens-prison"),
    ("l2_", "california-womens-prison"),
    ("lr_", "california-womens-prison"),
)

EXPLICIT_CAMPAIGNS = {
    "build_ugc_copy_xlsx": "cilocala",
    "car_selfie_person_swap": "juvenile-detention",
    "car_selfie_person_swap_nb": "juvenile-detention",
    "car_selfie_survivor_test": "juvenile-detention",
    "finalize_a2_variations": "california-womens-prison",
    "gen_black_personas": "california-womens-prison",
    "gen_living_real": "california-womens-prison",
    "gen_personas": "california-womens-prison",
    "gen_white_personas": "california-womens-prison",
    "normalize_a2_variations": "california-womens-prison",
    "pixar_themed_personas": "california-womens-prison",
    "pixarify_personas": "california-womens-prison",
    "podcast_omni_produce": "california-womens-prison",
    "qa_clip1s": "california-womens-prison",
    "burn_pulaski_jones_disclaimer": "pulaski-jones",
    "burn_pulaski_jones_disclaimer_image": "pulaski-jones",
    "render_pulaski_jones_minimal_ad": "pulaski-jones",
}

GENERAL_STEMS = {
    "admachin_client",
    "admachin_mcp_stdio",
    "admachin_push",
    "analyze_submagic_emojis",
    "audit_instruction_bloat",
    "audio_match",
    "caption",
    "caption_hormozi3",
    "caption_linecmp",
    "caption_news_subtitle",
    "caption_nick",
    "caption_redwood",
    "caption_styled",
    "capture_clean_traj",
    "capture_emoji_trajectories",
    "catalog_video_workflows",
    "crop_4x5",
    "detect_card_flips",
    "detect_emojis",
    "dissect",
    "emoji_anim_extract",
    "emoji_diff_track",
    "emoji_entrance_track",
    "emoji_match_report",
    "emoji_slide_measure",
    "emoji_template_probe",
    "extract_submagic_cards",
    "elevenlabs_client",
    "evolink_client",
    "fal_client",
    "framewise_video_qa",
    "googleflow_client",
    "kie_client",
    "openai_image",
    "openrouter_client",
    "openrouter_video",
    "opusclip_client",
    "pick_clean_anchors",
    "poyo_client",
    "rederive_emoji",
    "replicate_client",
    "scan_burned_text",
    "style_test_seedance",
    "submagic_client",
    "subtitle_style_registry",
    "track_emojis",
    "trim_silence",
    "useapi_client",
    "voice_consistency",
}

COMPATIBILITY_STEMS = {
    "admachin_upload_product_broll",
    "burn_disclaimer",
    "burn_disclaimer_image",
    "render_minimal_ad",
}

VARIANT_TOKENS = (
    "test",
    "retry",
    "reroll",
    "recover",
    "fallback",
    "fix",
    "hipri",
    "serial",
    "redownload",
    "variations",
)

TECHNIQUE_PATTERNS = {
    "AdMachin": r"admachin",
    "anchor-continuity": r"pick_clean_anchors|anchor frame|startImage|referenceImage",
    "assembly": r"assemble|stitch|concat",
    "audio-QA": r"audio_match|voice_consistency|loudness|lufs",
    "B-roll": r"\bb[- ]?roll\b",
    "captions": r"caption|subtitle",
    "framewise-QA": r"framewise_video_qa|every-frame|every_frame",
    "image-generation": r"generate_gpt_image|generate_nano_banana|gpt-image",
    "matte-PIP": r"remove_background|alpha webm|matte|picture.in.picture",
    "speech-QA": r"scribe|transcri",
    "video-generation": r"generate_veo|generate_seedance|generate_kling|googleflow|omni-flash",
    "voice-processing": r"voice_changer|clone_voice|voice_id",
}

PROVIDER_PATTERNS = {
    "ElevenLabs": r"elevenlabs|scribe",
    "ffmpeg": r"ffmpeg|ffprobe",
    "Google Flow/useapi": r"googleflow|useapi|omni-flash",
    "HyperFrames": r"hyperframes|gsap",
    "KIE": r"kie_client|gpt-image|nano.banana",
    "Poyo": r"poyo",
    "Seedance": r"seedance",
    "Veo": r"\bveo\b|generate_veo",
}


def first_line(text):
    return " ".join(text.strip().split())[:180]


def module_docstring(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return "", f"{error.msg} at line {error.lineno}"
    return first_line(ast.get_docstring(tree) or ""), None


def infer_campaign(stem, source):
    if stem in GENERAL_STEMS:
        return None
    if stem in EXPLICIT_CAMPAIGNS:
        return EXPLICIT_CAMPAIGNS[stem]
    for prefix, campaign in CAMPAIGN_PREFIXES:
        if stem.startswith(prefix):
            return campaign
    lowered = source.lower()
    signals = (
        ("outputs/depo", "depo-provera"),
        ("chowchilla", "california-womens-prison"),
        ("ccwf", "california-womens-prison"),
        ("juvenile detention", "juvenile-detention"),
        ("cilocala", "cilocala"),
        ("trimrx", "trimrx"),
        ("dakbalm", "cosmechef"),
    )
    matches = {campaign for token, campaign in signals if token in lowered}
    return matches.pop() if len(matches) == 1 else None


def script_record(path):
    source = path.read_text(errors="replace")
    stem = path.stem
    docstring, syntax_error = module_docstring(source)
    campaign = infer_campaign(stem, source)
    if stem in COMPATIBILITY_STEMS:
        role = "compatibility-wrapper"
        status = "legacy"
    elif stem in GENERAL_STEMS:
        role = "reusable-tool"
        status = "experiment" if stem == "style_test_seedance" else "canonical"
    elif campaign:
        role = "campaign-job"
        is_variant = any(token in stem for token in VARIANT_TOKENS) or bool(
            re.search(r"(?:^|_)v\d+(?:_|$)", stem)
        )
        status = "variant" if is_variant else "active-or-historical"
    else:
        role = "unassigned"
        status = "review"

    if stem == "catalog_video_workflows":
        techniques = []
        providers = []
    else:
        techniques = [
            label
            for label, pattern in TECHNIQUE_PATTERNS.items()
            if re.search(pattern, source, flags=re.IGNORECASE)
        ]
        providers = [
            label
            for label, pattern in PROVIDER_PATTERNS.items()
            if re.search(pattern, source, flags=re.IGNORECASE)
        ]
    return {
        "path": str(path.relative_to(ROOT)),
        "role": role,
        "status": status,
        "campaign": campaign,
        "summary": docstring,
        "syntax_error": syntax_error,
        "techniques": techniques,
        "providers": providers,
        "lines": source.count("\n") + 1,
    }


def frontmatter_description(text):
    match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
    return first_line(match.group(1)) if match else ""


def skill_record(path):
    skill_file = path / "SKILL.md"
    source_kind = "vendor-symlink" if path.is_symlink() else "repo-custom"
    if not skill_file.exists():
        return {
            "path": str(path.relative_to(ROOT)),
            "source": source_kind,
            "description": "",
            "lines": 0,
            "campaign_terms": [],
            "status": "missing-SKILL.md",
        }
    text = skill_file.read_text(errors="replace")
    campaign_terms = sorted(
        {
            term
            for term in ("Chowchilla", "CCWF", "CIW", "Depo", "Pulaski", "Jones", "JDC", "TrimRx")
            if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
        }
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "source": source_kind,
        "description": frontmatter_description(text),
        "lines": text.count("\n") + 1,
        "campaign_terms": campaign_terms,
        "status": "ok",
    }


def markdown_table(records, columns):
    header = "| " + " | ".join(label for _, label in columns) + " |"
    rule = "|" + "|".join("---" for _ in columns) + "|"
    rows = [header, rule]
    for record in records:
        values = []
        for key, _ in columns:
            value = record.get(key)
            if isinstance(value, list):
                value = ", ".join(value)
            value = "" if value is None else str(value)
            values.append(value.replace("|", "\\|").replace("\n", " "))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_script_catalog(records):
    role_counts = Counter(record["role"] for record in records)
    campaign_counts = Counter(
        record["campaign"] for record in records if record["campaign"]
    )
    grouped = defaultdict(list)
    for record in records:
        grouped[record["role"]].append(record)

    lines = [
        "# Video Workflow Catalog",
        "",
        "Generated by `scripts/catalog_video_workflows.py`. Legacy campaign entry points remain at",
        "their stable paths; use this catalog to decide what to reuse, migrate, or retire.",
        "",
        f"- Python workflows scanned: **{len(records)}**",
        f"- Reusable tools: **{role_counts['reusable-tool']}**",
        f"- Campaign jobs: **{role_counts['campaign-job']}**",
        f"- Compatibility wrappers: **{role_counts['compatibility-wrapper']}**",
        f"- Unassigned for review: **{role_counts['unassigned']}**",
        "",
        "## Campaign Counts",
        "",
    ]
    for campaign, count in sorted(campaign_counts.items()):
        lines.append(f"- `{campaign}`: {count}")

    columns = [
        ("path", "Path"),
        ("campaign", "Campaign"),
        ("status", "Status"),
        ("techniques", "Techniques"),
        ("summary", "Summary"),
    ]
    for role, title in (
        ("reusable-tool", "Reusable Tools"),
        ("campaign-job", "Campaign Jobs"),
        ("compatibility-wrapper", "Compatibility Wrappers"),
        ("unassigned", "Needs Classification"),
    ):
        lines.extend(["", f"## {title}", ""])
        lines.append(markdown_table(sorted(grouped[role], key=lambda item: item["path"]), columns))

    (INVENTORY / "video_workflow_catalog.md").write_text("\n".join(lines) + "\n")
    (INVENTORY / "video_workflow_catalog.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n"
    )


def write_skill_catalog(records):
    columns = [
        ("path", "Skill"),
        ("source", "Source"),
        ("status", "Status"),
        ("lines", "Lines"),
        ("campaign_terms", "Campaign Terms"),
        ("description", "Description"),
    ]
    content = [
        "# Skill Catalog",
        "",
        "Generated by `scripts/catalog_video_workflows.py`.",
        "",
        markdown_table(sorted(records, key=lambda item: item["path"]), columns),
        "",
        "Campaign terms are a review signal, not automatically a defect. Dedicated campaign",
        "skills such as `pulaski-jones-disclaimer` should retain their regulated campaign content.",
        "",
    ]
    (INVENTORY / "skill_catalog.md").write_text("\n".join(content))


def main():
    INVENTORY.mkdir(parents=True, exist_ok=True)
    workflow_paths = sorted(
        list(SCRIPTS.rglob("*.py")) + list(ROOT.glob("*.py"))
    )
    script_records = [
        script_record(path)
        for path in workflow_paths
        if "__pycache__" not in path.parts
    ]
    skill_records = [
        skill_record(path)
        for path in sorted(SKILLS.iterdir())
        if path.is_dir()
    ]
    write_script_catalog(script_records)
    write_skill_catalog(skill_records)
    print(
        f"catalogued {len(script_records)} Python workflows and {len(skill_records)} skills",
        flush=True,
    )
    unassigned = [record["path"] for record in script_records if record["role"] == "unassigned"]
    if unassigned:
        print(f"unassigned workflows: {len(unassigned)}", flush=True)
        for path in unassigned:
            print(f"  {path}", flush=True)


if __name__ == "__main__":
    main()

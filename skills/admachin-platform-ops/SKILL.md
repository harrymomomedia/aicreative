---
name: admachin-platform-ops
description: AdMachin platform API mechanics — upload/verify creatives, compose ads with copy, the ad_type DB-constraint trap, launched-ad immutability, project/subproject filing, and launch gating. Use when the user says "upload to admachin", "stage the ad", "compose ad with copy", "ad_type error", "the upload didn't show up", "edit a launched ad", "move the creative", or any AdMachin API/staging/launch operation. Distinct from admachin-video-ads (creative/compliance rules) — this is the platform plumbing.
---

# AdMachin Platform Ops — API mechanics that recur every campaign

These traps have each recurred across ≥3 campaigns. Full API contract details in CLAUDE.md
("Publishing to AdMachin"); this skill is the operational checklist.

## Upload → verify (never trust the upload response)

- `upload_creative` can return a success record for a file that **doesn't actually persist** —
  ALWAYS verify via `list_creatives` (filter by project) before building ads on the id.
- Pass `project_id` on upload or the creative lands in the default (null) project. Mis-filed?
  `update_creative_metadata` MOVES it (re-tag, no re-upload).
- To hide a creative, MOVE it to a null project — soft-delete via `status:"deleted"` fails a DB
  check constraint.
- Tort project `e15c60bd-…`; Women's Prison subproject `acf1b974-…`, IL JDC `7f876467-…`.
  Resolve names → UUIDs via `list_projects(search=)` / `list_subprojects`.

## Compose (ads + copy)

- **`ad_type` is NOT free-text** — DB check constraint `ads_ad_type_allowed`; a custom label 500s
  `create_ad`/`compose_ad_with_copy` AFTER the creative+copy rows already succeeded. **OMIT
  `ad_type`** (or copy a known-allowed value from an existing ad). Keep a resumable state file so
  the retry only re-runs the ad row.
- **One writer per JSON state file** — two staging scripts sharing one state file clobber each
  other (read-modify-write race).
- **Copy approval gate (user-locked):** present every headline + primary text VERBATIM in chat and
  get explicit approval BEFORE creating copy rows or assembling ads. A template walkthrough is not
  approval.

## Default UTM (JusticeCovered) — REQUIRED on every launched ad

Ads must launch with the full AdMachin "URL Parameters" default (the `{{ }}` macro guide) — a bare
landing URL is wrong. The `/launches` endpoint does NOT accept a `url_tags`/`url_parameters` field,
so the template is appended to **`landing_url`** itself (Facebook fills the macros at delivery; do
NOT url-encode the `{{ }}`). Build it with `admachin_utm.default_landing_url(base, media_buyer)`:

```
https://<campaign>.justicecovered.com/?utm_source={{site_source_name}}&utm_medium=paid_social
&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_id={{campaign.id}}
&campaign_id={{campaign.id}}&campaign_name={{campaign.name}}&adset_id={{adset.id}}
&adset_name={{adset.name}}&ad_id={{ad.id}}&ad_name={{ad.name}}&account_id={{account_id}}
&placement={{placement}}&site_source_name={{site_source_name}}&am_mb=<media_buyer>
```

- Base domain is per-campaign (`womensprison` / `depop` / …). Women's-prison base =
  `https://womensprison.justicecovered.com/`.
- `utm_medium` is static `paid_social`; `am_mb` = media-buyer code (`hj` = Jordan-Jones/Pulaski desk).
- Canonical source of truth: `admachin_utm.py` (`UTM_PARAMS`, `default_landing_url`). Since ads are
  IMMUTABLE once launched, get this right at creation — a wrong/bare URL means recreating the ad.

## FB adset create (duplicate settings, REST)

- `POST /fb/adsets` needs: `confirm: true`, `Idempotency-Key` header, `ad_account_id`, `campaign_id`,
  and `adset_params` (the FB fields). **`adset_params` must NOT include `status`/`campaign_id`/
  account fields** (AdMachin controls those; new adsets land PAUSED).
- `adset_params.daily_budget` is in **DOLLARS** (not cents) with a **$300/day hard safety cap** —
  `$100/day` → `daily_budget: 100`. (The raw Meta `daily_budget` you read back via graph is cents.)
- Duplicate targeting by reading the source adset via `GET /fb/graph-read?path=/<adset_id>&fields=
  targeting,promoted_object,attribution_spec,billing_event,optimization_goal,pacing_type` and
  passing those straight into `adset_params`.
- **Drop the bid cap** by setting `bid_strategy: "LOWEST_COST_WITHOUT_CAP"` and omitting `bid_amount`
  (source used `LOWEST_COST_WITH_BID_CAP` + `bid_amount`).
- **PLACEMENTS — set them EXPLICITLY; never drop the block.** Omitting `publisher_platforms`/
  `*_positions` flips the adset to **Advantage+ automatic, which turns Audience Network ON** — a
  silent, wrong change. The create endpoint also REJECTS the newer position values live adsets carry
  (`threads`, `biz_disco_feed`, `facebook_reels_overlay`, `profile_feed`, `notification`,
  `explore_home`, `ig_search`), so you can't copy the source's list verbatim. Verified-accepted
  **manual set, Audience Network OFF** (`MANUAL_PLACEMENTS` in `scripts/wp_launch_adsets.py`):
  `publisher_platforms:[facebook,instagram,messenger]` (NO audience_network),
  `device_platforms:[mobile,desktop]`, fb:`[feed,right_hand_column,instream_video,marketplace,
  story,search,facebook_reels]`, ig:`[stream,story,reels]`, messenger:`[story]`. Copy the AUDIENCE
  (geo/age/gender) from graph-read; SET placements from this constant.
- **There is NO native adset copy in the REST API** — no `/fb/adsets/{id}/copy`/`/duplicate`, and
  create-from-source fields (`source_adset_id`, `use_create_from_source`, `template_adset_id`, …)
  are all "unknown field". The exact-clone `use_create_from_source` is an **MCP-server** feature
  (local Mac), not available in a cloud/REST session — so in cloud you MUST reconstruct with the
  explicit manual placements above. **No REST update/delete for adsets either** (all 401): a
  wrong adset can't be edited or deleted via API — fix by creating a correct one and deleting the
  wrong one in Meta UI.

## Launch & post-launch

- **Launched ads are IMMUTABLE.** Wrong copy on a live ad → CREATE ONE MORE ad (new draft), never
  edit the live one.
- **Launch is gated, never default** — `scripts/admachin_push.py --launch` + typed `LAUNCH`
  confirmation (or `--yes` for automation). No TTY + no `--yes` = refuse. Launch SPENDS REAL MONEY.
- Ads have NO link field — `landing_url` is supplied at launch time.

## Environment gotchas

- **macOS has no `timeout` command** — wrapping a batch in `timeout 300 …` silently aborts it (an
  entire 20-image batch once never generated). Use a Python-level timeout or plain background runs.
- ElevenLabs voice slots: 30 cap on Creator — do NOT delete voices to free slots without explicit
  user approval.

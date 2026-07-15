# FB Ads Manager / Insights analysis via AdMachin MCP — methodology + gotchas

Reusable across ALL campaigns. How to pull + analyze live Facebook ad performance through the
AdMachin MCP (the FB Marketing/Insights API behind Ads Manager), and the traps that cost time.
Learned doing the IL JDC winner analysis (2026-06-27).

## Pulling data (cheap, rate-limit-safe)

- **Bulk-first:** `get_fb_account_performance_export(ad_account_id, level=ad, date_preset=maximum,
  time_increment=all_days, limit=500)` — ONE call per account; it paginates internally
  (~`ceil(ads/500)` Graph requests). Then aggregate/filter **locally** (jq/python on the saved
  tool-results `.txt`). Do NOT loop one call per campaign/ad — that's what burns rate limit.
- Discover accounts with `list_fb_ad_accounts`; skip `can_download_insights=false` for the bulk export.
- Big results auto-save to a tool-results file — `jq`/python it, never dump.
- **Repeat reads → the CACHE, free:** `list_insights` / `refresh_aggregate_insights(group_by=
  campaign|adset|ad|creative|headline|primary|copy_combo)` hit AdMachin's local copy, ZERO Meta
  calls. Great for rollups — BUT the cache can lag and **undercount leads** (it showed 35 where the
  live API showed the real count); refresh via a live `get_fb_insights` when you need current/accurate.

## Rate limits (BUC "ads_insights", per-account, ~5-min sliding window)

- One account-level `all_days` pull = low cost; you won't come close. What DOES burn budget:
  **daily breakdowns** (`time_increment=1` → rows = ads × days), **fanning out** per-ad/per-campaign
  calls, and re-pulling the same window. ~5 accounts × one bulk pull each is nothing.

## THE leads double-count gotcha (cost a 4× error once)

- FB reports the SAME lead under MULTIPLE `action_type`s: `lead`, `offsite_conversion.fb_pixel_lead`,
  `onsite_web_lead`, `offsite_lead_add_20_s_calls` — all equal. **Summing every "lead"-containing
  action QUADRUPLE-counts leads** (turned 37 real leads into 148, CPL $250 into a fake $63).
  → Use ONE canonical count: `lead` (else `offsite_conversion.fb_pixel_lead`). CPL = spend ÷ that
  single number. The UI's "Results / Cost per Result" column is this de-dup done for you.

## Disabled accounts are still readable (object-level)

- A **disabled** ad account can't spend/run ads, and the bulk export refuses it (`VALIDATION:
  cannot download…account is disabled`). BUT `get_fb_insights` / `get_fb_graph_read` at the OBJECT
  level (campaign / adset / ad id, or even `act_<id>`) STILL returns Meta's stored HISTORICAL
  insights — reading already-collected stats is a different permission than running ads. The data is
  FROZEN (no new spend). Meta insights retention ≈ 37 months, so historical reads keep working.
- The campaign's own `effective_status` can read ACTIVE while the parent ACCOUNT is disabled — check
  `get_fb_graph_read(<campaign_id>, fields=[account_id, effective_status])` to find its account.

## Viewing the actual creatives (pixels, not data)

- Insights + CSV are DATA only — no images. `hydrate_fb_creative_media(ad_id)` fetches the creative
  pixels from Meta into AdMachin (Supabase) storage and returns a public `media_url`; `curl` it +
  Read to view. (`get_fb_ad_full_details` gives copy/settings/creative specs, NOT the pixels.)

## Insights API vs the Ads-Manager CSV export

- For PERFORMANCE data the Insights API is a **superset** of the UI "Export to CSV" (the CSV button
  is just a UI wrapper over the same API). The API also does joins/automation, reads odd-state
  accounts, and runs async large jobs the CSV can't.
- The only extras the UI/CSV has: **settings / targeting / budget columns** (get them from object
  reads `get_fb_ad_full_details` / `get_fb_graph_read`, NOT `/insights`) and the pre-computed
  **Results / Cost-per-Result** column (you compute it from the `actions` array yourself).
- Shared limits (neither wins): ~37-mo retention; Meta **breakdown incompatibilities** (some
  breakdown combos are rejected) hit both because it's the same API.

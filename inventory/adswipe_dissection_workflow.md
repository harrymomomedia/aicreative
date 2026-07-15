# AdSwipe → image-ad dissection workflow (reusable)

How to pull and vision-dissect competitor / own image ads saved in AdMachin **AdSwipe**. Learned on
the TrimRx GLP-1 swipe teardown (47 image ads), 2026-06-18. Reuse for any campaign's swipe library.

## The problem
AdSwipe swipe records (`get_swipe_creative` / `list_swipe_creatives`) arrive with:
- `headline`, `ad_text` (primary/body), `cta_text`, `caption` — populated
- `ocr_text` — PARTIAL (null on many rows initially)
- `media_url`, `thumbnail_url` — **null** (no stored image file)
- `link_url` = the Meta Ad Library page (`facebook.com/ads/library/?id=<ad_archive_id>`); `source` often `chrome_extension`

So you can't Read the creative with vision until you retrieve the image separately.

## Dead ends — do NOT repeat
- **Chrome MCP `javascript_tool` cannot harvest the image URL.** The Ad Library renders the creative
  from an fbcdn URL, but the Chrome MCP redacts any query-string / CDN URL from JS return values →
  `img.src` (and even `location.href`) come back as `"[BLOCKED: Cookie/query string data]"`. Not a
  setting you can flip.
- **Deep-linking `?id=<ad_archive_id>`** defaults to the browser's country (e.g. South Korea) and
  bounces to a generic "~50,000 results" grid instead of the ad; needs `&country=US&active_status=all`
  to render the specific US-targeted ad.
- Screenshotting the Ad Library page works mechanically but is per-ad and slow — and unnecessary once
  the backfill runs.

## The working path
1. **AdMachin backfills the media.** Once run (AdMachin side), `media_url` + `thumbnail_url` populate
   with fetchable **Supabase public URLs**:
   `https://<project>.supabase.co/storage/v1/object/public/media/uploads/extension-imports/<ad_archive_id>/main-media-*.jpg`
   `ocr_text` fills for all rows too. The backfill is **progressive** — re-query until every image row
   has a `media_url`:
   `jq '[.data[]|select(.media_type=="image" or .media_type=="carousel")]|{n:length, with:(map(select(.media_url!=null))|length)}'`
2. **Download + Read.** `curl -L "<media_url>" -o outputs/<campaign>/swipes/<row>.jpg`; Read each with vision.
3. **Dissect at scale.** Build a text manifest (row → headline/primary/ocr/cta via `jq`), then fan out
   parallel subagents (~12 ads each) that Read their assigned image files + the manifest and return a
   per-ad teardown: **STYLE / HOOK / ANGLE / VISUAL / ON-IMAGE-TEXT / CTA / COMPLIANCE-FLAG / DEDUP**.
   Synthesize a style taxonomy + a compliance hot-list (what each ad does that violates the campaign
   rules, so the modeled versions are compliant).

Note: `list_swipe_creatives` payloads are large and auto-save to a tool-results file → `jq` them,
never dump. Filter by `subproject_id` to scope to one campaign.

## TrimRx run (reference)
47 image ads, AdSwipe subproject `d8e4bcc6-…` under GLP-1 project `5e013c51-…`. Full teardown +
compliance hot-list → `inventory/trimrx_swipe_dissection.md`.

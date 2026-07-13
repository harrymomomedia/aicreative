"""Canonical AdMachin / JusticeCovered default UTM template.

The AdMachin "Ad Settings → URL Parameters" default (the full {{ }} macro guide). Facebook fills
the {{ }} macros at delivery. At launch the /launches endpoint does NOT accept a url_tags /
url_parameters field — the parameters must be appended to `landing_url` itself, which is what
`default_landing_url()` builds. Verified 2026-07-12 (women's-prison HJ campaign).

Base domains are per-campaign under *.justicecovered.com (womensprison / depop / …).
`am_mb` = media-buyer code (hj for the Jordan/Jones + Pulaski desk).
"""
from urllib.parse import urlsplit, urlunsplit

# Order + values match the AdMachin UI default exactly. utm_medium is static (paid_social);
# everything else is a Facebook dynamic macro; am_mb is the media-buyer flag.
UTM_PARAMS = [
    ("utm_source",    "{{site_source_name}}"),
    ("utm_medium",    "paid_social"),
    ("utm_campaign",  "{{campaign.name}}"),
    ("utm_content",   "{{ad.name}}"),
    ("utm_id",        "{{campaign.id}}"),
    ("campaign_id",   "{{campaign.id}}"),
    ("campaign_name", "{{campaign.name}}"),
    ("adset_id",      "{{adset.id}}"),
    ("adset_name",    "{{adset.name}}"),
    ("ad_id",         "{{ad.id}}"),
    ("ad_name",       "{{ad.name}}"),
    ("account_id",    "{{account_id}}"),
    ("placement",     "{{placement}}"),
    ("site_source_name", "{{site_source_name}}"),
]

def default_utm(media_buyer="hj"):
    """Return the raw query string (no leading '?'), with the media-buyer flag appended."""
    parts = [f"{k}={v}" for k, v in UTM_PARAMS] + [f"am_mb={media_buyer}"]
    return "&".join(parts)

def default_landing_url(base_url, media_buyer="hj"):
    """Append the full default UTM template to a base landing URL. Preserves any existing path;
    replaces the query. Do NOT url-encode the {{ }} — Facebook needs the literal macros."""
    s = urlsplit(base_url)
    return urlunsplit((s.scheme, s.netloc, s.path or "/", default_utm(media_buyer), ""))

# The campaign's live landing base (women's-prison HJ).
WOMENS_PRISON_BASE = "https://womensprison.justicecovered.com/"

if __name__ == "__main__":
    print(default_landing_url(WOMENS_PRISON_BASE))

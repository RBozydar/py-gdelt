# GDELT HTTPS migration: diagnosis and repair

Verified on 2026-09-25 against the local `dev` checkout, starting at
`84861a54b74c39df1d603c423fa79f0337c17c13`.

## Cause

`http://data.gdeltproject.org/gdeltv2/lastupdate.txt` returns HTTP 301 to
HTTPS. TLS-verified HTTPS requests succeed. Both English and translation
master lists still contain HTTP archive URLs, as do the VGKG and TV-GKG
last-update manifests. Master-list probes used small Range requests and
received 206; they did not download the entire lists.

Standalone `FileSource` and caller-injected default HTTPX clients do not
follow redirects. Their `raise_for_status()` therefore converts the 301 into
`APIUnavailableError`. The unified client already follows redirects, so the
symptom depends on how callers construct the library.

The [2017 HTTPS announcement](https://blog.gdeltproject.org/https-now-available-for-selected-gdelt-apis-and-services/)
explicitly excluded the data CDN at publication time. That historical
limitation no longer describes the live data host.

## Implemented fix

- Use HTTPS for master/translation/last-update lists and generated v2/v3
  data URLs, including VGKG, TV-GKG, TV NGrams, and Radio NGrams.
- Normalize the exact legacy `http://data.gdeltproject.org/` prefix when
  parsing master-list rows and before file cache lookup or download. Both
  raw URL rows and size/hash/URL rows are supported, including cached lists.
- Apply the same normalization before Radio NGrams inventory filtering in
  both date-range and latest-data paths; validate HTTPS after normalization.
- Update lookup help links, the direct HTTPX integration discovery harness,
  and current file-source documentation.

Canonicalizing at the download boundary also supports previously persisted
HTTP URLs supplied by ETL callers. New HTTP and HTTPS requests share the
HTTPS cache key. Old HTTP-keyed cache entries are not migrated and may be
downloaded again. Other hosts and URL schemes are unchanged. TLS verification,
client ownership, public signatures, and caller redirect policy are unchanged.

This avoids an additional redirect request for every file without requiring
callers to enable redirects or broadening the set of redirect destinations.

## Validation

A deterministic HTTPX MockTransport reproduction returned 301 for HTTP and
200 for HTTPS. Before the fix, the manifest request failed with
`APIUnavailableError`. The regression now retrieves both manifests, upgrades
legacy links, downloads and extracts a ZIP, and reuses the HTTPS cache with
redirect following disabled. Additional cases preserve unrelated hosts and
cover mixed HTTP/HTTPS radio inventories.

The real patched `FileSource` downloaded the current last-update manifest
from a caller-supplied legacy HTTP URL and extracted all three listed archives.
This passed using both its owned client and an injected client, each with
redirects disabled. At the sampled `20260925211500` interval:

| Archive | Extracted bytes | Columns in first row |
| --- | ---: | ---: |
| Events | 397,419 | 61 |
| Mentions | 715,228 | 16 |
| GKG | 16,899,725 | 27 |

The four live schema-discovery tests passed (VGKG, TV-GKG, TV NGrams,
Radio NGrams; 5.64 seconds, no skips). The existing live FileSource test
`tests/test_runner.py` also passed with network access (3.82 seconds).
These verify retrieval and decompression, not all endpoint model conversions.

Focused source and broadcast endpoint tests: 112 passed. The initial offline
coverage run passed 1,719 tests. The URL normalization helper has 100% coverage
in its focused regression run.

Release preparation also resolved the pre-existing current-Ruff failures:

- Make the nested actor constructor keyword-only and name both actors' arguments
  (PLR0917), preserving the resulting records.
- Remove the obsolete BLE001 suppression (RUF100), preserving the parser's
  warning severity, traceback logging, and skip-and-continue behavior.
- Format Python examples in 24 tracked Markdown files, as required by Ruff
  0.16.9. Unrelated untracked notes and existing user edits are excluded from
  the release candidate.

No lint rules were disabled. Actor and parser regression checks passed 83 tests.
The release candidate is validated in a clean snapshot because the original
checkout contains unrelated untracked files that Ruff also discovers.

Final `make ci` passed on the release candidate: Ruff lint and format,
Mypy, and 1,720 tests with 84.81% coverage (47 integration tests deselected).
This includes the existing live FileSource smoke test. `uv build` produced
both the 0.1.12 wheel and source distribution successfully. The four explicit
live integration tests described above were run separately.

The source review checked all production HTTP literals and both radio
inventory paths. The autoreview command (`autoreview --mode local --engine
codex`) could not invoke its reviewer because TruffleHog is not installed;
no automated review pass is claimed.

## Separate service findings

Every configured REST API base URL already uses HTTPS. The following direct
HTTPS probes describe availability at the time of testing, not a guarantee
of complete result coverage or freshness:

| Service | Live result |
| --- | --- |
| DOC | 429 on initial request and a later isolated retry after cooldown |
| GEO | 404, including the exact `query=trump` example from its official documentation |
| Context | 200 with an empty JSON object for the sampled query |
| TV | 200 JSON with empty clips when the required station filter was supplied |
| TVAI | 200 JSON with a clip for `ocr:"climate" station:CNN`; plain keywords were rejected by the service |
| TVV | 301 to `visualexplorer.gdeltproject.org/tvv`, then 200 JSON when followed |
| LowerThird | 404 on both initial and station-specific queries |
| GKG GeoJSON | 200 with an empty GeoJSON FeatureCollection |

The GEO URL matches its [official documentation](https://blog.gdeltproject.org/gdelt-geo-2-0-api-debuts/).
No verified replacement for GEO or LowerThird was identified. The existing
REST client already follows TVV's redirect. Changing data URL schemes cannot
repair upstream 404s, remove rate limits, or establish dataset freshness.
BigQuery was not exercised: it uses the Google client rather than this CDN.

VGKG and TV-GKG HTTPS manifests are accessible but advertise files dated
2024-12-01 and 2023-03-24 respectively. A successful HTTPS response does not
establish that these datasets are still updating.

## ETL rollout

The patch version is 0.1.12; version 0.1.11 already exists on the remote release
branch. Package metadata, runtime version, lockfile, Commitizen version, and
release manifest are synchronized. The ETL deployment and queue were not
modified or remeasured. To consume the fix, update the ETL dependency to the
approved library revision, rebuild/redeploy, and
verify the version actually imported by the running container. Confirm a new
raw ingestion run succeeds before treating the incident as recovered.
Any stale concurrency admission state needs a separate live Dagster diagnosis;
the library patch does not release slots or drain queued runs.

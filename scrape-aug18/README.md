# 2026-08-18 API docs housekeeping scrape

Fresh scrape of the Smarkets trading OpenAPI spec, compared against baselines. See CHANGELOG-2026-08-18.md.

- live_full.json     — `/v0/control/openapi/`   (360 paths, whole API incl. web/app)
- live_trading.json  — `/v0/control/openapi/?tags=trading_api` (18 paths — the support-relevant surface)
- smarkets_openapi.json refreshed in workspace root + openapi/ (both = live_trading.json content)

Diff method: JSON path/method/schema enum comparison, reordering-filtered. Timestamps ignored.
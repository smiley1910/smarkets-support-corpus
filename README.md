# Smarkets API Support Workspace

> **Agent reference: [HERMES_REFERENCE.md](HERMES_REFERENCE.md)** — structure, domain mapping, operational notes.
> This file has detailed source pages, key facts, and test script usage for human reference.

Workspace for Smarkets API support emails. All documentation sourced from Smarkets help centre and OpenAPI spec.

## Structure

```
smarkets-api-support/
  docs/
    smarkets_api_knowledge_base.md    -- Comprehensive documentation from help.smarkets.com
    api_endpoints_reference.md        -- All 21 endpoints extracted from OpenAPI spec
    quick_reference_cheatsheet.md     -- One-page quick reference for daily use
    request_response_schemas.md       -- Detailed request/response schemas (order creation etc.)
  openapi/
    smarkets_openapi.json             -- Raw OpenAPI v3 spec (190KB)
  troubleshooting/
    common_api_issues.md              -- Troubleshooting guide for common problems
  scripts/
    smarkets_api_test.py              -- Quick connectivity/API test script
```

## Source Pages (The Bible)

These are the official Smarkets documentation pages we use as sole reference:

1. **Main API Resources Hub**
   https://help.smarkets.com/hc/en-gb/articles/34720906181021-Smarkets-API-Documentation-Resources

2. **API Access, Integration & T&Cs**
   https://help.smarkets.com/hc/en-gb/articles/34697834941085-Smarkets-API-Access-Integration-T-Cs

3. **API Documentation Portal (Swagger)**
   https://docs.smarkets.com/

4. **Raw OpenAPI Spec**
   https://api.smarkets.com/v0/control/openapi/?tags=trading_api

5. **API Request Form**
   https://support.smarkets.com/p/6MLL-PL7/api-request-form

## Key Facts

- API Base: https://api.smarkets.com
- Auth: Session-Token via Authorization header
- Setup fee: GBP150 (refundable within 60 days)
- API customers: ineligible for affiliate/0% commission offers
- Scraping/browser impersonation/reverse engineering: strictly prohibited
- Rate limits: pre-approved per account
- 60-day compliance review for all new API accounts
- Contact: api@smarkets.com

## Using the Test Script

```bash
cd scripts/
python3 smarkets_api_test.py --email user@example.com --password yourpass
```

Runs: connection check, public endpoints, login, authenticated endpoints.

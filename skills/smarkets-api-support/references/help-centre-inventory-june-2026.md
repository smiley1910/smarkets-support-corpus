# Help Centre Inventory — June 2026

> **Scraped:** 2026-06-29 via Jina AI reader (`r.jina.ai`) and browser_navigate
> **Related:** SKILL.md → "Operational Constraints" (Cloudflare blocking note)

## Overview

Two Zendesk-based help centres serve Smarkets products:

| Help Centre | URL | Categories | Articles (en-gb) | Locales |
|-------------|-----|-----------|-------------------|---------|
| Smarkets | help.smarkets.com | 12 | ~170 | en-gb, en-se (English/Sweden), sv (Swedish) |
| SBK | help.getsbk.com | 10 | ~131 | en-gb, en-id (Indonesia), en-in (India), en-us (United States), sv-se (Sweden) |
| **Combined** | | **22** | **~300** | **5 unique locales** |

## Access Method

- **Article pages** (`/articles/`): Jina reader (`https://r.jina.ai/URL`) works reliably — bypasses Cloudflare, returns clean markdown. Proven on both help.smarkets.com and help.getsbk.com article pages.
- **Category index pages** (`/categories/`): Jina reader works on help.smarkets.com but returns 404 on help.getsbk.com.
- **SBK main page** (`help.getsbk.com/hc/en-gb`): Jina only returns "Recent activity" section, not the category navigation. Use `browser_navigate` to see the full category listing.
- **Section pages** (`/sections/`): Jina reader works on both help centres — returns full article listings.

## Smarkets Help Centre (help.smarkets.com)

### Categories and Article Counts

| Category | ID | Sections | Articles |
|----------|----|---------|----------|
| Education | 360001487832 | Esports, American football, Politics, Matched betting, Bet types (15), Golf, +more | ~30+ |
| Calculators | 360001480311 | Calculators | 6 |
| Betting on Smarkets | 360001487852 | Smarkets API (2), Technical (5), Betting FAQs (8), Commission (3), Exchange betting (6) | 24 |
| Bonus & Promotions | 360001480331 | Other Promotions (1), Welcome bonus (5) | 6 |
| Your Account | 360001480351 | Data protection (3), Settings (9), Account (8), Your bets (3) | 23 |
| Account Verification | 360001480371 | Account security (2), Verifying account (7) | 9 |
| Payments | 360001487872 | Currency (2), Payment FAQs (4), Withdrawals (6), Deposits (6), Payment methods (6) | 24 |
| Source of Funds & Wealth | 16426956148893 | Source of Funds & Wealth Checks | 6 |
| Safer Gambling | 360001480391 | Recognising a problem (2), Toolkit (6), Help & support (2) | 10 |
| Betting Rules | 360001480411 | Erroneous Bets (1), Sports specific (25), General (1) | 27 |
| Terms & Conditions | 360001480431 | Trust Deed (1), T&Cs (1) | 2 |
| Contact Us | 360001480451 | Complaints (1), Contact methods (1) | 2 |

### Sports-Specific Rules (25 articles)

Articles 12–36, each a separate help page:

12. Football, 13. Horse Racing, 14. Golf, 15. Cricket, 16. Tennis, 17. Basketball, 18. Rugby Union & League, 19. Baseball, 20. American Football, 21. Motorsports, 22. Ice Hockey, 23. Boxing, 24. MMA, 25. Cycling, 26. Athletics, 27. Swimming, 28. Snooker and Pool, 29. Darts, 30. Politics, 31. Australian Football, 32. Esports, 33. Greyhound, 34. Table Tennis, 35. Fantasy Football, 36. Gaelic Games

### API Help Articles (in Betting on Smarkets category)

- Smarkets API Documentation & Resources (article 34720906181021)
- Smarkets API: Access, Integration & T&Cs (article 34697834941085)

These are help-centre-level articles, separate from the OpenAPI spec and workspace docs already captured.

## SBK Help Centre (help.getsbk.com)

### Categories and Article Counts

| Category | ID | Sections | Articles |
|----------|----|---------|----------|
| Bonus & Promotions | 360000599798 | Promo balance (3), Welcome bonus (5), Other promos (6+) | 14+ |
| Your Account | 360001956052 | Your bets (1), Account (6), Settings (6), Data protection (2) | 15 |
| Account Verification | 360001956072 | Verifying account (5), Source of Funds (5), Account security (2) | 12 |
| Contact Us | 360001956132 | Contact methods (1), Complaints (1) | 2 |
| Payments | 360001955952 | Payment methods (3), Deposits (2), Withdrawals (6), Payment FAQs (4), Currency (2) | 17 |
| Safer Gambling | 360001955892 | Recognising problem (2), Toolkit (5), Help & support (2) | 9 |
| Terms & Conditions | 360001955872 | T&Cs (2), Social code (1), Promo T&Cs (3) | 6 |
| Betting Rules | 360001955832 | General (1), Sport specific (24), Erroneous Bets (1) | 26 |
| General | 360001953912 | Esports (4) | 4 |
| Using SBK | 360000253517 | SBK betting (6), Features (6), Technical (4) | 16 |

### SBK Sports-Specific Rules (24 articles)

Same numbering as Smarkets (12–35) but NO Fantasy Football article (Smarkets has 25, SBK has 24).

### SBK-Specific Product Articles (not in Smarkets)

- Cash out on SBK
- Full Cover Bet Types
- Multiples on SBK
- Minimum and maximum stakes
- Reduction factor explanation
- SBK Bet Feed
- Fresh Legs on SBK
- SBK Best Price
- Save my Bet (World Cup feature)
- Live Activity

## Regional Differences (Expected)

Most articles will be identical across English locales with locale-specific differences:
- **Payment methods:** en-gb may list Visa/Trustly/PayPal; en-us may list different processors
- **Welcome bonus amounts:** UK = Bet £20 get £50; Ireland/Malta = Bet €10 get €50
- **Support organisations:** UK lists GamCare/Gambling Commission; other locales list local equivalents
- **Currency:** GBP (en-gb), EUR (en-se/sv-se), IDR (en-id), INR (en-in), USD (en-us)

Swedish locales (sv, sv-se) may have actual translated content — worth checking a sample article to confirm.

## What's Already Captured in Workspace

The workspace at `~/smarkets-api-support/` has:
- ✅ OpenAPI spec (190KB, 21 endpoints)
- ✅ API knowledge base, endpoints reference, schemas, cheatsheet
- ✅ Training materials (confluence_draft_v2.md, customer_faq.md, pattern_matching_guide.md)
- ✅ 20+ reference files covering specific topics
- ❌ Individual help centre articles (not scraped — only compiled summaries exist)
- ❌ SBK-specific product articles (none captured)
- ❌ Sports settlement rules articles (not individually scraped)
- ❌ Regional variant articles

## Scraping Plan

1. Scrape all en-gb articles for both help centres (~300 articles) via Jina reader
2. Scrape all 49 sports settlement rules (25 Smarkets + 24 SBK)
3. Build searchable index (title, URL, region, product, category, keywords)
4. Build RAG context chunks per topic for the umans-flash routing system
5. Cross-check regional differences for key articles (payments, welcome bonus, safer gambling)
6. Test umans-flash with full RAG context to verify accuracy improvement

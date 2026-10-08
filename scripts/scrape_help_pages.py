#!/usr/bin/env python3
"""
Scrape all Smarkets + SBK help centre articles via Jina reader.
Saves to ~/smarkets-api-support/help-pages/{product}/{locale}/
Builds index.json with all article metadata.
"""

import urllib.request
import re
import json
import os
import time
import sys

BASE_DIR = os.path.expanduser("~/smarkets-api-support")
JINA_PREFIX = "https://r.jina.ai/"

# Category URLs for both products
SMARKETS_CATEGORIES = [
    ("Education", "https://help.smarkets.com/hc/en-gb/categories/360001487832"),
    ("Calculators", "https://help.smarkets.com/hc/en-gb/categories/360001480311"),
    ("Betting on Smarkets", "https://help.smarkets.com/hc/en-gb/categories/360001487852"),
    ("Bonus & Promotions", "https://help.smarkets.com/hc/en-gb/categories/360001480331"),
    ("Your Account", "https://help.smarkets.com/hc/en-gb/categories/360001480351"),
    ("Account Verification", "https://help.smarkets.com/hc/en-gb/categories/360001480371"),
    ("Payments", "https://help.smarkets.com/hc/en-gb/categories/360001487872"),
    ("Source of Funds & Wealth", "https://help.smarkets.com/hc/en-gb/categories/16426956148893"),
    ("Safer Gambling", "https://help.smarkets.com/hc/en-gb/categories/360001480391"),
    ("Betting Rules", "https://help.smarkets.com/hc/en-gb/categories/360001480411"),
    ("Terms & Conditions", "https://help.smarkets.com/hc/en-gb/categories/360001480431"),
    ("Contact Us", "https://help.smarkets.com/hc/en-gb/categories/360001480451"),
]

SBK_CATEGORIES = [
    ("Bonus & Promotions", "https://help.getsbk.com/hc/en-gb/categories/360000599798-Bonus-Promotions"),
    ("Your Account", "https://help.getsbk.com/hc/en-gb/categories/360001956052-Your-Account"),
    ("Account Verification", "https://help.getsbk.com/hc/en-gb/categories/360001956072-Account-Verification"),
    ("Contact Us", "https://help.getsbk.com/hc/en-gb/categories/360001956132-Contact-Us"),
    ("Payments", "https://help.getsbk.com/hc/en-gb/categories/360001955952-Payments"),
    ("Safer Gambling", "https://help.getsbk.com/hc/en-gb/categories/360001955892-Safer-Gambling"),
    ("Terms & Conditions", "https://help.getsbk.com/hc/en-gb/categories/360001955872-Terms-Conditions"),
    ("Betting Rules", "https://help.getsbk.com/hc/en-gb/categories/360001955832-Betting-Rules"),
    ("General", "https://help.getsbk.com/hc/en-gb/categories/360001953912-General"),
    ("Using SBK", "https://help.getsbk.com/hc/en-gb/categories/360000253517-Using-SBK"),
]


def fetch_url(url, retries=2):
    """Fetch URL via urllib, return text or None."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                print(f"    FETCH ERROR ({url}): {e}")
                return None


def jina_fetch(url):
    """Fetch via Jina reader, return markdown text."""
    return fetch_url(JINA_PREFIX + url)


def extract_article_urls(markdown, base_domain):
    """Extract article URLs from category/section page markdown."""
    # Match patterns like: (https://help.smarkets.com/hc/en-gb/articles/XXXXX-slug)
    pattern = rf"https://{re.escape(base_domain)}/hc/en-gb/articles/(\d+)-([^\)]+)"
    matches = re.findall(pattern, markdown)
    seen = set()
    results = []
    for art_id, slug in matches:
        if art_id not in seen:
            seen.add(art_id)
            results.append((art_id, slug))
    return results


def extract_section_urls(markdown, base_domain):
    """Extract section URLs from category page markdown."""
    pattern = rf"https://{re.escape(base_domain)}/hc/en-gb/sections/(\d+)-([^\)]+)"
    matches = re.findall(pattern, markdown)
    seen = set()
    results = []
    for sec_id, slug in matches:
        if sec_id not in seen:
            seen.add(sec_id)
            results.append((sec_id, slug))
    return results


def slug_to_filename(slug):
    """Convert URL slug to filename."""
    # Take the slug part, replace dashes with underscores, limit length
    name = slug.split("?")[0].rstrip(")")
    name = name.replace("-", "_")[:80]
    return name


def scrape_product(product_name, categories, base_domain, output_dir):
    """Scrape all articles for a product (Smarkets or SBK)."""
    os.makedirs(output_dir, exist_ok=True)
    
    all_articles = {}  # art_id -> {url, slug, category, section, title}
    
    # Phase 1: Fetch all category pages, extract sections
    print(f"\n{'='*60}")
    print(f"Phase 1: Fetching {product_name} category pages")
    print(f"{'='*60}")
    
    sections = []  # [(section_id, section_slug, category_name)]
    for cat_name, cat_url in categories:
        print(f"  Category: {cat_name}")
        markdown = jina_fetch(cat_url)
        if not markdown:
            print(f"    ERROR: Failed to fetch category page")
            continue
        
        # Extract sections
        sec_urls = extract_section_urls(markdown, base_domain)
        for sec_id, sec_slug in sec_urls:
            sections.append((sec_id, sec_slug, cat_name))
        
        # Also extract articles directly visible on the category page
        art_urls = extract_article_urls(markdown, base_domain)
        for art_id, slug in art_urls:
            if art_id not in all_articles:
                all_articles[art_id] = {
                    "slug": slug,
                    "category": cat_name,
                    "section": None,
                    "product": product_name,
                    "region": "en-gb",
                    "url": f"https://{base_domain}/hc/en-gb/articles/{art_id}-{slug}",
                }
        
        time.sleep(0.3)
    
    print(f"\n  Found {len(sections)} sections, {len(all_articles)} articles from category pages")
    
    # Phase 2: Fetch all section pages, extract articles
    print(f"\n{'='*60}")
    print(f"Phase 2: Fetching {product_name} section pages ({len(sections)})")
    print(f"{'='*60}")
    
    for sec_id, sec_slug, cat_name in sections:
        sec_url = f"https://{base_domain}/hc/en-gb/sections/{sec_id}-{sec_slug}"
        print(f"  Section: {sec_slug[:50]}")
        markdown = jina_fetch(sec_url)
        if not markdown:
            print(f"    ERROR: Failed to fetch section page")
            continue
        
        art_urls = extract_article_urls(markdown, base_domain)
        for art_id, slug in art_urls:
            if art_id not in all_articles:
                all_articles[art_id] = {
                    "slug": slug,
                    "category": cat_name,
                    "section": sec_slug,
                    "product": product_name,
                    "region": "en-gb",
                    "url": f"https://{base_domain}/hc/en-gb/articles/{art_id}-{slug}",
                }
            else:
                # Update section if not set
                if not all_articles[art_id].get("section"):
                    all_articles[art_id]["section"] = sec_slug
        
        time.sleep(0.3)
    
    print(f"\n  Total unique articles found: {len(all_articles)}")
    
    # Phase 3: Scrape each article
    print(f"\n{'='*60}")
    print(f"Phase 3: Scraping {len(all_articles)} {product_name} articles")
    print(f"{'='*60}")
    
    success = 0
    failed = 0
    errors = []
    
    for i, (art_id, meta) in enumerate(sorted(all_articles.items())):
        filename = f"{art_id}_{slug_to_filename(meta['slug'])}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Skip if already scraped
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            success += 1
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(all_articles)}] Cached: {filename[:60]}")
            continue
        
        print(f"  [{i+1}/{len(all_articles)}] Scraping: {filename[:60]}")
        markdown = jina_fetch(meta["url"])
        
        if not markdown or len(markdown) < 50:
            print(f"    FAILED: empty response")
            failed += 1
            errors.append({"id": art_id, "url": meta["url"], "error": "empty response"})
            time.sleep(0.3)
            continue
        
        # Extract title from first line
        title_match = re.match(r"Title:\s*(.+)", markdown)
        title = title_match.group(1).strip() if title_match else meta["slug"].replace("-", " ").title()
        meta["title"] = title
        meta["filename"] = filename
        
        # Add metadata header to the file
        header = f"""<!-- 
id: {art_id}
title: {title}
product: {product_name}
region: en-gb
category: {meta.get('category', '')}
section: {meta.get('section', '')}
url: {meta['url']}
scraped: {time.strftime('%Y-%m-%d')}
-->
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + markdown)
        
        success += 1
        time.sleep(0.3)
    
    print(f"\n  Results: {success} success, {failed} failed out of {len(all_articles)}")
    if errors:
        print(f"  Errors: {json.dumps(errors[:5], indent=2)}")
    
    return all_articles, errors


def scrape_sports_rules():
    """Scrape all sports settlement rules for both products."""
    print(f"\n{'='*60}")
    print("Phase 4: Scraping sports settlement rules")
    print(f"{'='*60}")
    
    # Smarkets sports rules (articles 12-36, 25 total)
    smarkets_sports = [
        (12, "Football", "210005425-12-Football-rules"),
        (13, "Horse Racing", "209277269-13-Horse-Racing-rules"),
        (14, "Golf", "209277289-14-Golf-rules"),
        (15, "Cricket", "209277309-15-Cricket-rules"),
        (16, "Tennis", "209277329-16-Tennis-rules"),
        (17, "Basketball", "209277349-17-Basketball-rules"),
        (18, "Rugby Union and Rugby League", "209277369-18-Rugby-Union-and-Rugby-League-rules"),
        (19, "Baseball", "210004965-19-Baseball-rules"),
        (20, "American Football", "210005565-20-American-Football-rules"),
        (21, "Motorsports", "210005585-21-Motorsports-rules"),
        (22, "Ice Hockey", "210005645-22-Ice-Hockey-rules"),
        (23, "Boxing", "210005665-23-Boxing-rules"),
        (24, "MMA", "209277429-24-MMA-rules"),
        (25, "Cycling", "209277449-25-Cycling-rules"),
        (26, "Athletics", "209277469-26-Athletics-rules"),
        (27, "Swimming", "209277509-27-Swimming-rules"),
        (28, "Snooker and Pool", "115000626289-28-Snooker-and-Pool-rules"),
        (29, "Darts", "115000638205-29-Darts-rules"),
        (30, "Politics", "115000626649-30-Politics-rules"),
        (31, "Australian Football", "360006799777-31-Australian-Football-rules"),
        (32, "Esports", "360006824657-32-Esports-rules"),
        (33, "Greyhound", "360007024158-33-Greyhound-rules"),
        (34, "Table Tennis", "360007022497-34-Table-Tennis-rules"),
        (35, "Fantasy Football", "12807188772893-35-Fantasy-football-rules"),
        (36, "Gaelic Games", "20292956069277-36-Gaelic-Games-rules"),
    ]
    
    # SBK sports rules (articles 12-35, 24 total — no Fantasy Football)
    sbk_sports = [
        (12, "Football", "360002159437-12-Football-rules"),
        (13, "Horse Racing", "360002159497-13-Horse-Racing-rules"),
        (14, "Golf", "360002166058-14-Golf-rules"),
        (15, "Cricket", "360002166078-15-Cricket-rules"),
        (16, "Tennis", "360002159617-16-Tennis-rules"),
        (17, "Basketball", "360002159637-17-Basketball-rules"),
        (18, "Rugby Union and Rugby League", "360002166118-18-Rugby-Union-and-Rugby-League-rules"),
        (19, "Baseball", "360002159677-19-Baseball-rules"),
        (20, "American Football", "360002166158-20-American-Football-rules"),
        (21, "Motorsports", "360002159737-21-Motorsports-rules"),
        (22, "Ice Hockey", "360002166178-22-Ice-Hockey-rules"),
        (23, "Boxing", "360002159757-23-Boxing-rules"),
        (24, "MMA", "360002159777-24-MMA-rules"),
        (25, "Cycling", "360002166198-25-Cycling-rules"),
        (26, "Athletics", "360002166258-26-Athletics-rules"),
        (27, "Swimming", "360002166298-27-Swimming-rules"),
        (28, "Snooker and Pool", "360002159877-28-Snooker-and-Pool-rules"),
        (29, "Darts", "360002159917-29-Darts-rules"),
        (30, "Politics", "360002166278-30-Politics-rules"),
        (31, "Australian Football", "360006849198-31-Australian-Football-rules"),
        (32, "Esports", "360006870078-32-Esports-rules"),
        (33, "Greyhound", "360006979577-33-Greyhound-rules"),
        (34, "Table Tennis", "360007070978-34-Table-Tennis-rules"),
        (35, "Gaelic Games", "20293217457181-35-Gaelic-Games-rules"),
    ]
    
    results = {}
    
    # Scrape Smarkets sports rules
    sm_dir = os.path.join(BASE_DIR, "betting-rules", "smarkets")
    os.makedirs(sm_dir, exist_ok=True)
    
    print("\n  Smarkets sports rules (25):")
    for num, sport, slug in smarkets_sports:
        filename = f"{num:02d}_{sport.lower().replace(' ', '_')}.md"
        filepath = os.path.join(sm_dir, filename)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            print(f"    Cached: {filename}")
            results[f"smarkets_{num}"] = {"sport": sport, "filename": filename, "status": "cached"}
            continue
        
        url = f"https://help.smarkets.com/hc/en-gb/articles/{slug}"
        print(f"    Scraping: {sport}")
        markdown = jina_fetch(url)
        
        if markdown and len(markdown) > 50:
            header = f"""<!-- 
sport: {sport}
product: smarkets
article_num: {num}
url: {url}
scraped: {time.strftime('%Y-%m-%d')}
-->
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + markdown)
            results[f"smarkets_{num}"] = {"sport": sport, "filename": filename, "status": "scraped"}
        else:
            print(f"      FAILED")
            results[f"smarkets_{num}"] = {"sport": sport, "filename": filename, "status": "failed"}
        
        time.sleep(0.3)
    
    # Scrape SBK sports rules
    sbk_dir = os.path.join(BASE_DIR, "betting-rules", "sbk")
    os.makedirs(sbk_dir, exist_ok=True)
    
    print("\n  SBK sports rules (24):")
    for num, sport, slug in sbk_sports:
        filename = f"{num:02d}_{sport.lower().replace(' ', '_')}.md"
        filepath = os.path.join(sbk_dir, filename)
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            print(f"    Cached: {filename}")
            results[f"sbk_{num}"] = {"sport": sport, "filename": filename, "status": "cached"}
            continue
        
        url = f"https://help.getsbk.com/hc/en-gb/articles/{slug}"
        print(f"    Scraping: {sport}")
        markdown = jina_fetch(url)
        
        if markdown and len(markdown) > 50:
            header = f"""<!-- 
sport: {sport}
product: sbk
article_num: {num}
url: {url}
scraped: {time.strftime('%Y-%m-%d')}
-->
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + markdown)
            results[f"sbk_{num}"] = {"sport": sport, "filename": filename, "status": "scraped"}
        else:
            print(f"      FAILED")
            results[f"sbk_{num}"] = {"sport": sport, "filename": filename, "status": "failed"}
        
        time.sleep(0.3)
    
    return results


def scrape_general_rules():
    """Scrape general betting rules for both products."""
    print(f"\n{'='*60}")
    print("Phase 5: Scraping general betting rules")
    print(f"{'='*60}")
    
    rules = [
        ("smarkets", "general_rules_1-11", "https://help.smarkets.com/hc/en-gb/articles/212183509-1-11-General-Smarkets-betting-rules"),
        ("smarkets", "erroneous_bets", "https://help.smarkets.com/hc/en-gb/articles/212819049-Clearly-Erroneous-Bets-Policy"),
        ("sbk", "general_rules_1-11", "https://help.getsbk.com/hc/en-gb/articles/360002159057-1-11-General-SBK-betting-rules"),
        ("sbk", "erroneous_bets", "https://help.getsbk.com/hc/en-gb/articles/360030909571-Clearly-Erroneous-Bets-Policy"),
    ]
    
    results = {}
    for product, name, url in rules:
        filepath = os.path.join(BASE_DIR, "betting-rules", product, f"{name}.md")
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            print(f"  Cached: {product}/{name}")
            results[f"{product}_{name}"] = "cached"
            continue
        
        print(f"  Scraping: {product}/{name}")
        markdown = jina_fetch(url)
        
        if markdown and len(markdown) > 50:
            header = f"""<!-- 
product: {product}
type: {name}
url: {url}
scraped: {time.strftime('%Y-%m-%d')}
-->
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + markdown)
            results[f"{product}_{name}"] = "scraped"
        else:
            print(f"    FAILED")
            results[f"{product}_{name}"] = "failed"
        
        time.sleep(0.3)
    
    return results


def build_index(smarkets_articles, sbk_articles, sports_results, general_results):
    """Build a searchable index of all articles."""
    index = {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "products": {
            "smarkets": {
                "locales": ["en-gb", "en-se", "sv"],
                "article_count": len(smarkets_articles),
                "articles": [],
            },
            "sbk": {
                "locales": ["en-gb", "en-id", "en-in", "en-us", "sv-se"],
                "article_count": len(sbk_articles),
                "articles": [],
            },
        },
        "betting_rules": sports_results,
        "general_rules": general_results,
    }
    
    for art_id, meta in sorted(smarkets_articles.items()):
        index["products"]["smarkets"]["articles"].append({
            "id": art_id,
            "title": meta.get("title", ""),
            "category": meta.get("category", ""),
            "section": meta.get("section", ""),
            "filename": meta.get("filename", ""),
            "url": meta["url"],
        })
    
    for art_id, meta in sorted(sbk_articles.items()):
        index["products"]["sbk"]["articles"].append({
            "id": art_id,
            "title": meta.get("title", ""),
            "category": meta.get("category", ""),
            "section": meta.get("section", ""),
            "filename": meta.get("filename", ""),
            "url": meta["url"],
        })
    
    index_path = os.path.join(BASE_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\nIndex written to {index_path}")
    return index


def main():
    print(f"Starting help centre scrape at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output: {BASE_DIR}/help-pages/")
    
    # Scrape Smarkets
    smarkets_articles, sm_errors = scrape_product(
        "Smarkets",
        SMARKETS_CATEGORIES,
        "help.smarkets.com",
        os.path.join(BASE_DIR, "help-pages", "smarkets", "en-gb"),
    )
    
    # Scrape SBK
    sbk_articles, sbk_errors = scrape_product(
        "SBK",
        SBK_CATEGORIES,
        "help.getsbk.com",
        os.path.join(BASE_DIR, "help-pages", "sbk", "en-gb"),
    )
    
    # Scrape sports rules
    sports_results = scrape_sports_rules()
    
    # Scrape general rules
    general_results = scrape_general_rules()
    
    # Build index
    index = build_index(smarkets_articles, sbk_articles, sports_results, general_results)
    
    # Summary
    print(f"\n{'='*60}")
    print("SCRAPE COMPLETE")
    print(f"{'='*60}")
    print(f"Smarkets articles: {len(smarkets_articles)} ({len(sm_errors)} errors)")
    print(f"SBK articles: {len(sbk_articles)} ({len(sbk_errors)} errors)")
    print(f"Sports rules: {sum(1 for v in sports_results.values() if v['status'] != 'failed')}/{len(sports_results)} scraped")
    print(f"General rules: {sum(1 for v in general_results.values() if v == 'scraped' or v == 'cached')}/{len(general_results)} scraped")
    print(f"Index: {BASE_DIR}/index.json")
    print(f"\nCompleted at {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()

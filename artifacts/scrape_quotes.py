import os
import json
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://quotes.toscrape.com/page/{page}/"
OUTPUT_PATH = "/workspaces/AAWS/artifacts/notebooks/generated/quotes_sample_result.json"
MAX_PAGES = 3

def scrape_quotes():
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"[*] Starting scraper: pages 1 to {MAX_PAGES}")

    for page in range(1, MAX_PAGES + 1):
        url = BASE_URL.format(page=page)
        print(f"[*] Fetching page {page}: {url}")

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] Error fetching {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        quote_cards = soup.select("div.quote")

        if not quote_cards:
            print(f"[!] No quotes found on page {page}. Stopping.")
            break

        print(f"[*] Found {len(quote_cards)} quotes on page {page}")

        for card in quote_cards:
            text_el = card.select_one("span.text")
            author_el = card.select_one("small.author")
            tag_els = card.select("div.tags a.tag")

            text = text_el.get_text(strip=True) if text_el else ""
            author = author_el.get_text(strip=True) if author_el else ""
            tags = [tag.get_text(strip=True) for tag in tag_els]

            results.append({
                "page": page,
                "text": text,
                "author": author,
                "tags": tags
            })

        time.sleep(0.5)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[+] Successfully scraped {len(results)} quotes.")
    print(f"[+] Saved results to {OUTPUT_PATH}")

if __name__ == "__main__":
    scrape_quotes()

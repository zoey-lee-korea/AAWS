import os
import json
import time
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_URL = "http://quotes.toscrape.com/page/{page}/"
OUTPUT_PATH = "/workspaces/AAWS/artifacts/notebooks/generated/quotes_sample_result.json"
MAX_PAGE = 3

def scrape_quotes():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    results = []

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    })

    for page in range(1, MAX_PAGE + 1):
        url = BASE_URL.format(page=page)
        logging.info(f"Scraping page {page}: {url}")

        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        quote_elements = soup.select("div.quote")

        if not quote_elements:
            logging.warning(f"No quotes found on page {page}.")
            break

        logging.info(f"Found {len(quote_elements)} quotes on page {page}.")

        for el in quote_elements:
            text_el = el.select_one("span.text")
            author_el = el.select_one("small.author")
            tag_els = el.select("div.tags a.tag")

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

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logging.info(f"Successfully saved {len(results)} quotes to {OUTPUT_PATH}")
    return len(results)

if __name__ == "__main__":
    count = scrape_quotes()
    print(f"COLLECTION_COMPLETE: {count} items collected.")

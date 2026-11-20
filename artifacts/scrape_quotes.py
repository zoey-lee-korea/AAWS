import asyncio
import json
import os
from collections import Counter
from bs4 import BeautifulSoup
import httpx

PAGES = [
    "http://quotes.toscrape.com/page/1/",
    "http://quotes.toscrape.com/page/2/"
]
OUTPUT_FILE = "artifacts/data/quotes_async.json"

async def fetch_page(client, url):
    resp = await client.get(url, timeout=10.0)
    resp.raise_for_status()
    return resp.text

def parse_quotes(html):
    soup = BeautifulSoup(html, "html.parser")
    quotes_data = []
    quote_elements = soup.select("div.quote")
    for q in quote_elements:
        text_el = q.select_one("span.text")
        author_el = q.select_one("small.author")
        tag_els = q.select("div.tags a.tag")
        
        text = text_el.get_text(strip=True) if text_el else ""
        author = author_el.get_text(strip=True) if author_el else ""
        tags = [t.get_text(strip=True) for t in tag_els]
        
        quotes_data.append({
            "text": text,
            "author": author,
            "tags": tags
        })
    return quotes_data

async def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    all_quotes = []
    
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as client:
        tasks = [fetch_page(client, url) for url in PAGES]
        html_results = await asyncio.gather(*tasks)
        
        for html in html_results:
            quotes = parse_quotes(html)
            all_quotes.extend(quotes)
            
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully scraped {len(all_quotes)} quotes.")
    authors = Counter(q["author"] for q in all_quotes)
    all_tags = Counter(tag for q in all_quotes for tag in q["tags"])
    
    print("\nAuthors summary:")
    for author, count in authors.most_common():
        print(f"  - {author}: {count}")
        
    print("\nTop 10 Tags summary:")
    for tag, count in all_tags.most_common(10):
        print(f"  - {tag}: {count}")

if __name__ == "__main__":
    asyncio.run(main())

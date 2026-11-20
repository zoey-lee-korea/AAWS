import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_quotes():
    urls = [
        "http://quotes.toscrape.com/",
        "http://quotes.toscrape.com/page/2/"
    ]
    
    quotes_data = []
    
    for url in urls:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        quote_elements = soup.select("div.quote")
        for q in quote_elements:
            text_el = q.select_one("span.text")
            author_el = q.select_one("small.author")
            tag_els = q.select("div.tags a.tag")
            
            text = text_el.get_text(strip=True) if text_el else ""
            author = author_el.get_text(strip=True) if author_el else ""
            tags = [tag.get_text(strip=True) for tag in tag_els]
            
            quotes_data.append({
                "text": text,
                "author": author,
                "tags": tags
            })
            
    output_dir = "artifacts/data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "quotes_multiagent.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(quotes_data, f, indent=2, ensure_ascii=False)
        
    print(f"Collected {len(quotes_data)} quotes.")
    authors = set(q["author"] for q in quotes_data)
    print(f"Unique authors: {len(authors)} ({authors})")

if __name__ == "__main__":
    scrape_quotes()

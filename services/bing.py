"""Bing HTML web search provider."""

import requests
from bs4 import BeautifulSoup

BING_SEARCH_URL = "https://www.bing.com/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def bing_search(query, limit=10):
    query = (query or "").strip()
    if not query:
        return []
    try:
        response = requests.get(
            BING_SEARCH_URL,
            params={"q": query},
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select("li.b_algo"):
            link = item.select_one("h2 a")
            if not link:
                continue
            title = link.get_text(" ", strip=True)
            url = link.get("href", "")
            snippet_tag = item.select_one(".b_caption p")
            description = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
            if not title or not url:
                continue
            results.append({
                "title": title,
                "url": url,
                "description": description,
                "snippet": description,
                "source": "Bing",
            })
            if len(results) >= max(1, int(limit)):
                break
        return results
    except Exception as error:
        print(f"[VedFinder] Bing search error: {error}")
        return []


def get_bing_results(query, limit=10):
    return bing_search(query, limit)

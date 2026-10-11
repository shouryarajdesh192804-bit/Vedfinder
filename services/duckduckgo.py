"""DuckDuckGo HTML web search provider."""

import requests
from bs4 import BeautifulSoup

DUCKDUCKGO_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def duckduckgo_search(query, limit=10):
    query = (query or "").strip()
    if not query:
        return []
    try:
        response = requests.post(
            DUCKDUCKGO_URL,
            data={"q": query},
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select(".result"):
            link = item.select_one(".result__title a")
            if not link:
                continue
            title = link.get_text(" ", strip=True)
            url = link.get("href", "")
            snippet_tag = item.select_one(".result__snippet")
            description = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
            if not title or not url:
                continue
            results.append({
                "title": title,
                "url": url,
                "description": description,
                "snippet": description,
                "source": "DuckDuckGo",
            })
            if len(results) >= max(1, int(limit)):
                break
        return results
    except Exception as error:
        print(f"[VedFinder] DuckDuckGo search error: {error}")
        return []


# Compatibility names used by older versions of search_engine.py.
def get_duckduckgo_results(query, limit=10):
    return duckduckgo_search(query, limit)


def search_duckduckgo(query, limit=10):
    return duckduckgo_search(query, limit)

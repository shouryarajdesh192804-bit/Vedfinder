
"""VedFinder Wikipedia knowledge provider."""

import requests

API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "VedFinder/1.0 (educational search application)"
}


def wiki_search(query):
    query = (query or "").strip()

    if not query:
        return {}

    try:
        response = requests.get(
            API_URL,
            params={
                "action": "query",
                "format": "json",
                "prop": "extracts|pageimages|info",
                "exintro": 1,
                "explaintext": 1,
                "pithumbsize": 600,
                "inprop": "url",
                "redirects": 1,
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": 1,
            },
            headers=HEADERS,
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        if not pages:
            print(
                f"[VedFinder] No Wikipedia result for: {query}"
            )
            return {}

        page = next(iter(pages.values()))

        return {
            "title": page.get("title", ""),
            "summary": page.get("extract", ""),
            "image": page.get("thumbnail", {}).get("source", ""),
            "url": page.get("fullurl", ""),
        }

    except (requests.RequestException, ValueError) as error:
        print(
            f"[VedFinder] Wikipedia search error: {error}"
        )
        return {}


def get_wikipedia_summary(query):
    return wiki_search(query)


def wikipedia_search(query):
    return wiki_search(query)
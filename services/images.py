"""VedFinder image search with DuckDuckGo and Bing fallback."""

import requests
import re
from urllib.parse import quote

DDG_HOME = "https://duckduckgo.com/"
DDG_IMAGES = "https://duckduckgo.com/i.js"
BING_IMAGES = "https://www.bing.com/images/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _get_vqd(query):
    response = requests.get(
        DDG_HOME,
        params={"q": query, "ia": "images"},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    patterns = [
        r'vqd=["\']([^"\']+)',
        r'"vqd"\s*:\s*"([^"]+)"',
        r"vqd=([\w-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response.text)
        if match:
            return match.group(1)

    return None


def _valid_url(url):
    return isinstance(url, str) and url.startswith(("https://", "http://"))


def _duckduckgo_search(query, max_results):
    token = _get_vqd(query)

    if not token:
        print("[VedFinder] DuckDuckGo image token unavailable.")
        return []

    response = requests.get(
        DDG_IMAGES,
        params={
            "q": query,
            "vqd": token,
            "o": "json",
            "l": "us-en",
            "f": "",
            "p": "1",
        },
        headers={
            **HEADERS,
            "Referer": DDG_HOME,
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    print(
        "[VedFinder] DuckDuckGo raw image results:",
        len(results),
    )

    output = []
    seen = set()

    for item in results:
        if not isinstance(item, dict):
            continue

        image_url = (
            item.get("image")
            or item.get("imageurl")
            or item.get("image_url")
        )

        thumbnail = (
            item.get("thumbnail")
            or item.get("thumbnail_url")
            or image_url
        )

        page_url = (
            item.get("url")
            or item.get("u")
            or item.get("link")
            or ""
        )

        if not _valid_url(image_url) or image_url in seen:
            continue

        seen.add(image_url)

        output.append({
            "title": item.get("title") or query,
            "image": image_url,
            "thumbnail": thumbnail if _valid_url(thumbnail) else image_url,
            "url": page_url if _valid_url(page_url) else image_url,
        })

        if len(output) >= max_results:
            break

    return output


def _bing_search(query, max_results):
    response = requests.get(
        BING_IMAGES,
        params={
            "q": query,
            "form": "HDRSC2",
            "first": "1",
        },
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    # Bing embeds image metadata in HTML attributes.
    output = []
    seen = set()

    patterns = [
        r'm="(\{&quot;.*?&quot;\})"',
        r'm="(\{.*?\})"',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, response.text):
            raw = match.group(1)

            try:
                import html
                import json

                item = json.loads(html.unescape(raw))
            except (ValueError, TypeError):
                continue

            image_url = (
                item.get("murl")
                or item.get("imgurl")
                or item.get("turl")
            )

            thumbnail = item.get("turl") or image_url
            page_url = item.get("purl") or image_url

            if not _valid_url(image_url) or image_url in seen:
                continue

            seen.add(image_url)

            output.append({
                "title": item.get("t") or query,
                "image": image_url,
                "thumbnail": thumbnail if _valid_url(thumbnail) else image_url,
                "url": page_url if _valid_url(page_url) else image_url,
            })

            if len(output) >= max_results:
                return output

    # Alternative parser for Bing's murl/turl attributes.
    if not output:
        pattern = (
            r'murl&quot;:&quot;(https?://.*?)&quot;.*?'
            r'turl&quot;:&quot;(https?://.*?)&quot;'
        )

        for match in re.finditer(pattern, response.text):
            image_url = match.group(1)
            thumbnail = match.group(2)

            if image_url in seen:
                continue

            seen.add(image_url)
            output.append({
                "title": query,
                "image": image_url,
                "thumbnail": thumbnail,
                "url": image_url,
            })

            if len(output) >= max_results:
                break

    print("[VedFinder] Bing image results:", len(output))
    return output


def image_search(query, max_results=24):
    query = (query or "").strip()

    if not query:
        return []

    max_results = max(1, int(max_results))

    try:
        results = _duckduckgo_search(query, max_results)

        if results:
            print(
                f"[VedFinder] Images for '{query}': "
                f"{len(results)} (DuckDuckGo)"
            )
            return results

    except Exception as error:
        print(f"[VedFinder] DuckDuckGo image error: {error}")

    try:
        results = _bing_search(query, max_results)

        print(
            f"[VedFinder] Images for '{query}': "
            f"{len(results)} (Bing)"
        )
        return results

    except Exception as error:
        print(f"[VedFinder] Bing image error: {error}")

    return []


def get_images(query, max_results=24):
    return image_search(query, max_results)


def search_images(query, max_results=24):
    return image_search(query, max_results)


def duckduckgo_images(query, max_results=24):
    return image_search(query, max_results)
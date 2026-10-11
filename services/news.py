"""Google News RSS search provider."""

import html
import re
import xml.etree.ElementTree as ET

import requests

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*;q=0.8",
}


def _clean_text(value):
    if not value:
        return ""
    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _child_text(element, name):
    child = element.find(name)
    return (child.text or "").strip() if child is not None else ""


def get_news(query, max_results=12):
    query = (query or "").strip()
    if not query:
        return []
    try:
        response = requests.get(
            GOOGLE_NEWS_RSS,
            params={"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        channel = root.find("./channel")
        if channel is None:
            return []

        news = []
        for item in channel.findall("item"):
            title = _child_text(item, "title")
            url = _child_text(item, "link")
            description = _child_text(item, "description")
            published = _child_text(item, "pubDate")
            source = _child_text(item, "source") or "Google News"
            if not title:
                continue
            news.append({
                "title": title,
                "url": url,
                "link": url,
                "source": source,
                "description": _clean_text(description),
                "published": published,
            })
            if len(news) >= max(1, int(max_results)):
                break
        return news
    except ET.ParseError as error:
        print(f"[VedFinder] Google News XML error: {error}")
        return []
    except Exception as error:
        print(f"[VedFinder] News search error: {error}")
        return []


def news_search(query, max_results=12):
    return get_news(query, max_results)


def search_news(query, max_results=12):
    return get_news(query, max_results)


def get_google_news(query, max_results=12):
    return get_news(query, max_results)


def get_news_results(query, max_results=12):
    return get_news(query, max_results)

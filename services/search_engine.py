"""VedFinder search orchestration.

Keeps provider function names compatible with the existing services and
returns the keys expected by the current Flask templates.
"""

from services.bing import bing_search
from services.duckduckgo import duckduckgo_search
from services.images import image_search
from services.news import get_news
from services.videos import get_videos
from services.wikipedia import wiki_search


def _as_list(value, *keys):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, list):
                return candidate
        return []
    if value is None:
        return []
    return [value]


def _safe_call(function, query, default=None, **kwargs):
    try:
        return function(query, **kwargs)
    except TypeError:
        # Some providers only accept the query argument.
        try:
            return function(query)
        except Exception as error:
            print(f"[VedFinder] {function.__name__} failed: {error}")
            return default
    except Exception as error:
        print(f"[VedFinder] {function.__name__} failed: {error}")
        return default


def _knowledge(query):
    item = _safe_call(wiki_search, query)
    if not isinstance(item, dict):
        return None

    summary = item.get("summary") or item.get("description") or ""
    title = item.get("title") or query
    if not title and not summary:
        return None

    return {
        "title": title,
        "summary": summary,
        "description": item.get("description") or summary,
        "image": item.get("image") or item.get("thumbnail") or "",
        "url": item.get("url") or "",
    }


def _normalize_web(items):
    output = []
    for item in _as_list(items, "results", "websites"):
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("name")
        url = item.get("url") or item.get("link")
        if not title or not url:
            continue
        description = item.get("description") or item.get("snippet") or item.get("summary") or ""
        output.append({
            "title": title,
            "url": url,
            "description": description,
            "snippet": description,
            "source": item.get("source") or "Web",
        })
    return output


def _normalize_images(items, query):
    output = []
    for item in _as_list(items, "images", "results"):
        if not isinstance(item, dict):
            continue
        image = item.get("image") or item.get("imageurl") or item.get("image_url") or item.get("thumbnail")
        thumbnail = item.get("thumbnail") or item.get("thumbnail_url") or image
        if not thumbnail:
            continue
        output.append({
            "thumbnail": thumbnail,
            "image": image or thumbnail,
            "url": item.get("url") or item.get("link") or image or thumbnail,
            "title": item.get("title") or item.get("name") or query,
        })
    return output


def _normalize_videos(items):
    output = []
    for item in _as_list(items, "videos", "results"):
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("name") or "Video"
        url = item.get("url") or item.get("link") or ""
        output.append({
            "title": title,
            "url": url,
            "thumbnail": item.get("thumbnail") or item.get("image") or "",
            "channel": item.get("channel") or item.get("source") or "",
            "source": item.get("channel") or item.get("source") or "YouTube",
            "description": item.get("description") or "",
        })
    return output


def _normalize_news(items):
    output = []
    for item in _as_list(items, "news", "results"):
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("name")
        if not title:
            continue
        url = item.get("url") or item.get("link") or "#"
        output.append({
            "title": title,
            "url": url,
            "link": url,
            "source": item.get("source") or item.get("publisher") or "Google News",
            "description": item.get("description") or item.get("summary") or "",
            "published": item.get("published") or item.get("pubDate") or item.get("date") or "",
        })
    return output


def _empty_result(mode):
    return {
        "mode": mode,
        "summary": None,
        "knowledge": None,
        "websites": [],
        "images": [],
        "videos": [],
        "news": [],
        "maps": None,
    }


def search(query, mode="normal"):
    query = (query or "").strip()
    mode = (mode or "normal").strip().lower()
    if mode not in ("normal", "go"):
        mode = "normal"
    if not query:
        return _empty_result(mode)

    knowledge = _knowledge(query)

    # Go mode uses DuckDuckGo only. Normal mode falls back to Bing if needed.
    websites = _safe_call(duckduckgo_search, query, default=[])
    websites = _as_list(websites, "results", "websites")
    if mode == "normal" and not websites:
        websites = _safe_call(bing_search, query, default=[])
    websites = _normalize_web(websites)

    images = _normalize_images(
        _safe_call(image_search, query, default=[], max_results=24), query
    )
    videos = _normalize_videos(
        _safe_call(get_videos, query, default=[], limit=10)
    )
    news = _normalize_news(
        _safe_call(get_news, query, default=[], max_results=12)
    )

    return {
        "mode": mode,
        "summary": knowledge.get("summary") if knowledge else None,
        "knowledge": knowledge,
        "websites": websites,
        "images": images,
        "videos": videos,
        "news": news,
        "maps": None,
    }

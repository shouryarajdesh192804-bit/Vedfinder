# =========================================
# VedFinder V2
# services/fusion.py
# =========================================

def merge_results(bing_results, wiki_result):
    """
    Combine Bing + Wikipedia for the Knowledge section.

    Bing results are preserved even when Wikipedia
    returns nothing.
    """

    if not isinstance(bing_results, list):
        bing_results = []

    if not isinstance(wiki_result, dict):
        wiki_result = {}

    # -----------------------------------------
    # Wikipedia
    # -----------------------------------------

    wiki_title = wiki_result.get("title", "")

    wiki_summary = (
        wiki_result.get("summary")
        or wiki_result.get("description")
        or ""
    )

    wiki_image = wiki_result.get("image", "")

    wiki_url = wiki_result.get("url", "")

    # -----------------------------------------
    # Bing
    # -----------------------------------------

    web_results = []

    for result in bing_results:

        if not isinstance(result, dict):
            continue

        title = (
            result.get("title")
            or ""
        )

        description = (
            result.get("description")
            or result.get("snippet")
            or result.get("summary")
            or ""
        )

        url = (
            result.get("url")
            or result.get("link")
            or ""
        )

        if not title and not description and not url:
            continue

        web_results.append({
            "title": title,
            "description": description,
            "url": url
        })

    # -----------------------------------------
    # Final Knowledge
    # -----------------------------------------

    return {
        "title": wiki_title,

        "summary": wiki_summary,

        "description": wiki_summary,

        "image": wiki_image,

        "url": wiki_url,

        "source": "VedFinder",

        "web_results": web_results,

        "bing_results": web_results,

        "has_wikipedia": bool(
            wiki_title or wiki_summary
        ),

        "has_bing": bool(web_results)
    }
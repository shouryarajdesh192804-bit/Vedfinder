import re


def generate_summary(wiki_result, bing_results):

    if wiki_result is None:
        wiki_result = {}

    if bing_results is None:
        bing_results = []

    paragraphs = []

    wiki_summary = wiki_result.get("summary", "")

    if wiki_summary:

        paragraphs.append(wiki_summary)

    for result in bing_results[:5]:

        text = result.get("description", "").strip()

        if text and text not in paragraphs:

            paragraphs.append(text)

    summary = " ".join(paragraphs)

    summary = re.sub(r"\s+", " ", summary).strip()

    if len(summary) > 1400:

        summary = summary[:1400] + "..."

    return {

        "title": wiki_result.get("title", ""),

        "summary": summary,

        "image": wiki_result.get("image", ""),

        "url": wiki_result.get("url", "")

    }
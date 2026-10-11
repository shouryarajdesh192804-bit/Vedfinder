
"""VedFinder V2 - YouTube video search."""

import os
import requests
from dotenv import load_dotenv

# Load the project's root .env file.
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_FILE, override=False)

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


def get_videos(query, limit=10):
    query = (query or "").strip()

    if not query:
        return []

    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()

    if not api_key:
        print(
            f"[VedFinder] YOUTUBE_API_KEY not found. "
            f"Check {ENV_FILE}"
        )
        return []

    try:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max(1, min(int(limit), 50)),
            "key": api_key,
        }

        response = requests.get(
            YOUTUBE_API_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        videos = []

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})

            if not video_id:
                continue

            thumbnails = snippet.get("thumbnails", {})
            thumbnail = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url")
                or ""
            )

            videos.append({
                "title": snippet.get("title", "YouTube Video"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": thumbnail,
                "channel": snippet.get("channelTitle", "YouTube"),
                "source": "YouTube",
                "description": snippet.get("description", ""),
            })

        print(
            f"[VedFinder] Videos for '{query}': {len(videos)}"
        )
        return videos

    except requests.HTTPError as error:
        # Do not print the request URL: it can contain the API key.
        status = error.response.status_code if error.response is not None else "unknown"
        print(
            f"[VedFinder] YouTube HTTP error ({status}). "
            "Check API key validity, API restrictions and quota."
        )
        return []

    except (requests.RequestException, ValueError) as error:
        print(f"[VedFinder] YouTube request error: {error}")
        return []

    except Exception as error:
        print(f"[VedFinder] Video search error: {error}")
        return []


def search_videos(query, limit=10):
    return get_videos(query, limit)


def video_search(query, limit=10):
    return get_videos(query, limit)
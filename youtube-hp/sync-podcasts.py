from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parent
PAGE_URL = "https://www.youtube.com/@chamberd_piano/podcasts"
HTML_FILE = ROOT / "podcasts-page.html"
OUTPUT_FILE = ROOT / "playlist-data.js"
COVERS_DIR = ROOT / "covers"
ENV_FILES = [ROOT / ".env", ROOT.parent / ".env"]
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3/playlistItems"


def fetch_page() -> str:
    request = urllib.request.Request(
        PAGE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8")
    HTML_FILE.write_text(html, encoding="utf-8")
    return html


def load_env() -> None:
    for env_file in ENV_FILES:
        if not env_file.exists():
            continue

        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def extract_initial_data(html: str) -> dict:
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
    if not match:
        raise SystemExit("ytInitialData was not found on the podcasts page.")
    return json.loads(match.group(1))


def metadata_text(lockup: dict) -> str:
    rows = (
        lockup.get("metadata", {})
        .get("lockupMetadataViewModel", {})
        .get("metadata", {})
        .get("contentMetadataViewModel", {})
        .get("metadataRows", [])
    )
    texts = []
    for row in rows:
        for part in row.get("metadataParts", []):
            text = part.get("text", {}).get("content")
            if text:
                texts.append(text)
    return " / ".join(texts)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(request) as response:
        destination.write_bytes(response.read())


def clean_track_title(title: str) -> str:
    text = re.sub(r"\s*[\[\(][Pp]iano[\]\)]", "", title)
    text = re.sub(r"\s*(?:DQ|Dragon Quest)\s*[IVX]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*[IVX]+-\d+\s*$", "", text)
    text = re.sub(r"/+", " / ", text)
    parts = [part.strip() for part in text.split("/") if part.strip()]
    if parts:
        return parts[0]
    return title.strip()


def extract_difficulty(description: str) -> dict:
    difficulty_line = next((line.strip() for line in description.splitlines() if "難易度" in line and "★" in line), "")
    star_match = re.search(r"(★{1,5})", difficulty_line)
    score_match = re.search(r"[（(]\s*([1-5])\s+([^)）]+?)\s*[)）]", difficulty_line)

    stars = len(star_match.group(1)) if star_match else None
    detail = score_match.group(2).strip() if score_match else ""
    labels = {
        1: "初級",
        2: "初中級",
        3: "中級",
        4: "中上級",
        5: "上級",
    }
    label = labels.get(stars, "未設定")

    return {
        "stars": stars,
        "label": label,
        "detail": detail,
    }


def fetch_playlist_tracks(playlist_id: str, api_key: str) -> list[dict]:
    tracks = []
    page_token = None

    while True:
        query = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key,
        }
        if page_token:
            query["pageToken"] = page_token

        data = fetch_json(f"{YOUTUBE_API_BASE}?{urlencode(query)}")

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            raw_title = snippet.get("title", "").strip()
            if not raw_title or raw_title == "Private video":
                continue

            description = snippet.get("description", "")
            difficulty = extract_difficulty(description)
            video_id = content.get("videoId") or snippet.get("resourceId", {}).get("videoId")
            if not video_id:
                continue

            tracks.append(
                {
                    "title": clean_track_title(raw_title),
                    "rawTitle": raw_title,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "difficultyLabel": difficulty["label"],
                    "difficultyStars": difficulty["stars"],
                    "difficultyDetail": difficulty["detail"],
                }
            )

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return tracks


def parse_podcasts(data: dict, api_key: str | None) -> list[dict]:
    tabs = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
    selected = next(tab["tabRenderer"] for tab in tabs if tab.get("tabRenderer", {}).get("selected"))
    contents = selected["content"]["richGridRenderer"]["contents"]

    podcasts = []
    for item in contents:
        lockup = item.get("richItemRenderer", {}).get("content", {}).get("lockupViewModel")
        if not lockup:
            continue

        image_sources = (
            lockup["contentImage"]["collectionThumbnailViewModel"]["primaryThumbnail"]["thumbnailViewModel"]["image"]["sources"]
        )
        title = lockup["metadata"]["lockupMetadataViewModel"]["title"]["content"]
        playlist_id = lockup["contentId"]
        subtitle = metadata_text(lockup)
        episode_text = (
            lockup["contentImage"]["collectionThumbnailViewModel"]["primaryThumbnail"]["thumbnailViewModel"]["overlays"][0]
            ["thumbnailOverlayBadgeViewModel"]["thumbnailBadges"][0]["thumbnailBadgeViewModel"]["text"]
        )

        cover_file = COVERS_DIR / f"{playlist_id}.jpg"
        download_file(image_sources[-1]["url"], cover_file)

        podcast = {
            "id": playlist_id,
            "title": title,
            "description": subtitle,
            "thumbnail": f"./covers/{playlist_id}.jpg",
            "itemCountText": episode_text,
            "url": f"https://www.youtube.com/playlist?list={playlist_id}",
        }

        if api_key:
            podcast["tracks"] = fetch_playlist_tracks(playlist_id, api_key)

        podcasts.append(podcast)

    return podcasts


def main():
    load_env()
    COVERS_DIR.mkdir(exist_ok=True)
    api_key = os.environ.get("YOUTUBE_API_KEY")
    html = fetch_page()
    data = extract_initial_data(html)
    podcasts = parse_podcasts(data, api_key)
    OUTPUT_FILE.write_text(
        "window.playlistData = " + json.dumps(podcasts, ensure_ascii=False, indent=2) + ";",
        encoding="utf-8",
    )
    print(f"Saved {len(podcasts)} podcast playlists to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

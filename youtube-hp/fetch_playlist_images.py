import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / "youtube-oauth-token.json"
OUTPUT_FILE = ROOT / "playlist-images-response.json"
PLAYLIST_DATA_FILE = ROOT / "playlist-data.js"
CLIENT_SECRET_FILE = ROOT / "client_secret_194457164346-tk0b1mtt4j0vo653a44njfllc43npqoo.apps.googleusercontent.com.json"


def load_token():
    return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))


def load_client():
    data = json.loads(CLIENT_SECRET_FILE.read_text(encoding="utf-8"))
    return data["installed"]


def refresh_access_token(token, client):
    payload = urllib.parse.urlencode(
        {
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "refresh_token": token["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        client["token_uri"],
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        refreshed = json.loads(response.read().decode("utf-8"))
    refreshed["refresh_token"] = token["refresh_token"]
    TOKEN_FILE.write_text(json.dumps(refreshed, ensure_ascii=False, indent=2), encoding="utf-8")
    return refreshed


def load_playlist_ids():
    raw = PLAYLIST_DATA_FILE.read_text(encoding="utf-8")
    prefix = "window.playlistData = "
    if not raw.startswith(prefix):
        raise SystemExit("playlist-data.js format was unexpected.")
    data = json.loads(raw[len(prefix):].rstrip(";\n"))
    return [item["id"] for item in data]


def fetch_playlist_images(access_token, playlist_id):
    params = urllib.parse.urlencode({"part": "snippet", "playlistId": playlist_id, "maxResults": 50})
    request = urllib.request.Request(
        f"https://www.googleapis.com/youtube/v3/playlistImages?{params}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    if not TOKEN_FILE.exists():
        raise SystemExit("Missing youtube-oauth-token.json. Run oauth_youtube.py first.")

    token = load_token()
    client = load_client()
    if "refresh_token" in token:
        token = refresh_access_token(token, client)

    results = {}
    for playlist_id in load_playlist_ids():
        results[playlist_id] = fetch_playlist_images(token["access_token"], playlist_id)

    OUTPUT_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved playlist image responses to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

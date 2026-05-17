import base64
import hashlib
import json
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLIENT_SECRET_FILE = ROOT / "client_secret_194457164346-tk0b1mtt4j0vo653a44njfllc43npqoo.apps.googleusercontent.com.json"
TOKEN_FILE = ROOT / "youtube-oauth-token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    server_version = "OAuthCallback/1.0"

    def do_GET(self):
      parsed = urllib.parse.urlparse(self.path)
      query = urllib.parse.parse_qs(parsed.query)
      self.server.oauth_code = query.get("code", [None])[0]
      self.server.oauth_error = query.get("error", [None])[0]

      body = "Authentication finished. You can close this tab."
      self.send_response(200)
      self.send_header("Content-Type", "text/plain; charset=utf-8")
      self.send_header("Content-Length", str(len(body.encode("utf-8"))))
      self.end_headers()
      self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
      return


def read_client():
    data = json.loads(CLIENT_SECRET_FILE.read_text(encoding="utf-8"))
    return data["installed"]


def exchange_code(client, code, verifier, redirect_uri):
    payload = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": verifier,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        client["token_uri"],
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    if not CLIENT_SECRET_FILE.exists():
        raise SystemExit(f"Missing OAuth client file: {CLIENT_SECRET_FILE}")

    client = read_client()
    server = HTTPServer(("127.0.0.1", 0), OAuthCallbackHandler)
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"

    verifier = b64url(secrets.token_bytes(48))
    challenge = b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    state = secrets.token_urlsafe(24)

    params = {
        "client_id": client["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f'{client["auth_uri"]}?{urllib.parse.urlencode(params)}'

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("Open this URL if the browser does not launch automatically:")
    print(auth_url)
    webbrowser.open(auth_url)
    thread.join(timeout=300)

    code = getattr(server, "oauth_code", None)
    error = getattr(server, "oauth_error", None)
    server.server_close()

    if error:
        raise SystemExit(f"OAuth error: {error}")
    if not code:
        raise SystemExit("Timed out waiting for OAuth callback.")

    token = exchange_code(client, code, verifier, redirect_uri)
    TOKEN_FILE.write_text(json.dumps(token, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved token to {TOKEN_FILE}")


if __name__ == "__main__":
    main()

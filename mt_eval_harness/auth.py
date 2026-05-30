"""
OAuth PKCE authentication for the mt-eval harness.

Supports GitHub and Google sign-in via Supabase Auth.
Tokens are stored locally in ~/.mt-eval/auth.json.

Security model:
    - The Supabase anon key (SUPABASE_ANON_KEY) is public and read-only.
      It's the same key embedded in the website frontend.
    - User identity is established via OAuth (GitHub or Google).
    - The resulting JWT grants INSERT permission via RLS policies
      on the run_cards table (authenticated users only).
    - No service role key is ever distributed to end users.
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# Supabase public config
# These are safe to embed — identical to the values in the website frontend.
# The anon key only grants read access; writes require a valid user JWT.
# ---------------------------------------------------------------------------

SUPABASE_URL = "https://sjdomynysdljkbemupqa.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_bV6CFNFnzxhQI0wlBx2J0A_5Vm5gFBp"

# Where we persist the user's refresh token between sessions
TOKEN_PATH = Path.home() / ".mt-eval" / "auth.json"


# ---------------------------------------------------------------------------
# PKCE helpers
# ---------------------------------------------------------------------------

def _generate_pkce() -> tuple[str, str]:
    """Generate a PKCE code verifier and challenge.

    Returns:
        (code_verifier, code_challenge) tuple.
    """
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ---------------------------------------------------------------------------
# Token persistence
# ---------------------------------------------------------------------------

def _save_tokens(session: dict) -> None:
    """Write session tokens to disk with owner-only permissions."""
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(session, indent=2), encoding="utf-8")
    os.chmod(TOKEN_PATH, 0o600)


def _load_tokens() -> dict | None:
    """Load saved session tokens, or None if not found / corrupt."""
    if not TOKEN_PATH.exists():
        return None
    try:
        return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Supabase Auth API calls
# ---------------------------------------------------------------------------

def _refresh_session(refresh_token: str) -> dict:
    """Exchange a refresh token for a new access token."""
    data = json.dumps({"refresh_token": refresh_token}).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
        data=data,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _exchange_code(code: str, code_verifier: str, redirect_uri: str) -> dict:
    """Exchange an OAuth authorization code + PKCE verifier for tokens.

    Per RFC 7636, the redirect_uri must match the one used in the
    original authorization request.
    """
    data = json.dumps({
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=pkce",
        data=data,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Local callback server
# ---------------------------------------------------------------------------

class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP handler that captures the OAuth redirect."""

    auth_code: str | None = None
    error_message: str | None = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _CallbackHandler.auth_code = params["code"][0]
            self._respond(200, (
                "<h1>✅ Authenticated!</h1>"
                "<p>You can close this tab and return to the terminal.</p>"
            ))
        else:
            msg = params.get("error_description", ["Unknown error"])[0]
            _CallbackHandler.error_message = msg
            self._respond(400, f"<h1>❌ Error</h1><p>{msg}</p>")

    def _respond(self, code: int, body: str):
        html = (
            f'<html><body style="font-family:system-ui;text-align:center;'
            f'padding:4rem;color:#e0e0e0;background:#1a1a2e;">{body}</body></html>'
        )
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress default request logging."""
        pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_session() -> dict:
    """Get a valid Supabase session, refreshing or prompting login as needed.

    Returns:
        Session dict with 'access_token', 'refresh_token', and 'user'.

    Raises:
        SystemExit if authentication fails or the user cancels.
    """
    tokens = _load_tokens()

    # Try refreshing an existing session first
    if tokens and tokens.get("refresh_token"):
        try:
            session = _refresh_session(tokens["refresh_token"])
            _save_tokens(session)
            user = session.get("user", {})
            identity = _extract_identity(user)
            print(f"  Authenticated as {identity}")
            return session
        except Exception:
            # Refresh token expired or revoked — need fresh login
            pass

    return _interactive_login()


def get_submitter_name(session: dict) -> str:
    """Extract a human-readable submitter name from a session.

    Priority: GitHub username > Google name > email.
    """
    return _extract_identity(session.get("user", {}))


def logout() -> None:
    """Remove stored tokens."""
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
        print("  Logged out. Stored tokens removed.")
    else:
        print("  Not logged in.")


# ---------------------------------------------------------------------------
# Interactive login flow
# ---------------------------------------------------------------------------

def _interactive_login() -> dict:
    """Prompt the user to choose a provider and run the OAuth PKCE flow."""
    print("\n  No saved credentials. Sign in to publish results.\n")
    print("  Choose a provider:")
    print("    [1] GitHub")
    print("    [2] Google")

    choice = input("\n  > ").strip()

    provider_map = {"1": "github", "2": "google"}
    provider = provider_map.get(choice)
    if not provider:
        print("  Invalid choice. Use 1 or 2.")
        raise SystemExit(1)

    return _oauth_login(provider)


def _oauth_login(provider: str) -> dict:
    """Run the full OAuth PKCE flow for a given provider.

    1. Start a local HTTP server on a random port
    2. Open the browser to Supabase's /authorize endpoint
    3. Wait for the redirect callback with the auth code
    4. Exchange the code + PKCE verifier for session tokens
    """
    verifier, challenge = _generate_pkce()

    # Ephemeral local server on a random available port
    server = http.server.HTTPServer(("127.0.0.1", 0), _CallbackHandler)
    port = server.server_address[1]
    redirect_uri = f"http://localhost:{port}/callback"

    # Build the Supabase authorize URL
    params = urllib.parse.urlencode({
        "provider": provider,
        "redirect_to": redirect_uri,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })
    auth_url = f"{SUPABASE_URL}/auth/v1/authorize?{params}"

    print(f"\n  Opening browser for {provider.title()} sign-in...")
    webbrowser.open(auth_url)

    # Wait for the callback (timeout after 120 seconds)
    server.timeout = 120
    _CallbackHandler.auth_code = None
    _CallbackHandler.error_message = None

    while _CallbackHandler.auth_code is None and _CallbackHandler.error_message is None:
        server.handle_request()

    server.server_close()

    if _CallbackHandler.error_message:
        print(f"\n  Authentication error: {_CallbackHandler.error_message}")
        raise SystemExit(1)

    code = _CallbackHandler.auth_code

    # Exchange the authorization code for tokens
    try:
        session = _exchange_code(code, verifier, redirect_uri)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        print(f"\n  Token exchange failed ({exc.code}): {body}")
        raise SystemExit(1)

    _save_tokens(session)

    user = session.get("user", {})
    identity = _extract_identity(user)
    print(f"\n  ✅ Authenticated as {identity}")

    return session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_identity(user: dict) -> str:
    """Pull the best available display name from the Supabase user object."""
    meta = user.get("user_metadata", {})
    return (
        meta.get("preferred_username")   # GitHub username
        or meta.get("user_name")         # GitHub fallback
        or meta.get("full_name")         # Google display name
        or user.get("email", "anonymous")
    )

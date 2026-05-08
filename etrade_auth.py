"""
E*TRADE Sandbox OAuth 1.0a Authentication

Flow:
  1. Fetch a request token from the sandbox
  2. Print the authorization URL for the user to visit and authorize
  3. Accept the verifier code the user pastes back
  4. Exchange request token + verifier for an access token
  5. Make a sample authenticated API call to confirm it works
"""

import os
import webbrowser
from typing import Tuple
from requests_oauthlib import OAuth1Session

# ---------------------------------------------------------------------------
# Credentials  (sandbox)
# ---------------------------------------------------------------------------
CONSUMER_KEY    = os.environ.get("ETRADE_KEY",    "731d79a19427ba3889a05fc66d831d4f")
CONSUMER_SECRET = os.environ.get("ETRADE_SECRET", "0500c28cc9c99ee98dc0a4171900e39b99d46c48e28e7d8c0308795bb1f35fba")

# ---------------------------------------------------------------------------
# Sandbox endpoints
# ---------------------------------------------------------------------------
REQUEST_TOKEN_URL = "https://apisb.etrade.com/oauth/request_token"
AUTHORIZE_URL     = "https://us.etrade.com/e/t/etws/authorize"
ACCESS_TOKEN_URL  = "https://apisb.etrade.com/oauth/access_token"
BASE_URL          = "https://apisb.etrade.com"


def get_request_token() -> Tuple[str, str]:
    """Step 1 – obtain a temporary request token."""
    session = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        callback_uri="oob",          # out-of-band: user will copy/paste the verifier
    )
    response = session.fetch_request_token(REQUEST_TOKEN_URL)
    return response["oauth_token"], response["oauth_token_secret"]


def build_authorize_url(request_token: str) -> str:
    """Step 2 – build the URL the user must visit to grant access."""
    return f"{AUTHORIZE_URL}?key={CONSUMER_KEY}&token={request_token}"


def get_access_token(request_token: str, request_secret: str, verifier: str) -> Tuple[str, str]:
    """Step 3 – exchange request token + verifier for an access token."""
    session = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=request_token,
        resource_owner_secret=request_secret,
        verifier=verifier,
    )
    response = session.fetch_access_token(ACCESS_TOKEN_URL)
    return response["oauth_token"], response["oauth_token_secret"]


def make_authenticated_session(access_token: str, access_secret: str) -> OAuth1Session:
    """Return a fully authenticated OAuth1 session ready for API calls."""
    return OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_secret,
    )


def verify_auth(session: OAuth1Session) -> None:
    """Make a lightweight API call to confirm the session is valid."""
    url = f"{BASE_URL}/v1/user/list"
    resp = session.get(url)
    print(f"\nVerification call → {url}")
    print(f"  Status : {resp.status_code}")
    if resp.ok:
        print(f"  Body   : {resp.text[:400]}")
    else:
        print(f"  Error  : {resp.text[:400]}")


def main() -> None:
    print("=" * 60)
    print("  E*TRADE Sandbox – OAuth 1.0a Authentication")
    print("=" * 60)

    # --- Step 1: request token ---
    print("\n[1/3] Fetching request token …")
    req_token, req_secret = get_request_token()
    print(f"      Request token : {req_token}")

    # --- Step 2: user authorization ---
    auth_url = build_authorize_url(req_token)
    print(f"\n[2/3] Open this URL in your browser and log in to E*TRADE:")
    print(f"\n      {auth_url}\n")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass  # headless environments – user will copy/paste manually

    verifier = input("      Paste the verifier/PIN shown after authorization: ").strip()

    # --- Step 3: access token ---
    print("\n[3/3] Exchanging for access token …")
    acc_token, acc_secret = get_access_token(req_token, req_secret, verifier)
    print(f"      Access token        : {acc_token}")
    print(f"      Access token secret : {acc_secret}")

    # --- Verify ---
    session = make_authenticated_session(acc_token, acc_secret)
    verify_auth(session)

    print("\nAuthentication complete.  Store the access token/secret for reuse.")
    print(f"  ETRADE_ACCESS_TOKEN={acc_token}")
    print(f"  ETRADE_ACCESS_SECRET={acc_secret}")


if __name__ == "__main__":
    main()

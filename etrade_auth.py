"""
E*TRADE OAuth 1.0a Authentication (sandbox or production)

Usage:
  py etrade_auth.py          # production (default)
  py etrade_auth.py sandbox  # sandbox
"""

import os
import sys
import webbrowser
from typing import Tuple
from requests_oauthlib import OAuth1Session

# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
ENV = "sandbox" if len(sys.argv) > 1 and sys.argv[1].lower() == "sandbox" else "prod"

if ENV == "sandbox":
    CONSUMER_KEY    = "731d79a19427ba3889a05fc66d831d4f"
    CONSUMER_SECRET = "0500c28cc9c99ee98dc0a4171900e39b99d46c48e28e7d8c0308795bb1f35fba"
    BASE_URL        = "https://apisb.etrade.com"
else:
    CONSUMER_KEY    = "ef3aa933eebc40dff376fdd167ff37af"
    CONSUMER_SECRET = "365ede6296bd4908d84bb568ce4f591ed3d4236edb3223c70e1255bbf8e5ce70"
    BASE_URL        = "https://api.etrade.com"

REQUEST_TOKEN_URL = f"{BASE_URL}/oauth/request_token"
AUTHORIZE_URL     = "https://us.etrade.com/e/t/etws/authorize"
ACCESS_TOKEN_URL  = f"{BASE_URL}/oauth/access_token"


def get_request_token() -> Tuple[str, str]:
    session = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri="oob")
    response = session.fetch_request_token(REQUEST_TOKEN_URL)
    return response["oauth_token"], response["oauth_token_secret"]


def build_authorize_url(request_token: str) -> str:
    return f"{AUTHORIZE_URL}?key={CONSUMER_KEY}&token={request_token}"


def get_access_token(request_token: str, request_secret: str, verifier: str) -> Tuple[str, str]:
    session = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=request_token,
        resource_owner_secret=request_secret,
        verifier=verifier,
    )
    response = session.fetch_access_token(ACCESS_TOKEN_URL)
    return response["oauth_token"], response["oauth_token_secret"]


def main() -> None:
    print("=" * 60)
    print(f"  E*TRADE OAuth 1.0a Authentication  [{ENV.upper()}]")
    print("=" * 60)

    print("\n[1/3] Fetching request token ...")
    req_token, req_secret = get_request_token()
    print(f"      Request token : {req_token}")

    auth_url = build_authorize_url(req_token)
    print(f"\n[2/3] Open this URL in your browser and log in to E*TRADE:")
    print(f"\n      {auth_url}\n")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    verifier = input("      Paste the verifier/PIN shown after authorization: ").strip()

    print("\n[3/3] Exchanging for access token ...")
    acc_token, acc_secret = get_access_token(req_token, req_secret, verifier)
    print(f"      Access token        : {acc_token}")
    print(f"      Access token secret : {acc_secret}")

    print("\nAuthentication complete.")
    print(f"  ETRADE_ACCESS_TOKEN={acc_token}")
    print(f"  ETRADE_ACCESS_SECRET={acc_secret}")


if __name__ == "__main__":
    main()

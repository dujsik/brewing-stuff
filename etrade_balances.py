"""
Fetch E*TRADE account balances (sandbox or production).

Usage:
  py etrade_balances.py          # production (default)
  py etrade_balances.py sandbox  # sandbox
"""

import sys
from requests_oauthlib import OAuth1Session

# ---------------------------------------------------------------------------
# Credentials  —  paste your access token/secret after running etrade_auth.py
# ---------------------------------------------------------------------------
ENV = "sandbox" if len(sys.argv) > 1 and sys.argv[1].lower() == "sandbox" else "prod"

if ENV == "sandbox":
    CONSUMER_KEY    = "731d79a19427ba3889a05fc66d831d4f"
    CONSUMER_SECRET = "0500c28cc9c99ee98dc0a4171900e39b99d46c48e28e7d8c0308795bb1f35fba"
    ACCESS_TOKEN    = "t5sNUFVBo5y5dRRK8JelEfVEjXN7RfPZDPqjCgxO8RM="
    ACCESS_SECRET   = "PZWsZlN48s/1EB8IRRRCqXCnXzLcA/D6IRB2RcBe2HY="
    BASE_URL        = "https://apisb.etrade.com"
else:
    CONSUMER_KEY    = "ef3aa933eebc40dff376fdd167ff37af"
    CONSUMER_SECRET = "365ede6296bd4908d84bb568ce4f591ed3d4236edb3223c70e1255bbf8e5ce70"
    ACCESS_TOKEN    = ""   # paste from etrade_auth.py output
    ACCESS_SECRET   = ""   # paste from etrade_auth.py output
    BASE_URL        = "https://api.etrade.com"

if not ACCESS_TOKEN or not ACCESS_SECRET:
    print("ERROR: Run 'py etrade_auth.py' first and paste the access token/secret above.")
    sys.exit(1)

session = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_SECRET,
)


def get_accounts():
    resp = session.get(f"{BASE_URL}/v1/accounts/list.json")
    resp.raise_for_status()
    return resp.json()["AccountListResponse"]["Accounts"]["Account"]


def get_balance(account_id_key, account_type):
    resp = session.get(
        f"{BASE_URL}/v1/accounts/{account_id_key}/balance.json",
        params={"instType": account_type, "realTimeNAV": "true"},
    )
    resp.raise_for_status()
    return resp.json()["BalanceResponse"]


def main():
    print(f"Fetching accounts [{ENV.upper()}] ...")
    accounts = get_accounts()

    for acct in accounts:
        key   = acct["accountIdKey"]
        name  = acct.get("accountDesc", acct.get("accountId", key))
        atype = acct.get("institutionType", "BROKERAGE")

        print(f"\nAccount : {name}  (type: {atype})")
        print(f"  ID key: {key}")

        try:
            bal      = get_balance(key, atype)
            computed = bal.get("Computed", {})
            rtv      = computed.get("RealTimeValues", {})
            print(f"  Account type         : {bal.get('accountType', 'N/A')}")
            print(f"  Net cash             : ${computed.get('netCash', 0.0):.2f}")
            print(f"  Cash balance         : ${computed.get('cashBalance', 0.0):.2f}")
            print(f"  Net market value     : ${rtv.get('netMv', 0.0):.2f}")
            print(f"  Total account value  : ${rtv.get('totalAccountValue', 0.0):.2f}")
        except Exception as e:
            print(f"  Could not fetch balance: {e}")


if __name__ == "__main__":
    main()

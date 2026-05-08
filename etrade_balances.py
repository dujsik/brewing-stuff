"""
Fetch E*TRADE sandbox account balances.
Run: py etrade_balances.py
"""

import json
from requests_oauthlib import OAuth1Session

CONSUMER_KEY    = "731d79a19427ba3889a05fc66d831d4f"
CONSUMER_SECRET = "0500c28cc9c99ee98dc0a4171900e39b99d46c48e28e7d8c0308795bb1f35fba"
ACCESS_TOKEN    = "t5sNUFVBo5y5dRRK8JelEfVEjXN7RfPZDPqjCgxO8RM="
ACCESS_SECRET   = "PZWsZlN48s/1EB8IRRRCqXCnXzLcA/D6IRB2RcBe2HY="

BASE_URL = "https://apisb.etrade.com"

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
    params = {
        "instType": account_type,
        "realTimeNAV": "true",
    }
    resp = session.get(
        f"{BASE_URL}/v1/accounts/{account_id_key}/balance.json",
        params=params,
    )
    resp.raise_for_status()
    return resp.json()["BalanceResponse"]


def main():
    print("Fetching accounts...")
    accounts = get_accounts()

    for acct in accounts:
        key   = acct["accountIdKey"]
        name  = acct.get("accountDesc", acct.get("accountId", key))
        atype = acct.get("institutionType", "BROKERAGE")

        print(f"\nAccount : {name}  (type: {atype})")
        print(f"  ID key: {key}")

        try:
            bal = get_balance(key, atype)
            print(f"  Raw response: {json.dumps(bal, indent=2)}")
        except Exception as e:
            print(f"  Could not fetch balance: {e}")


if __name__ == "__main__":
    main()

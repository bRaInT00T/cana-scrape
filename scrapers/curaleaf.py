import requests
import json
import time
from pathlib import Path

SITE = "curaleaf"
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"{SITE}_products.json"
BASE_URL = "https://web-ui-curaleaf.sweedpos.com/_api/proxy/Products/GetProductList"

HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": f"https://{SITE}.com",
    "referer": f"https://{SITE}.com/",
    "storeid": "128",
    "ssr": "false",
    "platformos": "web",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

BODY = {
    "filters": {},
    "page": 1,
    "pageSize": 100, # No cap discovered on page size.  Settiing to 100 to be nice.
    "sortingMethodId": 2, # Sort by price (low to high)
    "searchTerm": "",
    "saleType": "Recreational",
    "platformOs": "web",
}

def fetch_all_curaleaf_products():
    all_products = []
    page = 1

    while True:
        BODY["page"] = page
        response = requests.post(BASE_URL, headers=HEADERS, json=BODY)
        response.raise_for_status()
        data = response.json()
        print(data)
        products = data.get("list", {})
        if not products:
            break

        all_products.extend(products)
        print(f"✅ Fetched {len(products)} products from page {page}")

        if len(products) < BODY["pageSize"]:
            break

        page += 1
        time.sleep(0.25)

    with open(OUTFILE, "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\n🎉 Saved {len(all_products)} total products to {OUTFILE}")

if __name__ == "__main__":
    fetch_all_curaleaf_products()
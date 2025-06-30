import requests
import json
import time
from pathlib import Path
from .base import ScraperRegistry


SITE = "indigodispensary"
BASE_URL = "https://api.dispenseapp.com/v1/venues/041444e70b831110/product-categories/24314d00f970b559/products"
data_dir = Path(__file__).resolve().parent.parent / "data/json"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"{SITE}_products.json"

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "api-key": "49dac8e0-7743-11e9-8e3f-a5601eb2e936",
    "origin": f"https://www.{SITE}.com",
    "referer": f"https://www.{SITE}.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "x-prospect-token": "e4258cf5-7c34-4bf4-816e-9ee023fcd194",
}

PARAMS = {
    "sort": "price",
    "limit": 50,
    "active": "true",
    "quantityMin": 1,
    "group": "true",
    "enable": "true",
    "orderPickUpType": "IN_STORE",
    "trackSearch": "true",
}


@ScraperRegistry.register
def fetch_all_indigodispensary_products():
    all_products = []
    skip = 0
    while True:
        params = PARAMS.copy()
        params["skip"] = skip

        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        try:
            products = data.get("data", [])
        except (KeyError, TypeError):
            print("⚠️ Unexpected response format:", data)
            break

        if not products:
            break

        all_products.extend(products)
        print(f"✅ Fetched {len(products)} products (skip={skip})")

        if len(products) < PARAMS["limit"]:
            break  # Reached end

        skip += PARAMS["limit"]
        time.sleep(0.25)  # be nice to the server

    with open(OUTFILE, "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\n🎉 Saved {len(all_products)} total products to {OUTFILE}")


if __name__ == "__main__":
    fetch_all_indigodispensary_products()

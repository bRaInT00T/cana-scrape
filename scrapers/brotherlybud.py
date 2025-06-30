import requests
import time
import json
from pathlib import Path
from datetime import datetime, timezone
from .base import ScraperRegistry


# Unverified if limit is manipulable
SITE = "brotherlybud"
data_dir = Path(__file__).resolve().parent.parent / "data/json"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"{SITE}_products.json"
URL = "https://brotherlybud.com/wp-admin/admin-ajax.php"
HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": f"https://{SITE}.com",
    "referer": f"https://{SITE}.com/shop/?pagination=1&sort=NAME_ASC&retailer_id=14beadc1-5ad4-49df-b412-7fe5118669cc&menu_type=RECREATIONAL&collection_type=PICKUP",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
BASE_DATA = {
    "action": "wizard_show_products",
    "wizard_data[age_confirm]": "true",
    "wizard_data[collection_method]": "PICKUP",
    "wizard_data[menu_type]": "RECREATIONAL",
    "wizard_data[retailer_id]": "14beadc1-5ad4-49df-b412-7fe5118669cc",
    "wizard_data[sort]": "PRICE_ASC",
    "wizard_data[event]": "CART DATA - url and localStorage data MATCH",
    "wizard_data[prod_prefix]": "",
    "nonce_ajax": "873382af87",
    "prod_categories[search_key_word]": "",
    "prod_categories[sort_order]": "PRICE_ASC",
    "search_key_word": "",
    "filter_attributes[search_key_word]": "",
    "filter_attributes[sort_order]": "PRICE_ASC"
}

@ScraperRegistry.register
def fetch_all_brotherlybud_products():
    all_products = []
    page = 1

    while True:
        data = BASE_DATA.copy()
        data["prods_pageNumber"] = str(page)

        response = requests.post(URL, headers=HEADERS, data=data)
        response.raise_for_status()
        result = response.json()

        products = result.get("data", {}).get("products_list", [])
        if not products:
            break

        all_products.extend(products)
        print(f"✅ Page {page}: Fetched {len(products)} products")
        page += 1
        time.sleep(0.3)

    with open(OUTFILE, "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\n🎉 Saved {len(all_products)} products to {OUTFILE}")

if __name__ == "__main__":
    fetch_all_brotherlybud_products()
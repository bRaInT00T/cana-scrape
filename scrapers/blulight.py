import requests
import time
import json
from pathlib import Path
from datetime import datetime, timezone
# from .base import ScraperRegistry

# https://blulight.com/
# Blulight Cannabis- Gloucester City
# 401 N Broadway, Gloucester City, NJ 08030

SITE = "blulight"
data_dir = Path(__file__).resolve().parent.parent / "data/json"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"{SITE}_products.json"
url = "https://headless.treez.io/v2.0/dispensary/blulight-gc/ecommerce/menu/searchProducts?pageSize=1000"
headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0, no-cache, must-revalidate, proxy-revalidate",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": f"https://{SITE}.com",
    "Referer": f"https://{SITE}.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "client_id": "29dce682258145c6b1cf71027282d083",
    "client_secret": "A57bB49AfD7F4233B1750a0B501B4E16",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

payload = {
    "strictMedicalCustomerType": False,
    "filters": {
        "price": {
            "between": {
                "min": 2,
                "max": 500000,
                "includeMin": True,
                "includeMax": True
            }
        }
    },
    "sortBy": {
        "field": "price",
        "descending": False
    }
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()

with open(OUTFILE, "w") as f:
    json.dump(response.json(), f, indent=2)

print(f"✅ Data saved to {OUTFILE}")
print(len(response.json()['data']))
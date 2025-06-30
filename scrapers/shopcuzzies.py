import requests
import json
import time
from pathlib import Path
from .base import ScraperRegistry


SITE = "shopcuzzies"
URL = "https://www.shopcuzzies.com/wp-json/joint-ecommerce/v1/products/5731/_search"
data_dir = Path(__file__).resolve().parent.parent / "data/json"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"{SITE}_products.json"

HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": f"https://www.{SITE}.com",
    "referer": f"https://www.{SITE}.com/menu/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

BASE_PAYLOAD = {
    "aggs": {
        "facet_bucket_all": {
            "aggs": {
                "applicableSpecials.specialName": {
                    "terms": {
                        "field": "applicableSpecials.specialName",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "category": {
                    "terms": {
                        "field": "category",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "variants.option": {
                    "terms": {
                        "field": "variants.option",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "strainType": {
                    "terms": {
                        "field": "strainType",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "effects": {
                    "terms": {
                        "field": "effects",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "brandName": {
                    "terms": {
                        "field": "brandName",
                        "size": 500,
                        "order": {"_key": "asc"},
                    }
                },
                "tagList": {
                    "terms": {
                        "field": "tagList",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "collections": {
                    "terms": {
                        "field": "collections",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "posId": {
                    "terms": {
                        "field": "posId",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "terpenes.name": {
                    "terms": {
                        "field": "terpenes.name",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
                "cannabinoids.name": {
                    "terms": {
                        "field": "cannabinoids.name",
                        "size": 100,
                        "order": {"_count": "desc"},
                    }
                },
            },
            "filter": {"bool": {"must": []}},
        }
    },
    "size": 100,  # No cap discovered on page size.  Settiing to 100 to be nice.
    "_source": {
        "includes": [
            "globalProductId",
            "jointId",
            "posId",
            "businessId",
            "providerBusinessId",
            "name",
            "nameText",
            "category",
            "subCategory",
            "description",
            "descriptionHtml",
            "effects",
            "primaryImage",
            "images",
            "menuType",
            "strainType",
            "staffPick",
            "tagList",
            "collections",
            "urlFragment",
            "brand",
            "brandId",
            "brandName",
            "brandNameText",
            "variants",
            "lowestPrice",
            "potencies",
            "potencyThcDisplayValue",
            "potencyThcRangeHigh",
            "potencyThcRangeLow",
            "potencyThcUnit",
            "potencyCbdDisplayValue",
            "potencyCbdRangeHigh",
            "potencyCbdRangeLow",
            "potencyCbdUnit",
            "terpenes",
            "cannabinoids",
            "applicableSpecials",
        ]
    },
    "query": {
        "bool": {
            "filter": [
                {"bool": {"should": [{"term": {"businessId": "5731"}}]}},
                {"bool": {"should": [{"term": {"menuType": "RECREATIONAL"}}]}},
            ]
        }
    },
    "from": 0,
    "sort": [{"potencyThcRangeHigh": "asc"}],
}


@ScraperRegistry.register
def fetch_all_shopcuzzies_products():
    all_products = []
    page_size = BASE_PAYLOAD["size"]
    offset = 0

    while True:
        payload = BASE_PAYLOAD.copy()
        payload["from"] = offset

        response = requests.post(URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        products = [hit["_source"] for hit in hits if "_source" in hit]
        all_products.extend(products)
        print(f"✅ Fetched {len(products)} products from offset {offset}")

        if len(hits) < page_size:
            break

        offset += page_size
        time.sleep(0.25)

    with open(OUTFILE, "w") as f:
        json.dump(all_products, f, indent=2)

    print(f"\n🎉 Saved {len(all_products)} total products to {OUTFILE}")


if __name__ == "__main__":
    fetch_all_shopcuzzies_products()

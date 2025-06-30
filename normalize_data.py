import json
import pandas as pd
from pathlib import Path
import re

data_dir = Path("data/json")
files = [
    "brotherlybud_products.json",
    "curaleaf_products.json",
    "indigodispensary_products.json",
    "mpxnj_products.json",
    "shopcuzzies_products.json",
]

rows = []

for file in files:
    with open(data_dir / file) as f:
        products = json.load(f)
    for prod in products:
        row = {
            "name": None,
            "category": None,
            "brand": None,
            "strainType": None,
            "priceRec": None,
            "dispensary": file.split("_")[0],
            "productUrl": None,
            "description": None,
        }
        # --- brotherlybud ---
        if "brotherlybud" in file:
            row["name"] = prod.get("name")
            row["category"] = prod.get("category")
            row["brand"] = (prod.get("brand") or {}).get("name")
            row["strainType"] = prod.get("strainType")
            v = prod.get("variants", [{}])[0]
            row["price"] = (
                v.get("specialPriceRec")
                if v.get("specialPriceRec") is not None
                else v.get("priceRec")
            )
            row["productUrl"] = (
                f"https://brotherlybud.com/product/{prod.get('slug')}"
                if prod.get("slug")
                else None
            )
            if row["productUrl"]:
                row[
                    "productUrl"
                ] += "/?retailer_id=14beadc1-5ad4-49df-b412-7fe5118669cc"
            row["description"] = prod.get("description")

        # --- curaleaf ---
        elif "curaleaf" in file:
            row["name"] = prod.get("name")
            category_obj = prod.get("category") or {}
            subcategory_obj = prod.get("subcategory") or {}
            category_name = category_obj.get("name", "")
            category_id = category_obj.get("id", "")
            subcategory_name = subcategory_obj.get("name", "")
            row["category"] = category_name
            row["brand"] = (prod.get("brand") or {}).get("name")
            strain_type = (
                (prod.get("strain") or {}).get("prevalence", {}).get("name")
                or (prod.get("strain") or {}).get("name")
                or ""
            )
            row["strainType"] = strain_type
            v = prod.get("variants", [{}])[0]
            row["price"] = (
                v.get("promoPrice")
                if v.get("promoPrice") is not None
                else v.get("price")
            )
            if v.get("name") and any(char.isdigit() for char in v.get("name")):
                row["description"] = v.get("name")
            else:
                row["description"] = None

            # Build the productUrl
            # e.g. https://curaleaf.com/shop/new-jersey/curaleaf-nj-bellmawr/menu/flower-7049/whole-flower-indica-zesty-garlic-cookies-3.5g-18162
            def slugify(val):
                import re

                if not val:
                    return ""
                val = str(val).lower().replace("&", "and")
                val = re.sub(r"[^a-z0-9]+", "-", val)
                return val.strip("-")

            if all(
                [
                    category_name,
                    category_id,
                    subcategory_name,
                    strain_type,
                    row["name"],
                    v.get("name"),
                    v.get("id"),
                ]
            ):
                # Try to map strain_type (e.g., "Indica" -> "indica")
                strain_slug = slugify(strain_type)
                url = (
                    f"https://curaleaf.com/shop/new-jersey/curaleaf-nj-bellmawr/menu/"
                    f"{slugify(category_name)}-{category_id}/"
                    f"{slugify(subcategory_name)}-{strain_slug}-{slugify(row['name'])}-{slugify(v.get('name'))}-{v.get('id')}"
                )
                row["productUrl"] = url
            else:
                row["productUrl"] = None
        # --- indigodispensary ---
        elif "indigodispensary" in file:
            v = prod.get("variants", [{}])[0]
            row["name"] = v.get("name") or prod.get("name")
            row["category"] = v.get("productCategoryName") or prod.get(
                "productCategoryName"
            )
            row["brand"] = (v.get("brand") or {}).get("name") or (
                prod.get("brand") or {}
            ).get("name")
            # Strain Type can be in multiple places
            row["strainType"] = v.get("cannabisType") or v.get("cannabisStrain")
            row["price"] = v.get("price")
            row["productUrl"] = v.get("productUrl") or prod.get("productUrl")
            row["description"] = v.get("description")
        # --- mpxnj ---
        elif "mpxnj" in file:
            row["name"] = prod.get("name")
            row["category"] = prod.get("category")
            row["brand"] = (prod.get("brand") or {}).get("name")
            row["strainType"] = prod.get("strainType")
            v = prod.get("variants", [{}])[0]
            row["price"] = (
                v.get("specialPriceRec")
                if v.get("specialPriceRec") is not None
                else v.get("priceRec")
            )
            if prod.get("slug"):
                row["productUrl"] = (
                    f"https://mpxnj.com/product/{prod.get('slug')}/?retailer_id=11883dc4-d7d7-4085-8e7b-ba5353eca58a"
                )
            else:
                row["productUrl"] = None
            row["description"] = prod.get("description")
        # --- shopcuzzies ---
        elif "shopcuzzies" in file:
            row["name"] = prod.get("name")
            row["category"] = prod.get("category")
            row["brand"] = prod.get("brandName") or prod.get("brandNameText")
            row["strainType"] = prod.get("strainType")
            v = prod.get("variants", [{}])[0]
            # Cast price to float, handle nulls
            try:
                row["price"] = (
                    float(v.get("specialPrice"))
                    if v.get("specialPrice")
                    else float(v.get("price"))
                )
            except Exception:
                row["price"] = None
            row["productUrl"] = (
                f"https://www.shopcuzzies.com/?product={prod.get('jointId')}"
                if prod.get("jointId")
                else None
            )
            row["description"] = prod.get("description")

        rows.append(row)

# Extract milligrams and pieces from name/description
for row in rows:
    # Try extracting from name first, then fallback to description if available
    text = row.get("name", "") or ""
    prod_desc = row.get("description", "")
    if prod_desc:
        text += " " + prod_desc

    # Regex for milligrams: matches things like "50mg", "100 MG", etc.
    potency_match = re.search(r"(\d+(?:\.\d+)?)\s?mgs?\b", text, re.IGNORECASE)
    val = float(potency_match.group(1)) if potency_match else None
    row["potency"] = int(val) if val is not None and val.is_integer() else val

    # Regex for pieces: matches things like "10pc", "10 pcs", "10 pieces", "10pk", "10 pack", etc.
    quant_match = re.search(
        r"(\d+)\s?(\w+\s?){0,2}?-?(?:p(?:cs?|ieces?)|pks?|per package|per bag|packs?|ct)\b",
        text,
        re.IGNORECASE,
    )
    row["quantity"] = int(quant_match.group(1)) if quant_match else None

df = pd.DataFrame(rows)
df.drop("description", axis=1, inplace=True)

# Ensure the columns exist even if not all rows have values
for col in ["potency", "quantity"]:
    if col not in df.columns:
        df[col] = None
df.to_csv("normalized_products.csv", index=False)

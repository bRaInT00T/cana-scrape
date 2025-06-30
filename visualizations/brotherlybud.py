import streamlit as st
import pandas as pd
import json
from pathlib import Path

SHOP = "brotherlybud"

# Load JSON data
# "../data/brotherlybud_products.json"
data_path = Path(__file__).resolve().parent.parent / "data/json" / f"{SHOP}_products.json"
with open(data_path) as f:
    products = json.load(f)

df = pd.json_normalize(products, sep=".")

# Add dispensary name and location columns
df["dispensary"] = "Brotherly Bud"
df["location"] = "500 N Black Horse Pike, Mt Ephraim, NJ 08059"  # Update if you want to be more precise

 # Extract priceRec from variants[0] if available
if "variants" in df.columns:
    df["priceRec"] = df["variants"].apply(
        lambda v: v[0].get("priceRec") if isinstance(v, list) and v and isinstance(v[0], dict) and "priceRec" in v[0] else None
    )
else:
    df["priceRec"] = None

df["priceRec"] = pd.to_numeric(df["priceRec"], errors="coerce")

# Extract brand name
df["brand"] = df["brand.name"] if "brand.name" in df.columns else None

# Ensure strainType column exists
if "strainType" not in df.columns:
    df["strainType"] = None

if "effects" not in df.columns:
    df["effects"] = None

# Normalize and export selected columns to CSV before filtering
export_cols = ["name", "category", "brand", "strainType", "priceRec", "dispensary", "location"]
for col in export_cols:
    if col not in df.columns:
        df[col] = None
df[export_cols].to_csv(Path(__file__).resolve().parent.parent / "data/csv" / "brotherlybud_products_normalized.csv", index=False)

st.header("Brotherlybud Products", divider="rainbow")

# Step 1: Filter by Category
selected_categories = st.multiselect(
    "Filter by Category",
    sorted(df["category"].dropna().unique().tolist()),
    default=["EDIBLES"]
)
filtered_df = df[df["category"].isin(selected_categories)] if selected_categories else df.copy()

# Step 2: Filter by Strain Type based on current category filter
strain_types = sorted(filtered_df["strainType"].dropna().unique().tolist())
selected_strains = st.multiselect("Select Strain Type(s)", strain_types, default=["INDICA", "HYBRID"])
filtered_df = filtered_df[filtered_df["strainType"].isin(selected_strains)] if selected_strains else filtered_df

# Step 3: Filter by Brand based on current filters
brands = sorted(filtered_df["brand"].dropna().unique().tolist())
selected_brands = st.multiselect("Filter by Brand", brands)
filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)] if selected_brands else filtered_df

# Step 4: Filter by Effects based on current filters
effects = sorted({effect for sublist in filtered_df["effects"].dropna() if isinstance(sublist, list) for effect in sublist})
selected_effects = st.multiselect("Filter by Effects", effects)
if selected_effects:
    filtered_df = filtered_df[
        filtered_df["effects"].apply(
            lambda e: isinstance(e, list) and any(effect in e for effect in selected_effects)
        )
    ]

# Step 5: Price Range Filter
if filtered_df["priceRec"].dropna().empty:
    st.warning("No valid price data available.")
    min_price, max_price = 0.0, 0.0
else:
    min_price_val = float(filtered_df["priceRec"].min())
    max_price_val = float(filtered_df["priceRec"].max())
    min_price, max_price = st.slider(
        "Price Range",
        min_price_val,
        max_price_val,
        (min_price_val, max_price_val),
        step=1.00,
        format="%.0f",
    )
    filtered_df = filtered_df[(filtered_df["priceRec"] >= min_price) & (filtered_df["priceRec"] <= max_price)]

# Display results
st.subheader(f"Showing {len(filtered_df)} products")
st.dataframe(filtered_df[["name", "category", "brand", "strainType", "priceRec", "dispensary", "location"]], hide_index=True, selection_mode="multi-row")
st.bar_chart(filtered_df["priceRec"].dropna())

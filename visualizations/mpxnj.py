import streamlit as st
import pandas as pd
import json
from pathlib import Path
import altair as alt

# ---------- Load Data ----------
DATA_FILE = Path(__file__).parent.parent / "data" / "mpxnj_all.json"

with open(DATA_FILE) as f:
    raw_data = json.load(f)

# ---------- Normalize & Clean ----------
df = pd.json_normalize(raw_data)

 # Extract priceRec from variants[0] if available
if "variants" in df.columns:
    df["priceRec"] = df["variants"].apply(
        lambda v: v[0].get("priceRec") if isinstance(v, list) and v and isinstance(v[0], dict) and "priceRec" in v[0] else None
    )
else:
    df["priceRec"] = None

df["priceRec"] = pd.to_numeric(df["priceRec"], errors="coerce")

# Use specialPriceRec if present, otherwise priceRec
if "specialPriceRec" in df.columns:
    df["price"] = df.apply(
        lambda row: row["specialPriceRec"] if pd.notnull(row.get("specialPriceRec")) else row.get("priceRec"),
        axis=1
    )
else:
    df["price"] = df.get("priceRec")
df["price"] = pd.to_numeric(df["price"], errors="coerce")

df["productUrl"] = "https://mpxnj.com/product/" + df["slug"] + "/?retailer_id=11883dc4-d7d7-4085-8e7b-ba5353eca58a"

# Rename and extract essential columns
df = df.rename(columns={
    "name": "name",
    "brand.name": "brand",
    "category": "type",
    "strainType": "strainType",
})

df = df[["name", "brand", "type", "strainType", "price", "productUrl"]]
df = df[df["price"].notnull()]
# Optionally fill missing brands, types, strains with "Unknown"
df["brand"] = df["brand"].fillna("Unknown")
df["type"] = df["type"].fillna("Unknown")
df["strainType"] = df["strainType"].fillna("Unknown")

# ---------- Sidebar Filters ----------
st.sidebar.title("🔍 Filter Products")

brands = sorted(df["brand"].dropna().unique())
strain_types = sorted(df["strainType"].dropna().unique())
price_min, price_max = df["price"].min(), df["price"].max()
categories = sorted(df["type"].dropna().unique())

selected_categories = st.sidebar.multiselect("Category", categories)
selected_brands = st.sidebar.multiselect("Brand", brands)
selected_strains = st.sidebar.multiselect("Strain Type", strain_types)
selected_price = st.sidebar.slider("Price Range", float(price_min), float(price_max), (float(price_min), float(price_max)), step=1.00, format="%.0f")

filtered_df = df[df["type"].isin(selected_categories)] if selected_categories else df.copy()
filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)] if selected_brands else filtered_df
filtered_df = filtered_df[filtered_df["strainType"].isin(selected_strains)] if selected_strains else filtered_df
filtered_df = filtered_df[filtered_df["price"].between(*selected_price)]


# ---------- Display Table ----------
st.title("🌿 MPXNJ Product Dashboard")

st.markdown(f"**{len(filtered_df)} products** match your filters.")

st.dataframe(
  filtered_df,
  use_container_width=True,
  hide_index=True,
  column_config={
    "productUrl": st.column_config.LinkColumn("Link", display_text="Link")
  }
)

# ---------- Price Distribution ----------
st.subheader("💸 Price Distribution by Brand")
chart = alt.Chart(filtered_df).mark_bar().encode(
    x=alt.X("brand:N", title="Brand"),
    y=alt.Y("mean(price):Q", title="Average Price"),
    color="brand:N",
    tooltip=["brand", "mean(price)"],
).properties(height=400)

st.altair_chart(chart, use_container_width=True)
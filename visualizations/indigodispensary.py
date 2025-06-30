import streamlit as st
import pandas as pd
import json
from pathlib import Path
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

# Load the JSON file
data_path = (
    Path(__file__).resolve().parent.parent / "data" / "indigodispensary_products.json"
)
with open(data_path) as f:
    products = json.load(f)

# Normalize JSON data
df = pd.json_normalize(products, sep=".")

# Extract and clean fields
df["brand"] = df["brand.name"].fillna("Unknown")
df["strainType"] = df["leaflogix.strainType"].fillna("Unknown")
df["type"] = df["type"].fillna(df["productCategoryName"]).fillna("Unknown")
df["priceWithDiscounts"] = pd.to_numeric(df["priceWithDiscounts"], errors="coerce")
df["effects"] = df["effects"].apply(lambda x: x if isinstance(x, list) else [])

# Sidebar filters
st.sidebar.title("Filters")

selected_categories = st.sidebar.multiselect(
    "Category", sorted(df["type"].dropna().unique()), default=[]
)
selected_brands = st.sidebar.multiselect(
    "Brand", sorted(df["brand"].dropna().unique()), default=[]
)
selected_strains = st.sidebar.multiselect(
    "Strain Type", sorted(df["strainType"].dropna().unique()), default=[]
)

all_effects = sorted({effect for sublist in df["effects"] for effect in sublist})
selected_effects = st.sidebar.multiselect("Effects", all_effects, default=[])

# Price range filter
if df["priceWithDiscounts"].dropna().empty:
    st.sidebar.warning("No price data available.")
    min_price, max_price = 0.0, 0.0
else:
    min_price_val, max_price_val = float(df["priceWithDiscounts"].min()), float(
        df["priceWithDiscounts"].max()
    )
    min_price, max_price = st.sidebar.slider(
        "Price Range",
        min_price_val,
        max_price_val,
        (min_price_val, max_price_val),
        step=1.00,
        format="%.0f",
    )
df["productUrl"] = df.get("productUrl", "")

# Apply filters
filtered_df = df.copy()
if selected_categories:
    filtered_df = filtered_df[filtered_df["type"].isin(selected_categories)]
if selected_brands:
    filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]
if selected_strains:
    filtered_df = filtered_df[filtered_df["strainType"].isin(selected_strains)]
if selected_effects:
    filtered_df = filtered_df[
        filtered_df["effects"].apply(
            lambda e: any(effect in e for effect in selected_effects)
        )
    ]
filtered_df = filtered_df[
    (filtered_df["priceWithDiscounts"] >= min_price)
    & (filtered_df["priceWithDiscounts"] <= max_price)
]

# Display results
st.title("Indigo Dispensary Products")
st.subheader(f"Showing {len(filtered_df)} products")

renamed_df = filtered_df[
    ["name", "productUrl", "brand", "type", "strainType", "priceWithDiscounts"]
].rename(
    columns={
        "name": "Name",
        "productUrl": "Link",
        "brand": "Brand",
        "type": "Category",
        "strainType": "Strain",
        "priceWithDiscounts": "Price",
    }
)

# renamed_df["Product Link"] = renamed_df.apply(
#     lambda row: f"[{row['Name']}]({row['Product Link']})" if row["Product Link"] else row["Name"],
#     axis=1
# )

st.dataframe(
    renamed_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="Link"),
    },
)


# Drop NaNs and round prices to two decimals for better grouping
chart_df = filtered_df.dropna(subset=["priceWithDiscounts", "strainType"]).copy()
chart_df["priceWithDiscounts"] = chart_df["priceWithDiscounts"].round(2)

# Group by price and strain type
chart_data = (
    chart_df.groupby(["priceWithDiscounts", "strainType"])
    .size()
    .reset_index(name="count")
)

# Create stacked column chart
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("priceWithDiscounts:O", title="Price ($)", sort="ascending"),
        y=alt.Y("count:Q", title="Number of Products"),
        color=alt.Color("strainType:N", title="Strain Type"),
        tooltip=["priceWithDiscounts", "strainType", "count"],
    )
    .properties(title="Product Count per Price by Strain Type", width=700, height=400)
)

st.altair_chart(chart, use_container_width=True)

import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Load your CSV
# uploaded_file = st.file_uploader("Upload your new products CSV", type=["csv"])

# if uploaded_file is  None:
df = pd.read_csv('normalized_products.csv')
  
if 'potency' in df.columns:
  df['price_per_mg'] = df['price'] / df['potency']
# Example mapping for normalizing categories
CATEGORY_MAP = {
    # Edibles
    "edibles": "Edibles",
    "🍬edibles🍫": "Edibles",
    "edible": "Edibles",
    "edible gummies": "Edibles",
    "edible products": "Edibles",
    "gummies": "Edibles",
    "edibles ": "Edibles",
    "edible ": "Edibles",
    # Accessories
    "accessories": "Accessories",
    "accessory": "Accessories",
    "apparel": "Accessories",
    # Pre-Rolls
    "pre_rolls": "Pre-Rolls",
    "pre-rolls": "Pre-Rolls",
    "prerolls": "Pre-Rolls",
    "pre rolls": "Pre-Rolls",
    # Vaporizers
    "vaporizers": "Vape",
    "vaporizer": "Vape",
    "vape": "Vape",
    # Flower
    "flower": "Flower",
    "flowers": "Flower",
    # Concentrates
    "concentrates": "Concentrates",
    "concentrate": "Concentrates",
    # Topicals
    "topicals": "Topical",
    "topical": "Topical",
    # Oral/Tinctures
    "oral": "Tinctures",
    "tinctures": "Tinctures",
    "tincture": "Tinctures",
}

STRAIN_TYPE_MAP = {
    "hybrid": "Hybrid",
    "hybrid ": "Hybrid",
    "🟣hybrid": "Hybrid",
    "sativa": "Sativa",
    "sativa ": "Sativa",
    "indica": "Indica",
    "indica ": "Indica",
    "not_applicable": None,
    "not applicable": None,
    "n/a": None,
    "one_to_one": "1:1",
    "hybrid_sativa": "Hybrid/Sativa",
    "sativa_hybrid": "Hybrid/Sativa",
    "indica_hybrid": "Hybrid/Indica",
    "thc": "THC",
    "two_to_one": "2:1",
    "other": "Other",
    "unknown": "Unknown",
    "": None,
}
def normalize_strain_type(st):
    if pd.isna(st):
        return None
    s = str(st).strip().lower().replace("-", "_")
    return STRAIN_TYPE_MAP.get(s, st if isinstance(st, str) else None)

def normalize_category(cat):
    if pd.isna(cat):
        return cat
    c = str(cat).strip().lower()
    return CATEGORY_MAP.get(c, cat if isinstance(cat, str) else "")

if "category" in df.columns:
    df["category"] = df["category"].apply(normalize_category)

if "strainType" in df.columns:
    df["strainType"] = df["strainType"].apply(normalize_strain_type)

st.title("🪴 Over the Bridge")

# Show when the data was last updated
try:
    with open("data/last_updated.txt", "r") as f:
        last_updated = f.read().strip()
    # st.info(f"**Data last updated:** {last_updated}")
    
    # Calculate and display time since last update
    try:
        last_dt = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - last_dt
        seconds = int(diff.total_seconds())
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if not parts:
            parts.append("just now")

        st.caption(f"⏱️ Updated {', '.join(parts)} ago. ({last_updated} EST)")
    except Exception:
        pass

except FileNotFoundError:
    st.warning("Last updated date not available.")
# st.write("Explore and filter your latest product additions.")

# Show quick summary
# st.subheader("Summary")


# Sidebar filters
st.sidebar.header("Filters")
search = st.sidebar.text_input("Search Name")
categories = df['category'].unique() if 'category' in df.columns else []
selected_cat = st.sidebar.multiselect("Category", categories, default=["Edibles"])
# StrainType filter
strains = df['strainType'].dropna().unique() if 'strainType' in df.columns else []
selected_strain = st.sidebar.multiselect("Strain", sorted(strains), default=["Hybrid", "Indica", "Hybrid/Indica", "Hybrid/Sativa"])
# Dispensary filter
dispensaries = df['dispensary'].dropna().unique() if 'dispensary' in df.columns else []
selected_disp = st.sidebar.multiselect("Dispensary", dispensaries)

# Filtering up to this point
filtered = df.copy()
if search:
    filtered = filtered[filtered['name'].str.contains(search, case=False, na=False)]
if selected_cat:
    filtered = filtered[filtered['category'].isin(selected_cat)]
if selected_strain:
    filtered = filtered[filtered['strainType'].isin(selected_strain)]
if selected_disp:
    filtered = filtered[filtered['dispensary'].isin(selected_disp)]

# Price range slider - based on filtered data
if "price" in filtered.columns and not filtered.empty:
    min_price, max_price = float(filtered["price"].min()), float(filtered["price"].max())
    price_range = st.sidebar.slider(
        "Price Range ($)", 
        min_value=min_price, 
        max_value=max_price, 
        value=(min_price, max_price),
        step=1.00,
        format="%.0f"
    )
    filtered = filtered[
        (filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])
    ]
else:
    price_range = (None, None)


# Check for Edibles missing quantity or potency (using *raw* columns before renaming)
if {'category', 'quantity', 'potency'}.issubset(df.columns):
    missing_edibles = df[
        (df['category'] == 'Edibles') &
        (df[['quantity', 'potency']].isnull().any(axis=1))
    ]
    count_missing = missing_edibles.shape[0]
    # if count_missing > 0:
        # st.warning(f"⚠️ There are {count_missing} Edibles missing either quantity or potency.")

st.subheader("Product List")

# Reorder columns before displaying the dataframe
desired_order = [
    "Name", "Category", "Brand", "Strain", "Potency", "Quant",
    "Price", "Price/mg", "Dispensary", "Link"
]

# Rename columns for clarity and correct capitalization
rename_map = {
    "name": "Name",
    "category": "Category",
    "brand": "Brand",
    "strainType": "Strain",
    "potency": "Potency",
    "quantity": "Quantity",
    "price": "Price",
    "price_per_mg": "Price/mg",
    "dispensary": "Dispensary",
    "productUrl": "Link"
}

filtered = filtered.rename(columns=rename_map)

# Only use columns that actually exist in the DataFrame
filtered = filtered[[col for col in desired_order if col in filtered.columns]]

# Hide columns if single filter selected
hide_columns = set()
if selected_cat and len(selected_cat) == 1:
    hide_columns.add("Category")
if selected_disp and len(selected_disp) == 1:
    hide_columns.add("Dispensary")
if selected_strain and len(selected_strain) == 1:
    hide_columns.add("Strain")

# Only use columns that actually exist in the DataFrame, minus any to hide
filtered_cols = [col for col in desired_order if col in filtered.columns and col not in hide_columns]
filtered = filtered[filtered_cols]

# If 'Link' exists, show as clickable link column
if "Link" in filtered.columns:
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn(
                label="Link",
                display_text="🔗",
                max_chars=None
            ),
        }
    )
else:
    st.dataframe(filtered.sort_values(["Price/mg", "Price"]), use_container_width=True, hide_index=True)

st.write(f"**Total Products:** {df.shape[0]}")
# Show details if row selected
# st.markdown("**Tip:** Click a row in the table to copy details.")
    
# else:
#     st.info("👆 Please upload a new products CSV to begin.")

# ---- Top 10 Edibles with Lowest Price per mg ----

# --- after renaming but before hiding columns ---
renamed_df = df.rename(columns=rename_map)

# ---- Top 10 Edibles with Lowest Price per mg ----
if {'Category', 'Price/mg'}.issubset(renamed_df.columns):
    edibles = renamed_df[renamed_df['Category'] == 'Edibles'].copy()
    edibles = edibles[pd.to_numeric(edibles['Price/mg'], errors='coerce').notnull()]
    edibles['Price/mg'] = edibles['Price/mg'].astype(float)
    edibles = edibles.sort_values('Price/mg').head(10)
    edibles.drop('Category', axis=1, inplace=True)
    st.subheader("🍬 Top 10 Edibles by Lowest Price per Mg")
    st.dataframe(
      edibles,
      column_config={
          "Potency": st.column_config.NumberColumn(format="%d"),
          "Quantity": st.column_config.NumberColumn(format="%d"),
          "Price": st.column_config.NumberColumn(format="$%.2f"),
          "Price/mg": st.column_config.NumberColumn(format="%.3f"),
          "Link": st.column_config.LinkColumn(
            label="Link",
            display_text="🔗",
            max_chars=None
          ),
      },
      hide_index=True,
      use_container_width=True,
    )
else:
    st.info("No edible data available for price per mg analysis.")
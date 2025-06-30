# Cana Scrape

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)![Streamlit](https://img.shields.io/badge/Streamlit-%F0%9F%A6%8A-orange)![Pandas](https://img.shields.io/badge/Pandas-%F0%9F%90%BC-lightgrey)

## Why This Project?

This project was created as a **learning exercise** and a practical demonstration of modern **data engineering skills**. The cannabis industry offers a unique case study: many dispensaries publish their menus with wildly inconsistent schemas, formats, and APIs. By aggregating and normalizing these sources, I can showcase the real-world techniques needed for data ingestion, cleaning, and analysis—exactly what’s required in analytics, business intelligence, and engineering roles.

**If you’re hiring a data engineer:**  
This repository demonstrates the ability to take messy, disparate web data and transform it into clean, actionable insights—end-to-end.

---

## What This Project Demonstrates

- **Data aggregation:** Scraping and merging data from diverse public web sources.
- **ETL pipeline:** Automating extract, transform, and load processes using Python.
- **Normalization:** Cleaning, mapping, and unifying inconsistent schemas.
- **Feature engineering:** Extracting and deriving fields (e.g., potency, pieces, price per mg).
- **Data manipulation:** Using Pandas to join, enrich, and filter real-world data.
- **Visualization:** Interactive dashboards (Streamlit) for analytics and reporting.
- **Practical problem-solving:** Dealing with missing, nested, or ambiguous information.

---

## Features

- **Automated scraping:** Modular scripts for various dispensary menus and APIs.
- **Robust normalization:** Handles different column names, value types, and structures.
- **Custom enrichment:** Uses regex and parsing to extract features from product names and descriptions.
- **Data aggregation:** Consolidates all data into a single, analysis-ready CSV.
- **Exploratory dashboard:** Streamlit UI for filtering, sorting, and comparing products.
- **Advanced metrics:** Computes price per mg, pack size, and highlights value options.
- **Reproducible workflow:** From scrape to dashboard with minimal setup.

---

## About This Project

Cana Scrape is designed as a portfolio piece to:

- Practice **end-to-end data workflows** (web > ETL > BI dashboard)
- Demonstrate **real-world data engineering techniques**
- Highlight **Python, Pandas, and Streamlit** as data engineering tools
- Show **applied analytics** on a novel, unstructured domain

---

> *This project is not for commercial use and does not promote or sell any cannabis products. It exists purely as a technical learning and demonstration platform.*

---

## Usage

### 1. Clone the Repository

```bash
git clone https://github.com/bRaInT00T/cana-scrape.git
cd cana-scrape
```

### 2. Install Dependencies

Create a virtual environment (recommended) and install requirements:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Scrape Data

Run all scraper modules to collect and store product data from supported dispensaries:

```bash
python run_scrapers.py
```

This will save individual JSON files to the `data/json/` directory.

### 4. Normalize and Aggregate Data

Process the scraped JSON files into a single normalized CSV:

```bash
python normalize_data.py
```

- This will create `data/products_normalized.csv` with all product info, engineered features, and clean columns.

### 5. Launch the Streamlit Dashboard

Visualize, filter, and explore the product data:

```bash
streamlit run consolidated_dash.py
```

- The dashboard will open in your browser, allowing interactive filtering, price analysis, and more.

---

## Notes

- All scrapers are for educational use; sites/APIs may change or block frequent access.
- If a data source changes format, update the relevant scraper and/or normalization logic.
- For demo purposes, a sample dataset is provided in the `data/` directory.

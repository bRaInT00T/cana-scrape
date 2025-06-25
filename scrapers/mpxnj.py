from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode
import json
import os
import re
import requests
import time

# MPX Medical & Recreational Dispensary - Pennsauken, NJ
# 5035 Central Hwy, Pennsauken, NJ 08109
# https://mpxnj.com

# ---------------- CONFIG ---------------- #
CATEGORY = "ALL"
# CATEGORY = "EDIBLES"

# Define output file
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
OUTFILE = data_dir / f"mpxnj_{CATEGORY.lower()}.json"
RETAILER_ID = "11883dc4-d7d7-4085-8e7b-ba5353eca58a" # Pennsauken Recreational
PAGE_SIZE = 20
BASE_URL = "https://mpxnj.com/wp-admin/admin-ajax.php"

# ---------------- GET COOKIES ---------------- #
def get_valid_cookies():
    """
    Retrieve valid cookies from the MPX NJ website.

    This function initializes a headless Chrome browser using Selenium, navigates
    to the MPX NJ website, and sets the 'age_confirm' local storage item to 'true'.
    It then retrieves cookies from the browser session and returns them as a dictionary.

    Returns:
        dict: A dictionary containing cookie names and their corresponding values.
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(options=options) as driver:
        driver.get("https://mpxnj.com")
        driver.execute_script("localStorage.setItem('age_confirm', 'true');")
        driver.get(f"https://mpxnj.com")
        time.sleep(0.5)  # Just enough to set the cookie
        return {c['name']: c['value'] for c in driver.get_cookies()}

# ---------------- FETCH NONCE ---------------- #
def fetch_nonce_with_selenium():
    """
    Fetch the nonce from the rendered page using selenium.

    This function opens a headless chrome instance, visits the MPX NJ website, and
    waits for 0.5 seconds to allow the JS to load.  It then searches for the nonce
    in the rendered page and returns the nonce value as a string.  If the nonce
    is not found, it raises a ValueError.

    Returns:
        str: The nonce value as a string.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get("https://mpxnj.com")
        time.sleep(0.5)  # Allow some time for JS to load

        page_source = driver.page_source

    match = re.search(r'"nonce"\s*:\s*"(\w+)"', page_source)
    if match:
        # print("✅ Nonce found in rendered page: ", match.group(1))
        return match.group(1)
    raise ValueError("Nonce not found in rendered page")


# ---------------- FETCH PAGE ---------------- #
def fetch_products_page(cookies, nonce, page):
    """
    Fetch the product data for a specific page from the MPX NJ website.

    This function sends a POST request to the MPX NJ server to retrieve product
    information for a given page number. The request is made with specific headers
    and payload data, including a nonce for authentication and page number for pagination.
    The response is checked for errors and the JSON data is returned.

    Args:
        cookies (dict): A dictionary of cookies to be included in the request.
        nonce (str): A nonce value for authentication.
        page (int): The page number to fetch products from.

    Returns:
        dict: The JSON response from the server containing product data.

    Raises:
        HTTPError: If the HTTP request returns an unsuccessful status code.
    """

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mpxnj.com',
        'Referer': f'https://mpxnj.com/shop/?pagination=1&sort=NAME_ASC&retailer_id={RETAILER_ID}&menu_type=RECREATIONAL&collection_type=PICKUP',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0'
    }
    current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
    payload = {
        "action": "wizard_show_products",
        "wizard_data[age_confirm]": "true",
        "wizard_data[created_time]": current_time,
        "wizard_data[default_set]": "true",
        "wizard_data[collection_method]": "PICKUP",
        "wizard_data[menu_type]": "RECREATIONAL",
        "wizard_data[retailer_id]": RETAILER_ID,
        "wizard_data[sort]": "NAME_ASC",
        "wizard_data[event]": "CART DATA - url and localStorage data MATCH",
        "wizard_data[prod_prefix]": "",
        "nonce_ajax": nonce,
        "prods_pageNumber": str(page),
        "prod_categories[search_key_word]": "",
        "prod_categories[sort_order]": "NAME_ASC",
        # "prod_categories[categories]": CATEGORY,
        "search_key_word": "",
        "filter_attributes[search_key_word]": "",
        "filter_attributes[sort_order]": "NAME_ASC"
    }

    response = requests.post(BASE_URL, headers=headers, cookies=cookies, data=urlencode(payload))
    response.raise_for_status()
    return response.json()

# ---------------- SCRAPE ALL PRODUCTS ---------------- #
def scrape_all_products():
    """
    Scrape all products from the MPX NJ website.

    1. Fetches a valid set of cookies.
    2. Fetches the nonce using selenium.
    3. Fetches the first page of products.
    4. Calculates the total number of products and pages.
    5. Fetches the remaining pages of products.
    6. Deduplicates the products by ID.
    7. Saves the products to the specified output file.

    Note: This function will fall back to using a hardcoded nonce if selenium fails
    to fetch a valid nonce.
    """
    cookies = get_valid_cookies()
    try:
        nonce = fetch_nonce_with_selenium()
    except Exception:
        print("⚠️ Falling back to hardcoded nonce.")
        nonce = "b5de8efb96"

    first_page_data = fetch_products_page(cookies, nonce, page=1)
    total = first_page_data['data'].get('products_count', 0)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"📦 Total products: {total} | Pages: {total_pages}")

    all_products = first_page_data['data'].get('products_list', [])

    for page in range(2, total_pages + 1):
        page_data = fetch_products_page(cookies, nonce, page)
        all_products.extend(page_data['data'].get('products_list', []))
        time.sleep(0.5)  # polite delay

    if os.path.isfile(OUTFILE):
        try:
            with open(OUTFILE, "r") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, ValueError):
            existing = []
        all_products += existing

    # Deduplicate by product ID
    seen, deduped = set(), []
    for p in all_products:
        pid = p.get("id")
        if pid and pid not in seen:
            seen.add(pid)
            deduped.append(p)
    deduped = sorted(deduped, key=lambda p: p['variants'][0]['priceRec'])
    with open(OUTFILE, "w") as f:
        json.dump(deduped, f, indent=2)

    print(f"✅ Saved {len(deduped)} unique products to {OUTFILE}")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    scrape_all_products()
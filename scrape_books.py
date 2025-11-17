import csv
import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
START_URL = BASE_URL
MIN_RECORDS = 1000
OUTPUT_FILE = "output/books.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BookScraper/1.0; +your-email@example.com)"
}


def get_with_retry(url, max_retries=3, delay=2):                                            # Error handling
    """
    Send GET request with simple retry logic.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[INFO] Requesting {url} (attempt {attempt})")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                return response

            print(f"[WARN] Status code {response.status_code} for {url}")

        except requests.RequestException as e:
            print(f"[ERROR] Request failed for {url}: {e}")

        time.sleep(delay)

    raise Exception(f"Failed to fetch {url} after {max_retries} retries")


def get_available_quantity(book_url):
    """
    Visit the book's detail page and extract numeric available quantity.
    Example availability text: "In stock (22 available)"
    """
    try:
        resp = get_with_retry(book_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        availability_tag = soup.select_one("p.instock.availability")
        if not availability_tag:
            return None

        availability_text = availability_tag.get_text(strip=True)
        
        match = re.search(r"(\d+)", availability_text)                                      # Extract first number in the text
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"[WARN] Could not get quantity for {book_url}: {e}")

    return None


def parse_book_list_page(html, current_url):
    """
    Parse one listing page: return list of book dicts and next page URL.
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for article in soup.select("article.product_pod"):
        # Title + detail link
        a_tag = article.select_one("h3 a")
        title = a_tag.get("title", "").strip()
        detail_href = a_tag.get("href")
        detail_url = urljoin(current_url, detail_href)

        
        price_tag = article.select_one("p.price_color")                                   # Price text (keep £, but fix encoding later via utf-8-sig)
        raw_price = price_tag.get_text(strip=True) if price_tag else ""
        clean_price = re.sub(r"[^0-9.]", "", raw_price)
        price = float(clean_price)
        
        rating_tag = article.select_one("p.star-rating")
        rating = ""
        if rating_tag:
            classes = rating_tag.get("class", [])
            if len(classes) > 1:
                rating = classes[1]

        
        stock_tag = article.select_one("p.instock.availability")
        stock = stock_tag.get_text(strip=True) if stock_tag else ""

        
        img_tag = article.select_one("img")
        img_src = img_tag.get("src") if img_tag else ""
        image_url = urljoin(current_url, img_src)

        
        available_quantity = get_available_quantity(detail_url)

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "stock": stock,
            "available_quantity": available_quantity,
            "product_page_url": detail_url,
            "image_url": image_url,
        })

    
    next_page_tag = soup.select_one("li.next a")                                              # Next page URL
    if next_page_tag:
        next_href = next_page_tag.get("href")
        next_url = urljoin(current_url, next_href)
    else:
        next_url = None

    return books, next_url


def scrape_books():
    print("[INFO] Starting book scraping...")

    
    robots_url = urljoin(BASE_URL, "robots.txt")                                               # Try robots.txt 
    try:
        r = requests.get(robots_url, headers=HEADERS, timeout=5)
        print(f"[INFO] robots.txt status: {r.status_code}")
    except requests.RequestException:
        print("[WARN] Could not fetch robots.txt; proceeding carefully.")

    all_books = []
    current_url = START_URL

    while current_url and len(all_books) < MIN_RECORDS:                                        # Automatic pagination
        response = get_with_retry(current_url)
        page_books, next_url = parse_book_list_page(response.text, current_url)

        all_books.extend(page_books)
        print(f"[INFO] Collected {len(all_books)} books so far...")

        
        time.sleep(1)                                                                          # Request delay

        current_url = next_url

    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)                                   # Output directory confirmation

   
    records_to_save = all_books[:MIN_RECORDS]

    
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:                       # Export data to CSV
        fieldnames = [
            "title",
            "price",
            "rating",
            "stock",
            "available_quantity",
            "product_page_url",
            "image_url",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records_to_save)

    print(f"[SUCCESS] Saved {len(records_to_save)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_books()

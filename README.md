# Web Scraping Assignment – Books to Scrape

## Website URL Used
https://books.toscrape.com/

## Overview
This project scrapes book information from the demo e-commerce website **Books to Scrape**.  
The script automatically paginates through all pages until **500+ book records** are collected and exports the cleaned data into a CSV file.

---

## Fields Extracted
For each book, the following fields are collected:

1. **Title**  
2. **Price (numeric, cleaned)**  
3. **Rating (Word rating, e.g., "Three", "Five")**  
4. **Stock availability**  
5. **Available quantity** (extracted from product detail page)  
6. **Product page URL**  
7. **Image URL**

---

## Total Records Collected
**1,000 records** (all books available on the website)

---

## Pagination Method Used
- Each page contains 20 books.  
- The script checks for `"li.next a"` on every page.  
- If found, the scraper uses `urljoin()` to follow the next page link.  
- This continues until all pages are exhausted or the target record count (1000) is reached.

---

## Challenges Faced & Solutions

### **1. Price Column Showing “Â£51.77”**
- Cause: Excel incorrectly interpreting UTF-8 as Windows-1252.  
- Solution: Cleaned the price using a regex to remove all non-numeric characters:  
  `clean_price = re.sub(r"[^0-9.]", "", raw_price)`  
- Also exported CSV using UTF-8-SIG for Excel compatibility.

### **2. Getting Available Quantity**
- Quantity is not available on the listing page.  
- Solution: For each book, the scraper visits the product detail page and extracts quantity using regex.

### **3. Handling Request Failures**
- Network failures can occur.  
- Solution: Implemented retry logic with a delay (`get_with_retry()`).

### **4. Avoiding Overloading the Server**
- Added `time.sleep(1)` delay between pages (responsible scraping).  
- Checked `robots.txt` before scraping.

---

## Step-by-Step Instructions to Run the Script

### **1. Clone or Download the Project**
Open the project folder in VS Code.

### **2. (Optional) Create a Virtual Environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```
### **3. Install Dependencies
```bash
pip install -r requirements.txt
```
### **4. Run the Scraper
```bash
output/books.csv
```

## Dependencies / Requirements
1. requests
2. beautifulsoap4
3. python version 3.9+ (recommended)

## Author
Name: Aurnab Biswas
Email: biswasarno75@gmail.com

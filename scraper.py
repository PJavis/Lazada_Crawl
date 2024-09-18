import os
import json
import csv
from collections import Counter
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from config import get_chrome_options, get_chrome_service
from utils import crawl_prices_by_combination

def load_last_processed_index(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

def save_last_processed_index(index, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(index))

def scrape_product(driver, url):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    product = {}

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.pdp-mod-review'))
        )
    except Exception:
        print(f"Không tìm thấy phần bình luận {url}")
        return product

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        title = soup.find('h1', class_='pdp-mod-product-badge-title')
        product['name'] = title.get_text(strip=True) if title else 'N/A'

        brand = soup.find('div', class_='pdp-product-brand')
        if brand:
            brand_link = brand.find('a', class_='pdp-product-brand__brand-link')
            product['brand'] = brand_link.get_text(strip=True) if brand_link else 'N/A'
        else:
            product['brand'] = 'N/A'

        product_detail = soup.find('div', class_='pdp-product-detail')
        product['description'] = product_detail.get_text(strip=True) if product_detail else 'N/A'

        review_elements = soup.find('div', class_='mod-reviews')
        reviews = []
        if review_elements:
            items = review_elements.find_all('div', class_='item')
            for item in items:
                review = {}
                stars_container = item.find('div', class_='container-star')
                if stars_container:
                    star_images = stars_container.find_all('img', class_='star')
                    src_list = [img['src'] for img in star_images]
                    src_count = Counter(src_list)
                    num_stars_gold = sum(count for src, count in src_count.items() if "TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png" in src)
                    review['rating'] = num_stars_gold

                content_element = item.find('div', class_='item-content')
                review['content'] = content_element.get_text(strip=True) if content_element else 'N/A'
                reviews.append(review)
        product['reviews'] = reviews

        seller_info_div = soup.find('div', id='module_seller_info')
        if seller_info_div:
            seller_name = seller_info_div.find('a', class_='seller-name__detail-name').text.strip()
            ratings = seller_info_div.find('div', class_='seller-info-value rating-positive').text.strip()
            product['seller_name'] = seller_name
            product['ratings'] = ratings

        product['url'] = url
    except Exception as e:
        print(f"Error: {e} trên trang {url}")

    return product

def write_to_csv(json_data, csv_filename):
    """Extracts the 'rating' and 'review' from json data and appends to CSV, cleaning up the review content."""
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for product in json_data:
            for review in product.get('reviews', []):
                if review.get('content') != 'N/A':
                    cleaned_content = review.get('content', '').replace('\n', ' ').strip()
                    csvwriter.writerow([review.get('rating', 'N/A'), cleaned_content])

def run_scraper():
    options = get_chrome_options()
    service = get_chrome_service()
    driver = webdriver.Chrome(options=options, service=service)

    results = []
    batch_size = 5
    csv_filename = 'reviews.csv'
    last_processed_index_file = 'last_processed_index.txt'

    last_processed_index = load_last_processed_index(last_processed_index_file)

    file_exists = os.path.exists(csv_filename)
    if not file_exists:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['rating', 'review'])  # Add headers if file doesn't exist

    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

        remaining_urls = urls[last_processed_index:]

        while remaining_urls:
            batch = remaining_urls[:batch_size]
            remaining_urls = remaining_urls[batch_size:]

            current_index = last_processed_index + len(batch)

            with open('urls1.txt', 'w', encoding='utf-8') as batch_file:
                batch_file.write(''.join(batch))

            for url in tqdm(batch, desc="Scraping products"):
                url = url.strip()
                product = scrape_product(driver, url)
                results.append(product)

            with open('products.json', 'w', encoding='utf-8') as json_file:
                json.dump(results, json_file, indent=4, ensure_ascii=False)

            write_to_csv(results, csv_filename)

            # Move this line inside the loop, so it updates after each batch
            save_last_processed_index(current_index, last_processed_index_file)

            results = []

            # Update last_processed_index for the next batch
            last_processed_index = current_index

    driver.quit()


if __name__ == "__main__":
    run_scraper()

from collections import Counter
from datetime import datetime, timezone
import time
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from config import get_chrome_options, get_chrome_service
from utils import crawl_prices_by_combination

def scrape_product(driver, url):
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    prices = crawl_prices_by_combination(driver)
    product = {}
    # Nhấp vào nút "Xem thêm" nếu có
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pdp-view-more-btn"))
        )
        button.click()
        time.sleep(1)
    except Exception:
        print(f"Không tìm thấy nút 'Xem thêm' hoặc không thể nhấp vào nút trên trang {url}")

    # Phân tích trang với BeautifulSoup
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

        # Lấy tất cả các ảnh
        image_elements = soup.select('.item-gallery img')
        image_sources = [img['src'] for img in image_elements]
        product['images'] = image_sources

        # Lấy thông tin người bán và thông số của họ
        seller_info_div = soup.find('div', id='module_seller_info')
        if seller_info_div:
            seller_name = seller_info_div.find('a', class_='seller-name__detail-name').text.strip()
            ratings = seller_info_div.find('div', class_='seller-info-value rating-positive').text.strip()
            seller_info = seller_info_div.find_all('div', class_='seller-info-value')
            ship_on_time = seller_info[1].text.strip() if len(seller_info) > 1 else 'N/A'
            chat_response = seller_info[2].text.strip() if len(seller_info) > 2 else 'N/A'

            product['seller_name'] = seller_name
            product['ratings'] = ratings
            product['ship_on_time'] = ship_on_time
            product['chat_response'] = chat_response

        product['url'] = url
        product['prices'] = prices
    except Exception as e:
        print(f"Error: {e} trên trang {url}")

    return product


def run_scraper():
    options = get_chrome_options()
    service = get_chrome_service()
    driver = webdriver.Chrome(options=options, service=service)

    url_temp = "https://www.lazada.vn/catalog/?q=shirt"
    driver.get(url_temp)
    time.sleep(10)

    results = []

    with open('urls1.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()
        for url in urls:
            url = url.strip()
            product = scrape_product(driver, url)
            results.append(product)

    driver.quit()

    # Lưu dữ liệu vào file JSON
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper()

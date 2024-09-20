import os
import csv
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from config import get_chrome_options, get_chrome_service

def load_last_processed_index(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

def save_last_processed_index(index, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(index))

def scrape_reviews(driver, url):
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    reviews = [] 

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.pdp-mod-review'))
        )
    except Exception:
        print(f"Không tìm thấy phần bình luận {url}")
        return reviews

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    try:
        review_elements = soup.find('div', class_='mod-reviews')

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
                
                item_content = item.find('div', class_='item-content')
                if item_content:
                    content_element = item_content.find('div', class_='content')

                review['content'] = content_element.get_text(strip=True) if content_element else 'N/A'
                review['url'] = url
                reviews.append(review)
    except Exception as e:
        print(f"Error: {e} trên trang {url}")

    return reviews 

def write_to_csv(csv_filename, reviews):
    """Appends reviews to the CSV file."""
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for review in reviews:
            if review.get('content') != 'N/A':
                cleaned_content = review.get('content', '').replace('\n', ' ').strip()
                csvwriter.writerow([review.get('rating', 'N/A'), cleaned_content])

def run_scraper():
    options = get_chrome_options()
    service = get_chrome_service()
    driver = webdriver.Chrome(options=options, service=service)

    batch_size = 5
    csv_filename = 'reviews_2.csv'
    last_processed_index_file = 'last_processed_index.txt'

    last_processed_index = load_last_processed_index(last_processed_index_file)

    file_exists = os.path.exists(csv_filename)
    if not file_exists:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['rating', 'review'])  

    with open('urls.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()
        remaining_urls = urls[last_processed_index:]

        while remaining_urls:
            batch = remaining_urls[:batch_size]
            remaining_urls = remaining_urls[batch_size:]

            current_index = last_processed_index + len(batch)

            for url in tqdm(batch, desc="Scraping products"):
                url = url.strip()
                reviews = scrape_reviews(driver, url)  
                write_to_csv(csv_filename, reviews)  
            
            save_last_processed_index(current_index, last_processed_index_file)
            last_processed_index = current_index

    driver.quit()

if __name__ == "__main__":
    run_scraper()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from config import get_chrome_options, get_chrome_service
# from utils import crawl_prices_by_combination


options = get_chrome_options()
service = get_chrome_service()
driver = webdriver.Chrome(options=options, service=service)

# URL của trang web
URL1 = "https://www.lazada.vn/catalog/?page="
URL2 = "&q=jeans"

# Sử dụng tập hợp để lưu các liên kết không trùng lặp
unique_hrefs = set()

# Lặp qua các trang
for i in range(1, 10):
    # Kết hợp URL và mở trang
    full_url = URL1 + str(i) + URL2
    driver.get(full_url)
    
    # Đợi cho đến khi các phần tử cần thiết xuất hiện trên trang
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div._95X4G'))
        )
    except Exception as e:
        print(f"Không thể tải trang hoặc không tìm thấy phần tử: {e}")
        continue

    # Lấy mã nguồn trang và phân tích bằng BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Tìm tất cả các phần tử <a> bên trong <div class="_95X4G">
    product_elements = soup.find_all('a', href=True, attrs={'age': '0'})
    
    # Thu thập các giá trị href
    for element in product_elements:
        href = element.get('href')
        if href:
            full_href = f"https://www.lazada.vn{href}"  # Đảm bảo liên kết đầy đủ
            unique_hrefs.add(full_href)

# Đóng WebDriver
driver.quit()

# Lưu các giá trị href không trùng lặp vào tệp văn bản
with open('urls.txt', 'w', encoding='utf-8') as file:
    for link in unique_hrefs:
        file.write(link + '\n')

print(f"Đã lưu {len(unique_hrefs)} liên kết vào urls.txt")

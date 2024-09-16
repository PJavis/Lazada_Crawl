import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import*
# Khởi tạo trình duyệt
driver = webdriver.Chrome()  # Hoặc trình duyệt bạn muốn

# Mở trang web chứa đoạn HTML
driver.get('https://www.lazada.vn/products/cod-s24-ultra-moi-chinh-hang-5g-dien-thoai-8128gb-thong-minh-toan-man-hinh-68-inch-full-hd-dual-sim-dien-thoai-di-dong-phien-ban-toan-cau-dien-thoai-i2785828290-s13594929926.html?')
time.sleep(60)

print(crawl_prices_by_combination(driver=driver))

# Đóng trình duyệt
driver.quit()
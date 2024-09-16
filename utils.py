from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_current_info(driver):
    try:
        # Luôn luôn lấy giá
        current_price_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'pdp-price_type_normal'))
        )
        current_price = current_price_element.text

        # Thử lấy màu và cấu hình, có thể không tồn tại
        try:
            current_color_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'sku-name'))
            )
            current_color = current_color_element.text
        except:
            current_color = "N/A"

        try:
            current_config_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[4]/div/div[3]/div[2]/div/div[1]/div[14]/div/div[2]/div/div/div[1]/span'))
            )
            current_config = current_config_element.text
        except:
            current_config = "N/A"

        return current_color, current_price, current_config
    except Exception as e:
        print(f"Đã xảy ra lỗi khi lấy giá và thông tin hiện tại: {e}")
        return "N/A", "N/A", "N/A"

def get_color_options(driver):
    try:
        color_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'sku-variable-img-wrap'))
        )
        return color_options
    except Exception as e:
        print(f"Đã xảy ra lỗi khi lấy các tùy chọn màu: {e}")
        return []

def get_config_options(driver):
    try:
        config_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'sku-variable-name'))
        )
        return config_options
    except Exception as e:
        print(f"Đã xảy ra lỗi khi lấy các tùy chọn cấu hình: {e}")
        return []

def add_price_record(prices, color, price, config):
    prices.append({
        'color': color,
        'price': price,
        'config': config,
        'date': datetime.now(pytz.utc).isoformat().replace('+00:00', 'Z')
    })

def crawl_prices_by_combination(driver):
    prices = []  # Khởi tạo danh sách prices tại đây
    current_color, current_price, current_config = get_current_info(driver)
    
    add_price_record(prices, current_color, current_price, current_config)

    color_options = get_color_options(driver)
    config_options = get_config_options(driver)

    current_config_option = None
    current_color_option = None

    try:
        current_config_option = driver.find_element(By.CLASS_NAME, 'sku-variable-name-selected')
    except Exception:
        print("Sản phẩm chỉ có 1 cấu hình")

    try:
        current_color_option = driver.find_element(By.CLASS_NAME, 'sku-variable-img-wrap-selected')
    except Exception:
        print("Sản phẩm chỉ có 1 màu")

    if current_config_option is not None:
        for config in config_options:
            config.click()
            current_color, current_price, current_config = get_current_info(driver)
            add_price_record(prices, current_color, current_price, current_config)

        current_config_option.click()
        for color in color_options:
            color.click()
            current_color, current_price, current_config = get_current_info(driver)
            add_price_record(prices, current_color, current_price, current_config)

    if not color_options and not config_options:
        print("Không tìm thấy các tùy chọn màu hoặc cấu hình.")
        return prices

    if not color_options:
        if current_color is None:
            current_color = "N/A"
        for config in config_options:
            config.click()
            add_price_record(prices, current_color, get_current_info(driver)[1], get_current_info(driver)[2])
        return prices

    if not config_options:
        if current_config is None:
            current_config = "N/A"
        for color in color_options:
            color.click()
            add_price_record(prices, get_current_info(driver)[0], current_price, current_config)
        return prices

    for color in color_options:
        color.click()
        for config in config_options:
            config.click()
            current_color, current_price, current_config = get_current_info(driver)
            if current_color and current_price and current_config:
                add_price_record(prices, current_color, current_price, current_config)

    return prices

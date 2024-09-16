from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_options():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    return options

def get_chrome_service():
    return Service("chromedriver-win64\\chromedriver.exe")

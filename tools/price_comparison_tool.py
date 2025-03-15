

from typing import Any
from smolagents.tools import Tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import time


class PriceComparisonTool(Tool):
    name = "price_comparison"
    description = "Finds the lowest price for a skincare product across Target, Walmart, Sephora, and Ulta."
    inputs = {'product_name': {'type': 'string', 'description': 'The name of the skincare product to search for.'}}
    output_type = "string"

    def forward(self, product_name: str) -> str:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        search_urls = {
            "Target": f"https://www.target.com/s?searchTerm={product_name.replace(' ', '+')}",
            "Walmart": f"https://www.walmart.com/search?q={product_name.replace(' ', '%20')}",
            "Sephora": f"https://www.sephora.com/search?keyword={product_name.replace(' ', '%20')}",
            "Ulta": f"https://www.ulta.com/search?searchTerm={product_name.replace(' ', '%20')}"
        }

        prices = {}

        try:
            for store, url in search_urls.items():
                try:
                    driver.get(url)
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '$')]"))
                    )
                    
                    # Store-specific price extraction
                    if store == "Target":
                        elements = driver.find_elements(By.CSS_SELECTOR, "[data-test='product-price']")
                    elif store == "Walmart":
                        elements = driver.find_elements(By.CSS_SELECTOR, "[itemprop='price']")
                    elif store == "Sephora":
                        elements = driver.find_elements(By.CSS_SELECTOR, "[data-comp='Price ']")
                    elif store == "Ulta":
                        elements = driver.find_elements(By.CSS_SELECTOR, ".ProductCardContent__Price")

                    found_prices = []
                    for element in elements:
                        price_text = element.text.replace('\n', '.').replace(' ', '')
                        matches = re.findall(r"\$\d+\.\d{2}", price_text)
                        if matches:
                            found_prices.extend([float(m.replace('$', '')) for m in matches])

                    if found_prices:
                        min_price = min(found_prices)
                        prices[store] = min_price
                    else:
                        prices[store] = None

                except Exception as e:
                    print(f"Error scraping {store}: {str(e)}")
                    prices[store] = None
                
                time.sleep(2)  # Add delay between requests

        finally:
            driver.quit()

        # Filtering out stores where prices were not found
        available_prices = {k: v for k, v in prices.items() if v is not None}

        if not available_prices:
            return f"Could not find '{product_name}' at Target, Walmart, Sephora, or Ulta."

        # Find the store with the lowest price
        lowest_store = min(available_prices, key=available_prices.get)
        lowest_price = available_prices[lowest_store]

        return f"The lowest price for '{product_name}' is ${lowest_price:.2f} at {lowest_store}."

        # Rest of the logic remains the same...
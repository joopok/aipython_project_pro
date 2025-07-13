import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from flask import current_app


class NaverScraper:
    def __init__(self):
        self.base_url = "https://search.shopping.naver.com/search/all"
        
    def search(self, keyword, max_items=20):
        """Search products on Naver Shopping"""
        results = []
        
        try:
            params = {
                'query': keyword,
                'sort': 'rel',  # relevance
                'pagingSize': max_items
            }
            
            response = requests.get(self.base_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Note: Naver's actual structure may vary, this is a simplified example
            products = soup.select('.basicList_item__2XT81')[:max_items]
            
            for product in products:
                try:
                    result = {
                        'platform': 'naver',
                        'name': product.select_one('.basicList_title__3P9Q7').text.strip(),
                        'price': int(product.select_one('.price_num__2WUXn').text.replace(',', '').replace('원', '')),
                        'url': product.select_one('.basicList_link__1MaTN')['href'],
                        'image_url': product.select_one('.thumbnail_thumb__3Agq6 img')['src'],
                        'rating': float(product.select_one('.basicList_star__3NkBn').text) if product.select_one('.basicList_star__3NkBn') else None,
                        'review_count': int(product.select_one('.basicList_etc__2uAYO').text.replace(',', '')) if product.select_one('.basicList_etc__2uAYO') else None,
                    }
                    results.append(result)
                except Exception as e:
                    continue
                    
        except Exception as e:
            current_app.logger.error(f"Naver scraping error: {str(e)}")
            
        return results


class CoupangScraper:
    def __init__(self):
        self.base_url = "https://www.coupang.com/np/search"
        
    def search(self, keyword, max_items=20):
        """Search products on Coupang"""
        results = []
        
        try:
            # Set up Chrome options
            chrome_options = Options()
            if current_app.config.get('HEADLESS_BROWSER'):
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                url = f"{self.base_url}?q={keyword}"
                driver.get(url)
                
                # Wait for products to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-product"))
                )
                
                # Scroll to load more products
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.select('.search-product')[:max_items]
                
                for product in products:
                    try:
                        price_elem = product.select_one('.price-value')
                        if price_elem:
                            price_text = price_elem.text.strip().replace(',', '').replace('원', '')
                            price = int(price_text) if price_text.isdigit() else 0
                        else:
                            price = 0
                            
                        result = {
                            'platform': 'coupang',
                            'name': product.select_one('.name').text.strip(),
                            'price': price,
                            'url': 'https://www.coupang.com' + product.select_one('.search-product-link')['href'],
                            'image_url': 'https:' + product.select_one('.search-product-wrap-img')['src'],
                            'rating': float(product.select_one('.rating').text) if product.select_one('.rating') else None,
                            'review_count': int(product.select_one('.rating-total-count').text.replace('(', '').replace(')', '').replace(',', '')) if product.select_one('.rating-total-count') else None,
                        }
                        results.append(result)
                    except Exception as e:
                        continue
                        
            finally:
                driver.quit()
                
        except Exception as e:
            current_app.logger.error(f"Coupang scraping error: {str(e)}")
            
        return results
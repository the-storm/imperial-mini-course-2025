import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import uuid
import time
import sys


class AdminBot:
    visiting = False
    logged_in = False
    
    def __init__(self):
        self.user_data_dir = '/tmp/chrome_admin_session'
        service = webdriver.ChromeService(executable_path="/usr/bin/chromedriver")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--js-flags=--noexpose_wasm,--jitless')
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(10)

    def login(self):
        try:
            hostname = os.getenv('HOSTNAME', 'localhost')
            domain = f'http://localhost:80' if hostname == 'localhost' else f'https://{hostname}'

            password = os.getenv('ADMIN_PASSWORD', 'kalmar')

            self.driver.get(domain+'/login')
            
            username_field = self.driver.find_element(By.NAME, 'username')
            password_field = self.driver.find_element(By.NAME, 'password')
            
            username_field.send_keys('admin')
            password_field.send_keys(password)
            password_field.submit()
            
            self.logged_in = True
            
        except Exception as e:
            print(f"Login failed: {str(e)}", file=sys.stderr, flush=True)
            self.logged_in = False

    
    def visit(self, note_url):
        if self.visiting:
            return False
            
        self.visiting = True
        try:
            if not self.logged_in:
                self.login()
                if not self.logged_in:
                    raise Exception("Failed to login")

            self.driver.get(note_url)
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"Failed to visit note: {e}", file=sys.stderr, flush=True)
            return False
            
        finally:
            self.visiting = False

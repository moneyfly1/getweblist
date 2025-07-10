#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver 安装验证脚本
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

def main():
    # 默认CI环境下chromedriver路径
    chromedriver_path = os.environ.get("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
    service = Service(chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.google.com")
    print("Title:", driver.title)
    driver.quit()

if __name__ == "__main__":
    main() 
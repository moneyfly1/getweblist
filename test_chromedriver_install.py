#!/usr/bin/env python3
"""
ChromeDriver安装验证脚本
适用于CI和本地环境
"""

import os
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def check_chromedriver_availability():
    """检查ChromeDriver是否可用"""
    print("=" * 50)
    print("ChromeDriver 可用性检查")
    print("=" * 50)
    
    # 检查环境变量
    chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
    print(f"ChromeDriver路径: {chrome_driver_path}")
    
    # 检查文件是否存在
    if os.path.exists(chrome_driver_path):
        print(f"✅ ChromeDriver文件存在: {chrome_driver_path}")
        if os.access(chrome_driver_path, os.X_OK):
            print(f"✅ ChromeDriver文件可执行")
        else:
            print(f"❌ ChromeDriver文件不可执行")
            return False
    else:
        print(f"❌ ChromeDriver文件不存在: {chrome_driver_path}")
        return False
    
    # 检查版本
    try:
        result = subprocess.run([chrome_driver_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ ChromeDriver版本: {result.stdout.strip()}")
        else:
            print(f"❌ ChromeDriver版本检查失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ChromeDriver版本检查异常: {e}")
        return False
    
    return True

def test_selenium_chrome():
    """测试Selenium + ChromeDriver"""
    print("\n" + "=" * 50)
    print("Selenium + ChromeDriver 测试")
    print("=" * 50)
    
    try:
        # 设置ChromeDriver路径
        chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
        service = Service(chrome_driver_path)
        
        # 配置Chrome选项
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # 创建WebDriver
        print("正在创建Chrome WebDriver...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # 访问测试页面
        print("正在访问测试页面...")
        driver.get("https://www.google.com")
        
        # 检查页面标题
        title = driver.title
        print(f"页面标题: {title}")
        
        # 关闭浏览器
        driver.quit()
        print("✅ Selenium + ChromeDriver 测试成功")
        return True
        
    except Exception as e:
        print(f"❌ Selenium + ChromeDriver 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始ChromeDriver安装验证...")
    
    # 检查ChromeDriver可用性
    availability_ok = check_chromedriver_availability()
    
    # 测试Selenium + ChromeDriver
    selenium_ok = False
    if availability_ok:
        selenium_ok = test_selenium_chrome()
    
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    
    if availability_ok and selenium_ok:
        print("🎉 所有测试通过！ChromeDriver安装正确且可用。")
        return 0
    elif availability_ok:
        print("⚠️ ChromeDriver文件存在但Selenium测试失败")
        print("这可能是因为缺少Chrome浏览器或其他环境问题")
        return 1
    else:
        print("❌ ChromeDriver安装或配置有问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
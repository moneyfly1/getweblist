#!/usr/bin/env python3
"""
代理配置脚本
帮助用户设置代理以绕过Google检测
"""

import os
import sys
import requests
from urllib.parse import urlparse

def test_proxy(proxy_url):
    """测试代理是否可用"""
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        response = requests.get('https://www.google.com', proxies=proxies, timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"代理测试失败: {e}")
        return False

def setup_proxy():
    """设置代理"""
    print("=" * 50)
    print("代理配置工具")
    print("=" * 50)
    
    print("由于Google的反爬虫机制，建议使用代理来避免被拦截。")
    print("请选择代理类型：")
    print("1. HTTP代理")
    print("2. SOCKS5代理")
    print("3. 不使用代理（不推荐）")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        proxy_url = input("请输入HTTP代理地址 (格式: http://ip:port): ").strip()
        if not proxy_url.startswith('http://'):
            proxy_url = 'http://' + proxy_url
        
        print(f"测试代理: {proxy_url}")
        if test_proxy(proxy_url):
            print("✅ 代理测试成功！")
            
            # 设置环境变量
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            print("代理已设置到环境变量")
            print(f"HTTP_PROXY={proxy_url}")
            print(f"HTTPS_PROXY={proxy_url}")
            
            return True
        else:
            print("❌ 代理测试失败，请检查代理地址")
            return False
            
    elif choice == "2":
        proxy_url = input("请输入SOCKS5代理地址 (格式: socks5://ip:port): ").strip()
        if not proxy_url.startswith('socks5://'):
            proxy_url = 'socks5://' + proxy_url
        
        print(f"测试代理: {proxy_url}")
        if test_proxy(proxy_url):
            print("✅ 代理测试成功！")
            
            # 设置环境变量
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            
            print("代理已设置到环境变量")
            print(f"HTTP_PROXY={proxy_url}")
            print(f"HTTPS_PROXY={proxy_url}")
            
            return True
        else:
            print("❌ 代理测试失败，请检查代理地址")
            return False
            
    elif choice == "3":
        print("⚠️ 警告：不使用代理可能被Google拦截")
        return True
        
    else:
        print("❌ 无效选择")
        return False

def main():
    """主函数"""
    print("SSPanel Mining 代理配置工具")
    print("=" * 50)
    
    if setup_proxy():
        print("\n✅ 代理配置完成！")
        print("现在可以运行采集器了：")
        print("python src/main.py mining --collector --classifier")
    else:
        print("\n❌ 代理配置失败")
        print("请检查代理地址或网络连接")

if __name__ == "__main__":
    main() 
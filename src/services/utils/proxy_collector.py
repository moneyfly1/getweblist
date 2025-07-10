#!/usr/bin/env python3
"""
代理搜集器
从多个免费代理网站搜集代理IP和端口
"""

import requests
import re
import time
import random
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

class ProxyCollector:
    """代理搜集器"""
    
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        
        # 代理网站列表
        self.proxy_sources = [
            {
                'name': 'FreeProxyList',
                'url': 'https://free-proxy-list.net/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'ProxyNova',
                'url': 'https://www.proxynova.com/proxy-server-list/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'ProxyList',
                'url': 'https://www.proxy-list.download/api/v1/get?type=http',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'SpysOne',
                'url': 'http://spys.one/free-proxy-list/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
        ]
    
    def fetch_proxies_from_source(self, source: Dict) -> List[str]:
        """从单个代理源获取代理列表"""
        try:
            logger.info(f"正在从 {source['name']} 获取代理...")
            
            response = requests.get(
                source['url'], 
                headers=source['headers'], 
                timeout=10
            )
            
            if response.status_code == 200:
                # 使用正则表达式提取IP:端口
                matches = re.findall(source['pattern'], response.text)
                proxies = [f"{ip}:{port}" for ip, port in matches]
                
                logger.info(f"从 {source['name']} 获取到 {len(proxies)} 个代理")
                return proxies
            else:
                logger.warning(f"从 {source['name']} 获取代理失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"从 {source['name']} 获取代理时出错: {e}")
            return []
    
    def test_proxy(self, proxy: str) -> Optional[Dict]:
        """测试单个代理是否可用"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # 测试连接Google
            response = requests.get(
                'https://www.google.com', 
                proxies=proxies, 
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 代理 {proxy} 测试成功")
                return {
                    'proxy': proxy,
                    'type': 'http',
                    'speed': response.elapsed.total_seconds()
                }
            else:
                return None
                
        except Exception as e:
            logger.debug(f"❌ 代理 {proxy} 测试失败: {e}")
            return None
    
    def collect_proxies(self, max_workers: int = 5) -> List[str]:
        """搜集代理列表"""
        logger.info("开始搜集代理...")
        
        # 从多个源并行获取代理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(self.fetch_proxies_from_source, source): source 
                for source in self.proxy_sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    proxies = future.result()
                    self.proxies.extend(proxies)
                except Exception as e:
                    logger.error(f"从 {source['name']} 获取代理时出错: {e}")
        
        # 去重
        self.proxies = list(set(self.proxies))
        logger.info(f"总共搜集到 {len(self.proxies)} 个唯一代理")
        
        return self.proxies
    
    def test_proxies(self, max_workers: int = 10) -> List[Dict]:
        """测试所有代理的可用性"""
        logger.info("开始测试代理可用性...")
        
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in self.proxies
            }
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    result = future.result()
                    if result:
                        working_proxies.append(result)
                except Exception as e:
                    logger.debug(f"测试代理 {proxy} 时出错: {e}")
        
        # 按速度排序
        working_proxies.sort(key=lambda x: x['speed'])
        self.working_proxies = working_proxies
        
        logger.info(f"找到 {len(working_proxies)} 个可用代理")
        return working_proxies
    
    def get_best_proxy(self) -> Optional[str]:
        """获取最佳代理"""
        if self.working_proxies:
            best_proxy = self.working_proxies[0]
            return f"http://{best_proxy['proxy']}"
        return None
    
    def get_random_proxy(self) -> Optional[str]:
        """获取随机代理"""
        if self.working_proxies:
            random_proxy = random.choice(self.working_proxies)
            return f"http://{random_proxy['proxy']}"
        return None
    
    def save_proxies_to_file(self, filename: str = "working_proxies.txt"):
        """保存可用代理到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            for proxy_info in self.working_proxies:
                f.write(f"{proxy_info['proxy']}\n")
        
        logger.info(f"已保存 {len(self.working_proxies)} 个可用代理到 {filename}")
    
    def load_proxies_from_file(self, filename: str = "working_proxies.txt") -> List[str]:
        """从文件加载代理列表"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                proxies = [line.strip() for line in f if line.strip()]
            
            logger.info(f"从文件加载了 {len(proxies)} 个代理")
            return proxies
        except FileNotFoundError:
            logger.warning(f"代理文件 {filename} 不存在")
            return []

def main():
    """主函数"""
    collector = ProxyCollector()
    
    # 搜集代理
    proxies = collector.collect_proxies()
    
    if proxies:
        # 测试代理
        working_proxies = collector.test_proxies()
        
        if working_proxies:
            # 保存可用代理
            collector.save_proxies_to_file()
            
            # 显示最佳代理
            best_proxy = collector.get_best_proxy()
            print(f"\n最佳代理: {best_proxy}")
            
            # 显示前5个最快代理
            print("\n前5个最快代理:")
            for i, proxy_info in enumerate(working_proxies[:5], 1):
                print(f"{i}. {proxy_info['proxy']} (速度: {proxy_info['speed']:.2f}s)")
        else:
            print("❌ 没有找到可用的代理")
    else:
        print("❌ 没有搜集到任何代理")

if __name__ == "__main__":
    main() 
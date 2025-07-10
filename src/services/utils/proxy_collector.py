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
import os
import json

class ProxyCollector:
    """代理搜集器"""
    BLACKLIST_FILE = "blacklist_sites.txt"
    
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
            },
            # 新增的代理源
            {
                'name': '66ip',
                'url': 'http://www.66ip.cn/mo.php?tqsl=100',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': '89ip',
                'url': 'https://www.89ip.cn/tqdl.html?api=1&num=100',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'Goubanjia',
                'url': 'http://www.goubanjia.com/free/gngn/index.shtml',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'PubProxy',
                'url': 'http://pubproxy.com/api/proxy?limit=100&format=json',
                'pattern': r'"ip":"([^"]+)","port":"([^"]+)"',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
            },
            {
                'name': 'Proxy11',
                'url': 'https://proxy11.com/api/proxy?limit=100',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
            },
            {
                'name': 'ProxyListDownload',
                'url': 'https://www.proxy-list.download/api/v1/get?type=https&country=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            # 额外的代理源
            {
                'name': 'ProxyListDownloadHTTP',
                'url': 'https://www.proxy-list.download/api/v1/get?type=http&country=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            {
                'name': 'ProxyListDownloadSOCKS',
                'url': 'https://www.proxy-list.download/api/v1/get?type=socks5&country=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            # 新增的高质量代理源
            {
                'name': 'SPYS',
                'url': 'http://spys.one/free-proxy-list/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'HidemyName',
                'url': 'https://hidemy.name/en/proxy-list/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'FreeProxyCZ',
                'url': 'https://free-proxy.cz/en/proxylist/country-all/http/ping-all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'SocksProxy',
                'url': 'https://www.socks-proxy.net/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'Hidester',
                'url': 'https://hidester.com/proxylist/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'Premproxy',
                'url': 'https://premproxy.com/proxy-by-country/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'ProxyScrape',
                'url': 'https://proxyscrape.com/free-proxy-list',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'OpenProxy',
                'url': 'https://openproxy.space/list',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            {
                'name': 'ProxyDB',
                'url': 'https://proxydb.net/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            # API类型的代理源
            {
                'name': 'ProxyScrapeAPI',
                'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            {
                'name': 'ProxyScrapeHTTPS',
                'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            {
                'name': 'ProxyScrapeSOCKS5',
                'url': 'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/plain',
                }
            },
            {
                'name': 'Kuaidaili',
                'url': 'https://www.kuaidaili.com/free/fps/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'IP3366',
                'url': 'http://www.ip3366.net/free/?stype=1&page=1',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'IPFoxy',
                'url': 'https://www.ipfoxy.com/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'IPIdea',
                'url': 'https://www.ipidea.net/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
            {
                'name': 'IPXProxy',
                'url': 'https://www.ipxproxy.com/',
                'pattern': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)',
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            },
        ]
        self.site_fail_count = {}
        self.site_blacklist = set()
        self.FAIL_THRESHOLD = 3
        self.POOL_FAIL_RATE = 0.99
        self.load_blacklist()
    
    def load_blacklist(self):
        if os.path.exists(self.BLACKLIST_FILE):
            try:
                with open(self.BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.site_blacklist = set(data)
                logger.info(f"已加载黑名单: {self.site_blacklist}")
            except Exception as e:
                logger.warning(f"加载黑名单失败: {e}")

    def save_blacklist(self):
        try:
            with open(self.BLACKLIST_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(self.site_blacklist), f, ensure_ascii=False, indent=2)
            logger.info(f"已保存黑名单: {self.site_blacklist}")
        except Exception as e:
            logger.warning(f"保存黑名单失败: {e}")

    def fetch_proxies_from_source(self, source: Dict) -> List[str]:
        if source['name'] in self.site_blacklist:
            logger.warning(f"{source['name']} 已被拉黑，跳过采集")
            return []
        try:
            logger.info(f"正在从 {source['name']} 获取代理...")
            
            response = requests.get(
                source['url'], 
                headers=source['headers'], 
                timeout=15
            )
            
            if response.status_code == 200:
                proxies = []
                
                # 处理不同格式的代理数据
                if source['name'] == 'PubProxy':
                    # PubProxy返回JSON格式
                    try:
                        data = response.json()
                        if 'data' in data:
                            for item in data['data']:
                                if 'ip' in item and 'port' in item:
                                    proxies.append(f"{item['ip']}:{item['port']}")
                    except Exception as e:
                        logger.warning(f"解析PubProxy JSON失败: {e}")
                        # 尝试正则表达式解析
                        matches = re.findall(source['pattern'], response.text)
                        proxies = [f"{ip}:{port}" for ip, port in matches]
                
                elif source['name'] == 'Proxy11':
                    # Proxy11可能返回JSON或文本格式
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and 'ip' in item and 'port' in item:
                                    proxies.append(f"{item['ip']}:{item['port']}")
                        elif isinstance(data, dict) and 'data' in data:
                            for item in data['data']:
                                if 'ip' in item and 'port' in item:
                                    proxies.append(f"{item['ip']}:{item['port']}")
                    except:
                        # 如果不是JSON，使用正则表达式
                        matches = re.findall(source['pattern'], response.text)
                        proxies = [f"{ip}:{port}" for ip, port in matches]
                
                else:
                    # 其他源使用正则表达式解析
                    matches = re.findall(source['pattern'], response.text)
                    proxies = [f"{ip}:{port}" for ip, port in matches]
                
                # 过滤无效的代理
                valid_proxies = []
                for proxy in proxies:
                    # 检查IP和端口格式
                    if ':' in proxy:
                        ip, port = proxy.split(':', 1)
                        # 验证IP格式
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            # 验证端口格式
                            if port.isdigit() and 1 <= int(port) <= 65535:
                                valid_proxies.append(proxy)
                
                logger.info(f"从 {source['name']} 获取到 {len(valid_proxies)} 个有效代理")
                if len(valid_proxies) == 0:
                    self.site_fail_count[source['name']] = self.site_fail_count.get(source['name'], 0) + 1
                    if self.site_fail_count[source['name']] >= self.FAIL_THRESHOLD:
                        self.site_blacklist.add(source['name'])
                        self.save_blacklist()
                        logger.warning(f"{source['name']} 采集失败次数过多，已加入黑名单")
                else:
                    self.site_fail_count[source['name']] = 0
                return valid_proxies
            else:
                logger.warning(f"从 {source['name']} 获取代理失败，状态码: {response.status_code}")
                self.site_fail_count[source['name']] = self.site_fail_count.get(source['name'], 0) + 1
                if self.site_fail_count[source['name']] >= self.FAIL_THRESHOLD:
                    self.site_blacklist.add(source['name'])
                    self.save_blacklist()
                    logger.warning(f"{source['name']} 采集失败次数过多，已加入黑名单")
                return []
                
        except Exception as e:
            logger.error(f"从 {source['name']} 获取代理时出错: {e}")
            self.site_fail_count[source['name']] = self.site_fail_count.get(source['name'], 0) + 1
            if self.site_fail_count[source['name']] >= self.FAIL_THRESHOLD:
                self.site_blacklist.add(source['name'])
                self.save_blacklist()
                logger.warning(f"{source['name']} 采集失败次数过多，已加入黑名单")
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
                    # 统计代理池成功率
                    if proxies is not None and len(proxies) > 0:
                        tested = 0
                        success = 0
                        for proxy in proxies:
                            result = self.test_proxy(proxy)
                            tested += 1
                            if result:
                                success += 1
                        if tested > 0 and (1 - success / tested) >= self.POOL_FAIL_RATE:
                            self.site_blacklist.add(source['name'])
                            self.save_blacklist()
                            logger.warning(f"{source['name']} 代理池99%失败，已禁用")
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

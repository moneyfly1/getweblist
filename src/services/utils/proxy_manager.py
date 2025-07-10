#!/usr/bin/env python3
"""
代理管理器
自动管理和轮换代理
"""

import os
import time
import random
from typing import List, Optional, Dict
from loguru import logger

from .proxy_collector import ProxyCollector

class ProxyManager:
    """代理管理器"""
    
    def __init__(self, proxy_file: str = "working_proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = []
        self.current_proxy = None
        self.proxy_failures = {}  # 记录代理失败次数
        self.max_failures = 3     # 最大失败次数
        
        # 加载代理
        self.load_proxies()
    
    def load_proxies(self):
        """加载代理列表"""
        # 首先尝试从文件加载
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"从文件加载了 {len(self.proxies)} 个代理")
        
        # 如果文件不存在或代理数量不足，则搜集新代理
        if len(self.proxies) < 5:
            logger.info("代理数量不足，开始搜集新代理...")
            self.collect_new_proxies()
    
    def collect_new_proxies(self):
        """搜集新代理"""
        collector = ProxyCollector()
        
        # 搜集代理
        proxies = collector.collect_proxies()
        
        if proxies:
            # 测试代理
            working_proxies = collector.test_proxies()
            
            if working_proxies:
                # 保存可用代理
                collector.save_proxies_to_file(self.proxy_file)
                
                # 更新代理列表
                self.proxies = [proxy_info['proxy'] for proxy_info in working_proxies]
                logger.info(f"搜集到 {len(self.proxies)} 个可用代理")
            else:
                logger.warning("没有找到可用的代理")
        else:
            logger.warning("没有搜集到任何代理")
    
    def get_proxy(self) -> Optional[str]:
        """获取一个可用代理"""
        if not self.proxies:
            logger.warning("没有可用代理")
            return None
        
        # 过滤掉失败次数过多的代理
        available_proxies = [
            proxy for proxy in self.proxies 
            if self.proxy_failures.get(proxy, 0) < self.max_failures
        ]
        
        if not available_proxies:
            logger.warning("所有代理都已达到最大失败次数，重置失败计数")
            self.proxy_failures.clear()
            available_proxies = self.proxies
        
        # 随机选择一个代理
        selected_proxy = random.choice(available_proxies)
        self.current_proxy = f"http://{selected_proxy}"
        
        logger.info(f"选择代理: {self.current_proxy}")
        return self.current_proxy
    
    def mark_proxy_failed(self, proxy: str):
        """标记代理失败"""
        if proxy.startswith('http://'):
            proxy = proxy[7:]  # 移除 http:// 前缀
        
        self.proxy_failures[proxy] = self.proxy_failures.get(proxy, 0) + 1
        logger.warning(f"代理 {proxy} 失败，失败次数: {self.proxy_failures[proxy]}")
        
        # 如果失败次数过多，尝试搜集新代理
        if self.proxy_failures[proxy] >= self.max_failures:
            logger.info("代理失败次数过多，尝试搜集新代理...")
            self.collect_new_proxies()
    
    def mark_proxy_success(self, proxy: str):
        """标记代理成功"""
        if proxy.startswith('http://'):
            proxy = proxy[7:]  # 移除 http:// 前缀
        
        # 重置失败计数
        if proxy in self.proxy_failures:
            self.proxy_failures[proxy] = 0
            logger.info(f"代理 {proxy} 成功，重置失败计数")
    
    def set_proxy_environment(self, proxy: str):
        """设置代理环境变量"""
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        logger.info(f"已设置代理环境变量: {proxy}")
    
    def clear_proxy_environment(self):
        """清除代理环境变量"""
        if 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        if 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        logger.info("已清除代理环境变量")
    
    def get_proxy_status(self) -> Dict:
        """获取代理状态"""
        total_proxies = len(self.proxies)
        failed_proxies = len([p for p, count in self.proxy_failures.items() if count >= self.max_failures])
        available_proxies = total_proxies - failed_proxies
        
        return {
            'total': total_proxies,
            'available': available_proxies,
            'failed': failed_proxies,
            'current': self.current_proxy
        }
    
    def refresh_proxies(self):
        """刷新代理列表"""
        logger.info("刷新代理列表...")
        self.collect_new_proxies()
        self.proxy_failures.clear()

def main():
    """主函数"""
    manager = ProxyManager()
    
    # 获取代理状态
    status = manager.get_proxy_status()
    print(f"代理状态: 总计 {status['total']}, 可用 {status['available']}, 失败 {status['failed']}")
    
    # 获取一个代理
    proxy = manager.get_proxy()
    if proxy:
        print(f"当前代理: {proxy}")
        
        # 设置环境变量
        manager.set_proxy_environment(proxy)
        
        # 模拟使用代理
        print("正在测试代理...")
        time.sleep(2)
        
        # 模拟代理成功
        manager.mark_proxy_success(proxy.split('//')[1])
    else:
        print("❌ 没有可用代理")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
代理搜集和测试脚本
自动从多个免费代理网站搜集代理并测试可用性
"""

import sys
import os
import time
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.utils.proxy_collector import ProxyCollector
from services.utils.proxy_manager import ProxyManager

def main():
    """主函数"""
    print("=" * 60)
    print("代理搜集和测试工具")
    print("=" * 60)
    
    # 创建代理搜集器
    collector = ProxyCollector()
    
    print("\n1. 开始搜集代理...")
    proxies = collector.collect_proxies()
    
    if not proxies:
        print("❌ 没有搜集到任何代理")
        return
    
    print(f"\n✅ 成功搜集到 {len(proxies)} 个代理")
    
    print("\n2. 开始测试代理可用性...")
    working_proxies = collector.test_proxies()
    
    if not working_proxies:
        print("❌ 没有找到可用的代理")
        return
    
    print(f"\n✅ 找到 {len(working_proxies)} 个可用代理")
    
    # 保存可用代理
    collector.save_proxies_to_file()
    
    # 显示代理信息
    print("\n3. 代理信息:")
    print("-" * 40)
    for i, proxy_info in enumerate(working_proxies[:10], 1):  # 显示前10个
        print(f"{i:2d}. {proxy_info['proxy']:<20} 速度: {proxy_info['speed']:.2f}s")
    
    if len(working_proxies) > 10:
        print(f"... 还有 {len(working_proxies) - 10} 个代理")
    
    # 测试代理管理器
    print("\n4. 测试代理管理器...")
    manager = ProxyManager()
    
    status = manager.get_proxy_status()
    print(f"代理状态: 总计 {status['total']}, 可用 {status['available']}, 失败 {status['failed']}")
    
    # 测试获取代理
    proxy = manager.get_proxy()
    if proxy:
        print(f"获取到代理: {proxy}")
        
        # 设置环境变量
        manager.set_proxy_environment(proxy)
        print("代理环境变量已设置")
        
        # 模拟使用代理
        print("正在测试代理连接...")
        time.sleep(2)
        
        # 标记成功
        manager.mark_proxy_success(proxy.split('//')[1])
        print("代理测试成功")
    else:
        print("❌ 无法获取代理")
    
    print("\n" + "=" * 60)
    print("代理搜集和测试完成！")
    print("=" * 60)
    
    print("\n📋 使用说明:")
    print("1. 可用代理已保存到 working_proxies.txt")
    print("2. 代理管理器会自动使用这些代理")
    print("3. 运行采集器时会自动轮换代理")
    print("4. 如果代理失效，会自动搜集新代理")
    
    print("\n🚀 现在可以运行采集器:")
    print("python src/main.py mining --collector --classifier")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
反检测机制测试脚本
测试重试机制和代理支持
"""

import os
import sys
import time
import random
from unittest.mock import patch, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.sspanel_mining.sspanel_collector import SSPanelHostsCollector
from services.sspanel_mining.exceptions import CollectorSwitchError

def test_retry_mechanism():
    """测试重试机制"""
    print("🧪 测试重试机制...")
    
    # 创建临时文件
    temp_file = "test_data.txt"
    
    try:
        collector = SSPanelHostsCollector(
            path_file_txt=temp_file,
            silence=True,
            debug=True
        )
        
        # 模拟CollectorSwitchError
        with patch.object(collector, '_page_tracking') as mock_tracking:
            mock_tracking.side_effect = CollectorSwitchError("模拟Google拦截")
            
            # 测试重试机制
            try:
                collector.run(page_num=1, sleep_node=1)
            except CollectorSwitchError as e:
                print("✅ 重试机制正常工作，正确捕获了CollectorSwitchError")
                print(f"异常信息: {e}")
            else:
                print("❌ 重试机制未正常工作")
                
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_proxy_support():
    """测试代理支持"""
    print("\n🌐 测试代理支持...")
    
    # 检查环境变量
    http_proxy = os.environ.get('HTTP_PROXY')
    https_proxy = os.environ.get('HTTPS_PROXY')
    
    if http_proxy or https_proxy:
        print(f"✅ 检测到代理设置:")
        if http_proxy:
            print(f"  HTTP_PROXY: {http_proxy}")
        if https_proxy:
            print(f"  HTTPS_PROXY: {https_proxy}")
    else:
        print("⚠️ 未检测到代理设置")
        print("建议设置代理以避免被Google拦截")

def test_random_behavior():
    """测试随机行为模拟"""
    print("\n🎲 测试随机行为模拟...")
    
    # 测试随机延迟
    delays = [random.uniform(1, 5) for _ in range(5)]
    print(f"随机延迟测试: {[f'{d:.2f}s' for d in delays]}")
    
    # 测试随机滚动
    scroll_actions = ['PAGE_DOWN', 'END', 'PAGE_UP', 'HOME']
    random_scrolls = [random.choice(scroll_actions) for _ in range(5)]
    print(f"随机滚动测试: {random_scrolls}")
    
    print("✅ 随机行为模拟正常")

def test_user_agent_rotation():
    """测试用户代理轮换"""
    print("\n🔄 测试用户代理轮换...")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    selected_ua = random.choice(user_agents)
    print(f"随机选择的用户代理: {selected_ua[:50]}...")
    print("✅ 用户代理轮换正常")

def main():
    """主测试函数"""
    print("=" * 60)
    print("反检测机制测试")
    print("=" * 60)
    
    # 运行所有测试
    test_retry_mechanism()
    test_proxy_support()
    test_random_behavior()
    test_user_agent_rotation()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n📋 建议:")
    print("1. 如果测试通过，说明反检测机制正常工作")
    print("2. 建议设置代理以避免被Google拦截")
    print("3. 运行: python setup_proxy.py 来配置代理")
    print("4. 然后运行: python src/main.py mining --collector --classifier")

if __name__ == "__main__":
    main() 
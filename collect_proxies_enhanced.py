#!/usr/bin/env python3
"""
增强版代理搜集脚本
专门测试新的代理源网站
"""

import sys
import os
import time
import json
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.utils.proxy_collector import ProxyCollector
from services.utils.proxy_manager import ProxyManager

def test_specific_sources():
    """测试特定的代理源"""
    collector = ProxyCollector()
    
    # 测试新的代理源
    new_sources = [
        '66ip', '89ip', 'Goubanjia', 'PubProxy', 
        'Proxy11', 'ProxyListDownload', 'ProxyListDownloadHTTP', 'ProxyListDownloadSOCKS',
        # 新增的高质量代理源
        'SPYS', 'HidemyName', 'FreeProxyCZ', 'SocksProxy', 'Hidester', 
        'Premproxy', 'ProxyScrape', 'OpenProxy', 'ProxyDB',
        'ProxyScrapeAPI', 'ProxyScrapeHTTPS', 'ProxyScrapeSOCKS5'
    ]
    
    print("=" * 60)
    print("测试新的代理源")
    print("=" * 60)
    
    for source_name in new_sources:
        print(f"\n🔍 测试代理源: {source_name}")
        
        # 找到对应的源配置
        source_config = None
        for source in collector.proxy_sources:
            if source['name'] == source_name:
                source_config = source
                break
        
        if source_config:
            try:
                proxies = collector.fetch_proxies_from_source(source_config)
                if proxies:
                    print(f"✅ {source_name}: 获取到 {len(proxies)} 个代理")
                    print(f"   前5个代理: {proxies[:5]}")
                else:
                    print(f"❌ {source_name}: 没有获取到代理")
            except Exception as e:
                print(f"❌ {source_name}: 获取失败 - {e}")
        else:
            print(f"❌ {source_name}: 未找到配置")

def test_all_sources():
    """测试所有代理源"""
    collector = ProxyCollector()
    
    print("\n" + "=" * 60)
    print("测试所有代理源")
    print("=" * 60)
    
    all_proxies = []
    
    for source in collector.proxy_sources:
        print(f"\n🔍 测试: {source['name']}")
        try:
            proxies = collector.fetch_proxies_from_source(source)
            if proxies:
                print(f"✅ 获取到 {len(proxies)} 个代理")
                all_proxies.extend(proxies)
            else:
                print(f"❌ 没有获取到代理")
        except Exception as e:
            print(f"❌ 获取失败: {e}")
    
    # 去重
    unique_proxies = list(set(all_proxies))
    print(f"\n📊 总计获取到 {len(unique_proxies)} 个唯一代理")
    
    return unique_proxies

def test_proxies_quality(proxies):
    """测试代理质量"""
    if not proxies:
        print("❌ 没有代理可测试")
        return []
    
    print(f"\n🧪 测试 {len(proxies)} 个代理的质量...")
    
    # 只测试前50个代理以节省时间
    test_proxies = proxies[:50]
    working_proxies = []
    
    for i, proxy in enumerate(test_proxies, 1):
        print(f"测试 {i}/{len(test_proxies)}: {proxy}")
        
        try:
            result = collector.test_proxy(proxy)
            if result:
                working_proxies.append(result)
                print(f"✅ {proxy} 可用 (速度: {result['speed']:.2f}s)")
            else:
                print(f"❌ {proxy} 不可用")
        except Exception as e:
            print(f"❌ {proxy} 测试失败: {e}")
        
        # 添加延迟避免过于频繁的请求
        time.sleep(0.5)
    
    return working_proxies

def save_proxy_report(proxies, working_proxies):
    """保存代理报告"""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_proxies': len(proxies),
        'working_proxies': len(working_proxies),
        'success_rate': f"{(len(working_proxies) / len(proxies) * 100):.2f}%" if proxies else "0%",
        'working_proxies_list': working_proxies
    }
    
    # 保存到JSON文件
    with open('proxy_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 保存可用代理到文本文件
    with open('working_proxies.txt', 'w', encoding='utf-8') as f:
        for proxy_info in working_proxies:
            f.write(f"{proxy_info['proxy']}\n")
    
    print(f"\n📄 报告已保存:")
    print(f"   - proxy_report.json: 详细报告")
    print(f"   - working_proxies.txt: 可用代理列表")

def main():
    """主函数"""
    print("=" * 60)
    print("增强版代理搜集工具")
    print("=" * 60)
    
    # 测试特定源
    test_specific_sources()
    
    # 测试所有源
    all_proxies = test_all_sources()
    
    if all_proxies:
        # 测试代理质量
        working_proxies = test_proxies_quality(all_proxies)
        
        # 保存报告
        save_proxy_report(all_proxies, working_proxies)
        
        # 显示结果
        print(f"\n🎉 搜集完成!")
        print(f"📊 统计信息:")
        print(f"   - 总代理数: {len(all_proxies)}")
        print(f"   - 可用代理数: {len(working_proxies)}")
        if all_proxies:
            success_rate = len(working_proxies) / len(all_proxies) * 100
            print(f"   - 成功率: {success_rate:.2f}%")
        
        if working_proxies:
            print(f"\n🏆 最佳代理 (按速度排序):")
            sorted_proxies = sorted(working_proxies, key=lambda x: x['speed'])
            for i, proxy_info in enumerate(sorted_proxies[:10], 1):
                print(f"   {i}. {proxy_info['proxy']} (速度: {proxy_info['speed']:.2f}s)")
        
        print(f"\n🚀 现在可以运行采集器:")
        print(f"python src/main.py mining --collector --classifier")
    else:
        print("❌ 没有获取到任何代理")

if __name__ == "__main__":
    main() 
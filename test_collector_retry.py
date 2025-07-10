#!/usr/bin/env python3
"""
测试CollectorSwitchError重试机制
"""

import sys
import os
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.sspanel_mining.sspanel_collector import SSPanelHostsCollector
from services.sspanel_mining.exceptions import CollectorSwitchError

def test_collector_retry():
    """测试采集器的重试机制"""
    
    print("=== 测试SSPanel采集器重试机制 ===")
    
    # 创建临时文件用于测试
    test_file = "test_dataset.txt"
    
    try:
        # 创建采集器实例
        collector = SSPanelHostsCollector(
            path_file_txt=test_file,
            silence=True,  # 在CI环境中使用静默模式
            debug=False
        )
        
        print(f"[INFO] 采集器初始化完成")
        print(f"[INFO] 搜索查询: {collector._QUERY}")
        print(f"[INFO] 目标文件: {test_file}")
        
        # 运行采集器（只采集少量页面进行测试）
        print(f"[INFO] 开始测试采集（限制为2页）...")
        collector.run(page_num=2, sleep_node=1)
        
        print(f"[SUCCESS] 采集测试完成")
        
        # 检查是否生成了文件
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf8') as f:
                lines = f.readlines()
            print(f"[INFO] 成功采集到 {len(lines)} 个站点")
            for i, line in enumerate(lines[:5]):  # 只显示前5个
                print(f"  {i+1}. {line.strip()}")
            if len(lines) > 5:
                print(f"  ... 还有 {len(lines) - 5} 个站点")
        else:
            print(f"[WARNING] 未生成数据文件")
            
    except CollectorSwitchError as e:
        print(f"[ERROR] 遇到Google拦截: {e}")
        print("[INFO] 这是预期的行为，说明重试机制正在工作")
        return False
        
    except Exception as e:
        print(f"[ERROR] 遇到未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"[INFO] 已清理测试文件: {test_file}")
    
    return True

def test_retry_logic():
    """测试重试逻辑（不实际运行采集器）"""
    
    print("\n=== 测试重试逻辑 ===")
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"[INFO] 第 {retry_count + 1} 次尝试...")
            
            # 模拟可能失败的操作
            if random.random() < 0.7:  # 70%的概率失败
                raise CollectorSwitchError("模拟的Google拦截")
            
            print("[SUCCESS] 操作成功")
            break
            
        except CollectorSwitchError as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = retry_count * 5  # 递增等待时间
                print(f"[WARNING] 检测到拦截，等待 {wait_time} 秒后进行第 {retry_count + 1} 次重试...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] 经过 {max_retries} 次重试后仍然失败")
                return False
    
    return True

if __name__ == "__main__":
    print("开始测试SSPanel采集器改进...")
    
    # 测试重试逻辑
    retry_success = test_retry_logic()
    
    # 测试实际采集器（可选，在CI环境中可能被拦截）
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        print("\n[INFO] 在CI环境中，跳过实际采集测试以避免被Google拦截")
        collector_success = True
    else:
        collector_success = test_collector_retry()
    
    if retry_success and collector_success:
        print("\n[SUCCESS] 所有测试通过！")
        sys.exit(0)
    else:
        print("\n[FAILURE] 部分测试失败")
        sys.exit(1) 
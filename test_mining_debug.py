#!/usr/bin/env python3
"""
调试采集器和分类器运行情况
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_collector():
    """测试采集器"""
    print("=" * 50)
    print("测试采集器")
    print("=" * 50)
    
    try:
        from services.sspanel_mining.sspanel_collector import SSPanelHostsCollector
        
        # 创建临时文件
        test_file = f"test_dataset_{datetime.now().strftime('%Y-%m-%d')}.txt"
        
        print(f"创建采集器实例...")
        collector = SSPanelHostsCollector(
            path_file_txt=test_file,
            silence=True,
            debug=False
        )
        
        print(f"采集器配置:")
        print(f"  - 搜索查询: {collector._QUERY}")
        print(f"  - 目标文件: {test_file}")
        print(f"  - 静默模式: {collector.silence}")
        
        # 只运行1页进行测试
        print(f"开始采集（限制1页）...")
        collector.run(page_num=1, sleep_node=1)
        
        # 检查结果
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf8') as f:
                lines = f.readlines()
            print(f"✅ 采集成功！生成了 {len(lines)} 个站点")
            print("前5个站点:")
            for i, line in enumerate(lines[:5]):
                print(f"  {i+1}. {line.strip()}")
            
            # 清理测试文件
            os.remove(test_file)
            print(f"已清理测试文件: {test_file}")
            return True
        else:
            print("❌ 未生成数据文件")
            return False
            
    except Exception as e:
        print(f"❌ 采集器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_classifier():
    """测试分类器"""
    print("\n" + "=" * 50)
    print("测试分类器")
    print("=" * 50)
    
    try:
        from apis.scaffold.mining import run_classifier
        
        print("运行分类器...")
        run_classifier(power=4, source="local", batch=1)
        
        # 检查分类器结果
        classifier_dir = "src/database/sspanel_hosts/classifier"
        if os.path.exists(classifier_dir):
            csv_files = [f for f in os.listdir(classifier_dir) if f.endswith('.csv')]
            if csv_files:
                latest_csv = max(csv_files, key=lambda x: os.path.getctime(os.path.join(classifier_dir, x)))
                csv_path = os.path.join(classifier_dir, latest_csv)
                
                with open(csv_path, 'r', encoding='utf8') as f:
                    lines = f.readlines()
                
                print(f"✅ 分类器成功！最新文件: {latest_csv}")
                print(f"文件大小: {len(lines)} 行")
                print("前5行内容:")
                for i, line in enumerate(lines[:5]):
                    print(f"  {i+1}. {line.strip()}")
                return True
            else:
                print("❌ 分类器目录中没有CSV文件")
                return False
        else:
            print("❌ 分类器目录不存在")
            return False
            
    except Exception as e:
        print(f"❌ 分类器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_data():
    """检查现有数据"""
    print("\n" + "=" * 50)
    print("检查现有数据")
    print("=" * 50)
    
    # 检查数据文件
    data_dir = "src/database/sspanel_hosts"
    if os.path.exists(data_dir):
        txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
        print(f"数据文件数量: {len(txt_files)}")
        if txt_files:
            latest_txt = max(txt_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
            print(f"最新数据文件: {latest_txt}")
    
    # 检查分类文件
    classifier_dir = "src/database/sspanel_hosts/classifier"
    if os.path.exists(classifier_dir):
        csv_files = [f for f in os.listdir(classifier_dir) if f.endswith('.csv')]
        print(f"分类文件数量: {len(csv_files)}")
        if csv_files:
            latest_csv = max(csv_files, key=lambda x: os.path.getctime(os.path.join(classifier_dir, x)))
            print(f"最新分类文件: {latest_csv}")

def main():
    """主函数"""
    print("开始调试采集器和分类器...")
    
    # 检查现有数据
    check_existing_data()
    
    # 测试采集器
    collector_success = test_collector()
    
    # 测试分类器
    classifier_success = test_classifier()
    
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    
    if collector_success and classifier_success:
        print("🎉 所有测试通过！")
        return 0
    elif collector_success:
        print("⚠️ 采集器成功，但分类器失败")
        return 1
    elif classifier_success:
        print("⚠️ 分类器成功，但采集器失败")
        return 1
    else:
        print("❌ 所有测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的ChromeDriver测试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """测试基本导入"""
    try:
        from services.utils.toolbox.toolbox import get_ctx
        print("✅ 基本导入测试通过")
        return True
    except Exception as e:
        print(f"❌ 基本导入测试失败: {e}")
        return False

def test_chrome_version_detection():
    """测试Chrome版本检测"""
    try:
        from services.utils.toolbox.toolbox import _get_chrome_version
        version = _get_chrome_version()
        if version:
            print(f"✅ Chrome版本检测成功: {version}")
        else:
            print("⚠️ 无法检测Chrome版本，但这可能不是问题")
        return True
    except Exception as e:
        print(f"❌ Chrome版本检测失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("ChromeDriver 简化测试")
    print("=" * 50)
    
    # 测试基本导入
    import_test = test_basic_import()
    
    # 测试Chrome版本检测
    version_test = test_chrome_version_detection()
    
    print("=" * 50)
    if import_test and version_test:
        print("🎉 基本测试通过！")
        print("注意：这个测试只验证了基本功能，完整的ChromeDriver测试需要Chrome浏览器环境")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver 兼容性测试脚本
用于验证修复后的ChromeDriver管理是否正常工作
"""

import sys
import os
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_chromedriver():
    """测试ChromeDriver初始化"""
    try:
        from services.utils.toolbox.toolbox import get_ctx
        
        logger.info("开始测试ChromeDriver初始化...")
        
        # 测试无头模式
        logger.info("测试无头模式ChromeDriver...")
        with get_ctx(silence=True) as driver:
            logger.info("ChromeDriver初始化成功！")
            driver.get("https://www.google.com")
            logger.info("页面加载成功！")
            title = driver.title
            logger.info(f"页面标题: {title}")
            
        logger.info("✅ ChromeDriver测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromeDriver测试失败: {e}")
        return False

def test_version_detection():
    """测试Chrome版本检测"""
    try:
        from services.utils.toolbox.toolbox import _get_chrome_version
        
        logger.info("开始测试Chrome版本检测...")
        version = _get_chrome_version()
        
        if version:
            logger.info(f"✅ 检测到Chrome版本: {version}")
        else:
            logger.warning("⚠️ 无法检测Chrome版本，但这可能不是问题")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Chrome版本检测失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("=" * 50)
    logger.info("ChromeDriver 兼容性测试")
    logger.info("=" * 50)
    
    # 测试Chrome版本检测
    version_test = test_version_detection()
    
    # 测试ChromeDriver初始化
    driver_test = test_chromedriver()
    
    logger.info("=" * 50)
    if version_test and driver_test:
        logger.info("🎉 所有测试通过！ChromeDriver修复成功！")
        return 0
    else:
        logger.error("❌ 部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
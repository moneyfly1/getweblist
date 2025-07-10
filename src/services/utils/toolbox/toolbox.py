# -*- coding: utf-8 -*-
# Time       : 2022/1/16 0:27
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import sys
import os
import subprocess
import time
from typing import Optional

from loguru import logger
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager


class InitLog:

    @staticmethod
    def init_log(**sink_path):
        event_logger_format = (
            "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | "
            "<lvl>{level}</lvl> - "
            # "<c><u>{name}</u></c> | "
            "{message}"
        )
        logger.remove()
        logger.add(
            sink=sys.stdout,
            colorize=True,
            level="DEBUG",
            format=event_logger_format,
            diagnose=False
        )
        if sink_path.get("error"):
            logger.add(
                sink=sink_path.get("error"),
                level="ERROR",
                rotation="1 week",
                encoding="utf8",
                diagnose=False
            )
        if sink_path.get("runtime"):
            logger.add(
                sink=sink_path.get("runtime"),
                level="DEBUG",
                rotation="20 MB",
                retention="20 days",
                encoding="utf8",
                diagnose=False
            )
        return logger


def _set_ctx() -> ChromeOptions:
    options = ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--lang=zh-CN")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--incognito")
    options.add_argument("--disk-cache")
    return options


def _get_chrome_version():
    """获取Chrome版本号"""
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[-1]
                return version.split('.')[0]  # 返回主版本号
        elif sys.platform.startswith('linux'):
            # Linux
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[-1]
                return version.split('.')[0]  # 返回主版本号
        elif sys.platform.startswith('darwin'):
            # macOS
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[-1]
                return version.split('.')[0]  # 返回主版本号
    except Exception as e:
        logger.warning(f"无法获取Chrome版本: {e}")
    return None


def _create_chromedriver_service_with_retry(max_retries=3):
    """创建ChromeDriver服务，带重试机制"""
    for attempt in range(max_retries):
        try:
            # 获取Chrome版本并尝试匹配
            chrome_version = _get_chrome_version()
            if chrome_version:
                # 使用已知稳定的版本映射
                stable_versions = {
                    "138": "120.0.6099.109",  # Chrome 138+ 使用最新的稳定版本
                    "137": "120.0.6099.109",
                    "136": "120.0.6099.109",
                    "135": "120.0.6099.109",
                    "134": "120.0.6099.109",
                    "133": "120.0.6099.109",
                    "132": "120.0.6099.109",
                    "131": "120.0.6099.109",
                    "130": "120.0.6099.109",
                    "129": "120.0.6099.109",
                    "128": "120.0.6099.109",
                    "127": "120.0.6099.109",
                    "126": "120.0.6099.109",
                    "125": "120.0.6099.109",
                    "124": "120.0.6099.109",
                    "123": "120.0.6099.109",
                    "122": "120.0.6099.109",
                    "121": "120.0.6099.109",
                    "120": "120.0.6099.109",
                    "119": "119.0.6045.105", 
                    "118": "118.0.5993.70",
                    "117": "117.0.5938.149",
                    "116": "116.0.5845.96",
                    "115": "115.0.5790.170",
                    "114": "114.0.5735.90",
                    "113": "113.0.5672.63",
                    "112": "112.0.5615.49",
                    "111": "111.0.5563.64",
                    "110": "110.0.5481.77",
                    "109": "109.0.5414.119",
                    "108": "108.0.5359.71",
                    "107": "107.0.5304.18",
                    "106": "106.0.5249.61",
                    "105": "105.0.5195.52",
                    "104": "104.0.5112.79",
                    "103": "103.0.5060.134",
                    "102": "102.0.5005.61",
                    "101": "101.0.4951.41",
                    "100": "100.0.4896.75",
                    "99": "99.0.4844.51",
                    "98": "98.0.4758.102",
                    "97": "97.0.4692.71",
                    "96": "96.0.4664.110",
                    "95": "95.0.4638.69",
                    "94": "94.0.4606.81",
                    "93": "93.0.4577.63",
                    "92": "92.0.4515.159",
                    "91": "91.0.4472.124",
                    "90": "90.0.4430.212",
                    "89": "89.0.4389.23",
                    "88": "88.0.4324.96",
                    "87": "87.0.4280.88",
                    "86": "86.0.4240.22",
                    "85": "85.0.4183.87",
                    "84": "84.0.4147.30",
                    "83": "83.0.4103.39",
                    "82": "82.0.4058.20",
                    "81": "81.0.4044.138",
                    "80": "80.0.3987.106",
                    "79": "79.0.3945.36",
                    "78": "78.0.3904.105",
                    "77": "77.0.3865.40",
                    "76": "76.0.3809.126",
                    "75": "75.0.3770.140",
                    "74": "74.0.3729.6",
                    "73": "73.0.3683.68",
                    "72": "72.0.3626.69",
                    "71": "71.0.3578.137",
                    "70": "70.0.3538.97",
                    "69": "69.0.3497.128",
                    "68": "68.0.3440.75",
                    "67": "67.0.3396.99",
                    "66": "66.0.3359.181",
                    "65": "65.0.3325.146",
                    "64": "64.0.3282.140",
                    "63": "63.0.3239.132",
                    "62": "62.0.3202.94",
                    "61": "61.0.3163.100",
                    "60": "60.0.3112.113",
                    "59": "59.0.3071.115",
                    "58": "58.0.3029.110",
                    "57": "57.0.2987.133",
                    "56": "56.0.2924.87",
                    "55": "55.0.2883.87",
                    "54": "54.0.2840.87",
                    "53": "53.0.2785.143",
                    "52": "52.0.2743.116",
                    "51": "51.0.2704.103",
                    "50": "50.0.2661.102",
                    "49": "49.0.2623.112",
                    "48": "48.0.2544.116",
                    "47": "47.0.2516.88",
                    "46": "46.0.2494.80",
                    "45": "45.0.2454.101",
                    "44": "44.0.2403.157",
                    "43": "43.0.2357.132",
                    "42": "42.0.2311.135",
                    "41": "41.0.2272.96",
                    "40": "40.0.2234.2",
                    "39": "39.0.2171.99",
                    "38": "38.0.2125.111",
                    "37": "37.0.2062.124",
                    "36": "36.0.1985.125",
                    "35": "35.0.1916.153",
                    "34": "34.0.1847.137",
                    "33": "33.0.1750.154",
                    "32": "32.0.1700.102",
                    "31": "31.0.1650.63",
                    "30": "30.0.1599.101",
                    "29": "29.0.1547.76",
                    "28": "28.0.1500.95",
                    "27": "27.0.1453.110",
                    "26": "26.0.1410.64",
                    "25": "25.0.1364.172",
                    "24": "24.0.1312.56",
                    "23": "23.0.1270.14",
                    "22": "22.0.1229.94",
                    "21": "21.0.1180.89",
                    "20": "20.0.1133.57",
                    "19": "19.0.1084.56",
                    "18": "18.0.1025.168",
                    "17": "17.0.963.79",
                    "16": "16.0.902.73",
                    "15": "15.0.874.121",
                    "14": "14.0.835.202",
                    "13": "13.0.782.112",
                    "12": "12.0.706.0",
                    "11": "11.0.696.70",
                    "10": "10.0.648.204",
                    "9": "9.0.597.84",
                    "8": "8.0.552.215",
                    "7": "7.0.517.44",
                    "6": "6.0.472.62",
                    "5": "5.0.307.9",
                    "4": "4.0.211.0",
                    "3": "3.0.195.0",
                    "2": "2.0.226.0",
                    "1": "1.0.154.0"
                }
                
                if chrome_version in stable_versions:
                    driver_version = stable_versions[chrome_version]
                    logger.info(f"Chrome版本 {chrome_version}，使用ChromeDriver版本 {driver_version}")
                    from selenium.webdriver.chrome.service import Service
                    return Service(ChromeDriverManager(version=driver_version, log_level=0).install())
                else:
                    logger.warning(f"Chrome版本 {chrome_version} 不在稳定版本映射中，尝试使用默认版本")
                    from selenium.webdriver.chrome.service import Service
                    return Service(ChromeDriverManager(log_level=0).install())
            else:
                # 如果无法获取Chrome版本，使用已知稳定的版本
                logger.info("无法获取Chrome版本，使用稳定版本120.0.6099.109")
                from selenium.webdriver.chrome.service import Service
                return Service(ChromeDriverManager(version="120.0.6099.109", log_level=0).install())
        except Exception as e:
            logger.warning(f"ChromeDriverManager安装失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 等待2秒后重试
            else:
                raise
    
    # 如果所有重试都失败，抛出异常
    raise RuntimeError("ChromeDriverManager安装失败，已尝试所有重试")


def get_ctx(silence: Optional[bool] = None):
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver import Chrome

    silence = True if silence is None or "linux" in sys.platform else silence

    options = _set_ctx()
    if silence is True:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
    options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"')
    
    # 改进的ChromeDriver管理，解决GitHub Actions兼容性问题
    service = None
    
    # 方案1: 使用环境变量指定的ChromeDriver
    chrome_driver_path = os.environ.get('CHROME_DRIVER_PATH')
    if chrome_driver_path and os.path.exists(chrome_driver_path):
        logger.info(f"使用环境变量指定的ChromeDriver: {chrome_driver_path}")
        service = Service(chrome_driver_path)
    
    # 方案2: 尝试使用系统ChromeDriver
    if service is None:
        try:
            # 检查系统是否有chromedriver
            result = subprocess.run(['which', 'chromedriver'], capture_output=True)
            if result.returncode == 0:
                logger.info("使用系统ChromeDriver")
                service = Service("chromedriver")
        except Exception as e:
            logger.warning(f"系统ChromeDriver检查失败: {e}")
    
    # 方案3: 使用webdriver_manager，但指定稳定版本
    if service is None:
        try:
            service = _create_chromedriver_service_with_retry()
        except Exception as e:
            logger.error(f"ChromeDriver安装完全失败: {e}")
            raise RuntimeError("无法初始化ChromeDriver，请检查Chrome浏览器安装和网络连接")
    
    if service is None:
        raise RuntimeError("无法创建ChromeDriver服务")
    
    return Chrome(options=options, service=service)  # noqa

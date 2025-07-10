# -*- coding: utf-8 -*-
# Time       : 2022/2/4 12:08
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
from os.path import dirname, join, exists, abspath

import pytz

# ---------------------------------------------------
# TODO [√] 项目索引路径定位
# ---------------------------------------------------
# 获取项目根目录（适用于本地和云端）
def get_project_root():
    return abspath(os.path.join(os.path.dirname(__file__), '../../..'))

PROJECT_ROOT = get_project_root()

# 系统数据库
PROJECT_DATABASE = join(PROJECT_ROOT, "src", "database")

# 运行缓存:采集器输出目录
DIR_OUTPUT_STORE_COLLECTOR = join(PROJECT_DATABASE, "sspanel_hosts")

# 运行缓存:分类器输出目录
DIR_OUTPUT_STORE_CLASSIFIER = join(DIR_OUTPUT_STORE_COLLECTOR, "classifier")
# ---------------------------------------------------
# TODO [√] 运行日志设置
# ---------------------------------------------------
DIR_LOG = join(PROJECT_DATABASE, "logs")
from services.utils import InitLog

logger = InitLog.init_log(
    error=join(DIR_LOG, "error.log"),
    runtime=join(DIR_LOG, "runtime.log")
)
# ---------------------------------------------------
# TODO [*] 自动调整
# ---------------------------------------------------
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")

# 目录补全
for _pending in [
    PROJECT_DATABASE,
    DIR_OUTPUT_STORE_COLLECTOR,
    DIR_OUTPUT_STORE_CLASSIFIER,
    DIR_LOG
]:
    if not exists(_pending):
        os.mkdir(_pending)

# -*- coding: utf-8 -*-
"""i志愿 考勤比对工具 - 全局配置"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://www.gdzyz.cn"
ADMIN_URL = BASE_URL + "/admin/#/dashboard"

TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# 请求超时（秒）
TIMEOUT = 30
# 登录等待超时（秒）：等待用户手动完成登录
LOGIN_WAIT_TIMEOUT = 300
# 活动查询默认数量
DEFAULT_ACTIVITY_LIMIT = 10
# 名单/考勤分页大小
PAGE_SIZE = 50

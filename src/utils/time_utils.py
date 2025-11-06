# -*- coding: utf-8 -*-
"""时间工具函数
提供与时间相关的工具函数
"""

import datetime


def get_current_time_str():
    """获取当前时间的格式化字符串，用于Allure报告
    
    Returns:
        str: 格式化的当前时间字符串
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


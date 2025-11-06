# -*- coding: utf-8 -*-
"""多乐五子棋应用启动测试脚本
此脚本用于自动连接设备、启动多乐五子棋应用、等待特定界面出现并执行点击操作。
"""

import uiautomator2 as u2
import time
import pytest
import allure
# 导入工具函数
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str
# 导入参数
from src.config.coordinates import SDKPrivacyConfig

class TestDuoleWuZiQiApp:
    """多乐五子棋应用测试类"""

    @pytest.fixture(scope="class")
    def driver(self):
        """连接到Android设备并返回驱动实例的fixture"""
        driver = u2.connect()  # 连接手机，若电脑只连接了一部手机，则不需要设备信息
        print("设备连接成功!")
        print("设备信息:")
        print(driver.info)  # 打印设备信息
        yield driver

        # 测试结束后清理资源——暂时先不关闭
        # driver.app_stop("com.duole.wuziqihd")
        # print("测试结束，已关闭应用")

    @allure.feature("应用启动")
    @allure.story("启动多乐五子棋应用")
    def test_launch_app(self, driver):
        """测试启动多乐五子棋应用"""
        with allure.step(f"[{get_current_time_str()}] 清理后台应用并启动指定包名的应用"):
            try:
                # 启动应用前先清理后台，确保应用是最新状态
                driver.app_stop("com.duole.wuziqihd")
                # 启动指定包名的应用
                driver.app_start("com.duole.wuziqihd")
                allure.attach(f"[{get_current_time_str()}] 已启动应用com.duole.wuziqihd", "操作结果")
            except Exception as e:
                print(f"启动应用时发生错误: {e}")
                allure.attach(f"[{get_current_time_str()}] {str(e)}", "错误信息", allure.attachment_type.TEXT)
                # 截图保存错误状态
                attach_screenshot_to_allure(driver, "app_launch_error", f"[{get_current_time_str()}] 启动应用错误时的界面")
                raise

        with allure.step("验证应用启动成功"):
            # 等待应用启动并获取当前包名
            time.sleep(3)  # 给应用启动时间
            current_package = driver.app_current()['package']
            assert current_package == "com.duole.wuziqihd", f"应用启动失败，当前包名为: {current_package}"
            allure.attach("应用启动成功", "验证结果")


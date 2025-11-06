# -*- coding: utf-8 -*-
"""多乐五子棋应用每日签到测试脚本
此脚本用于测试游戏内的每日签到功能。
"""

from unittest import result
from numpy import rad2deg
import uiautomator2 as u2
import time
import pytest
import allure
# 导入工具函数
from src.utils.screenshot_utils import attach_screenshot_to_allure, attach_screenshot_with_mark_to_allure
from src.utils.time_utils import get_current_time_str
from src.utils.image_utils import create_image_matcher


class TestDailySignIn:
    """多乐五子棋应用每日签到测试类"""

    @pytest.fixture(scope="class")
    def driver(self):
        """连接到Android设备并返回驱动实例的fixture"""
        driver = u2.connect()  # 连接手机，若电脑只连接了一部手机，则不需要设备信息
        print("设备连接成功!")
        print("设备信息:")
        print(driver.info)  # 打印设备信息
        yield driver

    @allure.feature("每日签到")
    @allure.story("每日签到功能点击测试")
    def test_click_signin_button(self, driver):
        """每日签到功能点击测试"""
        
        with allure.step("查找签到弹窗按钮"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_signin_button_common.png'
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_templates_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_button_not_found", "签到按钮未找到")

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"签到按钮位置: ({x}, {y}), 置信度: {confidence:.3f}", "签到按钮查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "signin_button_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试查找签到弹窗失败: {e}",returncode=1)
        
        with allure.step("点击签到弹窗按钮"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_text/signin_dialog_title_text_common.png'
                driver.click(x, y)
                time.sleep(2)
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_templates_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_dialog_title_text_not_found", "签到弹窗标题未找到")

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"签到弹窗标题位置: ({x}, {y}), 置信度: {confidence:.3f}", "签到弹窗标题查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "signin_button_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试点击签到按钮失败: {e}",returncode=1)
# -*- coding: utf-8 -*-
"""多乐五子棋应用每日签到测试脚本
此脚本用于测试游戏内的每日签到功能。
"""
import os
import uiautomator2 as u2
import time
import pytest
import allure
import subprocess
# 导入工具函数
from src.config.coordinates import set_current_app
from src.utils.screenshot_utils import attach_screenshot_to_allure, attach_screenshot_with_mark_to_allure
from src.utils.time_utils import get_current_time_str
from src.utils.image_utils import create_image_matcher

set_current_app("com.duole.wuziqihd")
os.environ["APP_PACKAGE"] = "com.duole.wuziqihd"



class TestDailySignIn:
    """多乐五子棋应用每日签到测试类"""

    @pytest.fixture(scope="class")
    def driver(self):
        """初始化UIAutomator2驱动并启动应用"""
        d = u2.connect()
        
        # 检查 app 是否已运行
        current_app = d.app_current()
        if current_app.get('package') != 'com.duole.chinachess':
            # 只有在 app 未运行时才启动
            try:
                d.app_stop("com.duole.chinachess")
                time.sleep(2)
            except Exception:
                pass
            d.app_start("com.duole.chinachess")
        
        yield d
        # 用例结束后不强制关闭，避免影响后续排查
        # d.app_stop("com.duole.chinachess")


    @allure.feature("游戏大厅")
    @allure.story("验证App启动，进入游戏大厅")
    def test_launch_app_enter_gamehome(self,driver):
        """验证App启动，进入游戏大厅"""
        with allure.step("App启动"):
            driver.app_start(os.environ["APP_PACKAGE"])
            time.sleep(20)
            attach_screenshot_to_allure(driver, "app_launch_success", "App启动成功")
        
        with allure.step("查找多乐币图标验证已经进入到游戏大厅"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_icon/gamehome_duolebi_icon_common.png'
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_template_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "gamehome_duolecoin_icon_not_found", "多乐币图标未找到")
                    pytest.exit("测试查找多乐币图标失败: 未找到多乐币图标", returncode=1)

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"多乐币图标位置: ({x}, {y}), 置信度: {confidence:.3f}", "多乐币图标查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "gamehome_duolecoin_icon_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试查找多乐币图标失败: {e}",returncode=1)

    @allure.feature("每日签到")
    @allure.story("签到入口红点逻辑验证")
    def test_signin_dialog_reddot_show(self,driver):
        """测试签到入口红点是否显示"""
        with allure.step("执行邮件请求脚本"):
            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'email_request.sh')
            try:
                result = subprocess.run(['bash', script_path], capture_output=True, text=True, timeout=600)
                if result.returncode != 0:
                    allure.attach(result.stderr, "脚本执行错误", allure.attachment_type.TEXT)
                    pytest.exit(f"邮件请求脚本执行失败: {result.stderr}", returncode=1)
                allure.attach(result.stdout, "脚本执行输出", allure.attachment_type.TEXT)
            except subprocess.TimeoutExpired:
                pytest.exit("邮件请求脚本执行超时", returncode=1)
            except Exception as e:
                pytest.exit(f"执行邮件请求脚本时发生异常: {e}", returncode=1)
        
        with allure.step("查找签到入口红点"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_signin_reddot_button_common.png'
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_template_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_reddot_button_not_found", "签到入口红点未找到")
                    pytest.exit("测试查找签到入口红点失败: 未找到签到入口红点", returncode=1)

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"签到入口红点位置: ({x}, {y}), 置信度: {confidence:.3f}", "签到入口红点查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "signin_reddot_button_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试查找签到入口红点失败: {e}",returncode=1)

        with allure.step("点击签到入口红点"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/signin_dialog/signin_dialog_title_text_common.png'
                driver.click(x, y)
                time.sleep(2)
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_template_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_dialog_title_text_not_found", "签到弹窗标题未找到")
                    pytest.fail("测试失败: 点击签到入口红点后，未找到签到弹窗")

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"签到入口红点位置: ({x}, {y}), 置信度: {confidence:.3f}", "签到入口红点查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "signin_reddot_button_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试点击签到入口红点失败: {e}",returncode=1)

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
                    result = image_matcher.find_template_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_button_not_found", "签到按钮未找到")
                    pytest.exit("测试查找签到弹窗失败: 未找到签到按钮", returncode=1)

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
                template = 'src/resources/templates/common/signin_dialog/signin_dialog_text/signin_dialog_title_text_common.png'
                driver.click(x, y)
                time.sleep(2)
                result = image_matcher.find_template_in_screenshot(template,threshold=0.6)
                if not result:
                    result = image_matcher.find_template_in_screenshot(template,threshold=0.45)
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.45)
                    attach_screenshot_to_allure(driver, "signin_dialog_title_text_not_found", "签到弹窗标题未找到")
                    pytest.fail("测试失败: 点击签到按钮后，未找到签到弹窗标题")

                x, y, confidence = result
                x, y, confidence = int(x), int(y), float(confidence)
                allure.attach(f"签到弹窗标题位置: ({x}, {y}), 置信度: {confidence:.3f}", "签到弹窗标题查找结果",allure.attachment_type.TEXT)
                image_matcher.create_marked_screenshot_for_single_template(template,threshold=0.6)
                
            except Exception as e:
                attach_screenshot_to_allure(driver, "signin_button_not_found", f"[{get_current_time_str()}] 用例发生异常，立即退出")
                pytest.exit(f"测试点击签到按钮失败: {e}",returncode=1)


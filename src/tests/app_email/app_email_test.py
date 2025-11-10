"""
多乐五子棋应用邮件相关功能测试
此脚本用于自动连接设备、启动多乐五子棋应用、等待特定界面出现并执行邮件相关功能操作。
"""
import uiautomator2 as u2
import requests
import json
import time
import pytest
import allure
import subprocess
import os

# 导入工具函数
from src.utils.image_utils import create_image_matcher
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str

# 设置应用包名
os.environ["APP_PACKAGE"] = "com.duole.wuziqihd"

class TestDuoleWuZiQiAppEmail:
    """多乐五子棋应用邮件相关功能测试类"""

    @pytest.fixture(scope="class")
    def driver(self):
        """初始化UIAutomator2驱动并启动应用"""
        d = u2.connect()
        
        # 检查 app 是否已运行
        current_app = d.app_current()
        if current_app.get('package') != 'com.duole.wuziqihd':
            # 只有在 app 未运行时才启动
            try:
                d.app_stop("com.duole.wuziqihd")
                time.sleep(2)
            except Exception:
                pass
            d.app_start("com.duole.wuziqihd")
        
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

    @allure.feature("底导邮件")
    @allure.story("邮件红点展示和退场逻辑")
    def test_email_reddot_and_exit_logic(self, driver):
        """测试邮件红点展示和退场逻辑"""
        
        with allure.step("判断是否展示红点，如果没有红点，发请求展示红点"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_email_button_reddot_count_1_common.png'
                result = image_matcher.find_template_in_screenshot(template, threshold=1)
                if not result:
                    # 未找到红点，先创建标记截图
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=1)
                    attach_screenshot_to_allure(driver, "email_reddot_not_found_before_request", "未找到邮件红点，准备执行邮件请求脚本")
                                        
                    try:
                        url = "http://120.53.247.249:8012/mails/send"
                        payload = {
                            "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                            "mailInfo": {
                                "userlist": [461684],
                                "addresser": "多乐五子棋团队",
                                "title": "滕王阁序",
                                "content": "豫章故郡",
                                "days": 1,
                                "type": 0,
                                "props": [
                                    {
                                        "proptype": 0,
                                        "propid": 0,
                                        "delta": 400000
                                    },
                                    {
                                        "proptype": 0,
                                        "propid": 2,
                                        "delta": 4
                                    }
                                ],
                                "from": 3,
                                "extraInfo": {
                                    "type": 1,
                                    "extra": ""
                                }
                            }   
                        }
                        payload["mailInfo"] = json.dumps(payload["mailInfo"])
                        response = requests.post(url, data=payload)
                        
                        # 检查响应状态
                        if response.status_code != 200:
                            allure.attach(f"HTTP状态码: {response.status_code}\n响应内容: {response.text}", "邮件请求失败", allure.attachment_type.TEXT)
                            pytest.exit(f"邮件请求失败: HTTP {response.status_code}, {response.text}", returncode=1)
                        
                        # 附加响应内容到Allure报告
                        allure.attach(response.text, "邮件请求响应", allure.attachment_type.TEXT)
                        print(f"邮件请求成功: {response.text}")

                        # 脚本执行成功后，等待一段时间让应用更新界面
                        time.sleep(5)
                        
                        # 再次尝试查找红点
                        with allure.step("邮件请求后再次查找红点"):
                            found_threshold = 1.0
                            result = image_matcher.find_template_in_screenshot(template, threshold=found_threshold)
                            if not result:
                                found_threshold = 0.6
                                result = image_matcher.find_template_in_screenshot(template,threshold=found_threshold)
                            if not result:
                                found_threshold = 0.45
                                result = image_matcher.find_template_in_screenshot(template, threshold=found_threshold)
                            if result:
                                x, y, confidence = result
                                x, y, confidence = int(x), int(y), float(confidence)
                                allure.attach(f"邮件请求后找到红点位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}", "邮件请求后红点查找结果", allure.attachment_type.TEXT)
                                # 创建标记截图，使用实际找到时的阈值
                                image_matcher.create_marked_screenshot_for_single_template(template, threshold=found_threshold)
                                # 附加普通截图以便查看完整界面
                                attach_screenshot_to_allure(driver, "email_reddot_found_after_request", "邮件请求后成功找到邮件红点")
                            else:
                                # 仍未找到红点
                                image_matcher.create_marked_screenshot_for_single_template(template, threshold=0.45)
                                attach_screenshot_to_allure(driver, "email_reddot_not_found_after_request", "邮件请求后仍未找到邮件红点")
                                pytest.exit("邮件请求后仍未找到邮件红点", returncode=1)
                                
                    except requests.exceptions.Timeout:
                        attach_screenshot_to_allure(driver, "email_request_timeout", f"[{get_current_time_str()}] 邮件请求超时")
                        pytest.exit("邮件请求超时", returncode=1)
                    except requests.exceptions.RequestException as e:
                        attach_screenshot_to_allure(driver, "email_request_error", f"[{get_current_time_str()}] 邮件请求异常: {e}")
                        pytest.exit(f"执行邮件请求时发生异常: {e}", returncode=1)
                    except Exception as e:
                        attach_screenshot_to_allure(driver, "email_request_unknown_error", f"[{get_current_time_str()}] 邮件请求发生未知异常: {e}")
                        pytest.exit(f"执行邮件请求时发生未知异常: {e}", returncode=1)
                else:
                    # 第一次就找到红点，记录结果
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(f"首次查找即找到邮件红点位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: 1", "邮件红点查找结果", allure.attachment_type.TEXT)
                    # 创建标记截图，使用实际查找时的阈值
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=1)
                    # 附加普通截图以便查看完整界面
                    attach_screenshot_to_allure(driver, "email_reddot_found_on_first_attempt", "首次查找即找到邮件红点")
                    
            except Exception as e:
                attach_screenshot_to_allure(driver, "email_reddot_test_error", f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}")
                pytest.exit(f"测试邮件红点失败: {e}", returncode=1)

        with allure.step("有红点，点击底导邮件按钮进入邮件页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_email_button_reddot_count_1_common.png'
                result = image_matcher.find_template_in_screenshot(template, threshold=1)
                found_threshold = 1.0
                if not result:
                    result = image_matcher.find_template_in_screenshot(template, threshold=0.6)
                    found_threshold = 0.6
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=0.6)
                    attach_screenshot_to_allure(driver, "email_button_not_found", "没有找到带有红点的邮件按钮")
                    pytest.exit("没有找到带有红点的邮件按钮", returncode=1)

                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(f"带有红点的邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}", "查找带红点的邮件按钮结果", allure.attachment_type.TEXT)
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=found_threshold)
                    attach_screenshot_to_allure(driver, "email_button_found", "找到了带有红点的邮件按钮")
                    driver.click(x, y)
                    time.sleep(2)
                    
                    # 验证是否进入邮件页面
                    with allure.step("验证是否进入邮件页面"):
                        unread_template = 'src/resources/templates/common/email/email_button/email_select_unread_button_common.png'
                        unread_result = image_matcher.find_template_in_screenshot(unread_template, threshold=0.6)
                        if not unread_result:
                            unread_result = image_matcher.find_template_in_screenshot(unread_template, threshold=0.45)
                        if unread_result:
                            unread_x, unread_y, unread_confidence = unread_result
                            unread_x, unread_y, unread_confidence = int(unread_x), int(unread_y), float(unread_confidence)
                            allure.attach(f"未读邮件按钮位置: ({unread_x}, {unread_y}), 置信度: {unread_confidence:.3f}", "邮件页面验证结果", allure.attachment_type.TEXT)
                            image_matcher.create_marked_screenshot_for_single_template(unread_template, threshold=0.6)
                            attach_screenshot_to_allure(driver, "email_page_verified", "成功进入邮件页面")
                        else:
                            image_matcher.create_marked_screenshot_for_single_template(unread_template, threshold=0.45)
                            attach_screenshot_to_allure(driver, "email_page_not_found", "未找到邮件页面，未读邮件按钮不存在")
                            pytest.exit("点击邮件按钮后，未找到邮件页面（未读邮件按钮不存在）", returncode=1)
                    
            
            except Exception as e:
                attach_screenshot_to_allure(driver, "email_button_click_error", f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}")
                pytest.exit(f"测试点击邮件按钮失败: {e}", returncode=1)

        with allure.step("点击查看按钮阅读邮件"):
            try:
                image_matcher = create_image_matcher(driver)
                template = 'src/resources/templates/common/email/email_button/email_view_button_common.png'
                result = image_matcher.find_template_in_screenshot(template, threshold=0.6)
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(template, threshold=0.45)
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=0.45)
                    attach_screenshot_to_allure(driver, "view_button_not_found", "没有找到查看按钮")
                    pytest.exit("没有找到查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(f"查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}", "查看按钮查找结果", allure.attachment_type.TEXT)
                    image_matcher.create_marked_screenshot_for_single_template(template, threshold=found_threshold)
                    attach_screenshot_to_allure(driver, "view_button_found", "找到了查看按钮")
                    driver.click(x, y)
                    time.sleep(2)

                    # 验证是否进入邮件详情页面
                    with allure.step("验证是否进入邮件详情页面"):
                        title_template = 'src/resources/templates/common/email_detail/email_detail_text/email_detail_title_text_common.png'
                        title_result = image_matcher.find_template_in_screenshot(title_template, threshold=0.6)
                        if not title_result:
                            title_result = image_matcher.find_template_in_screenshot(title_template, threshold=0.45)
                        if not title_result:
                            image_matcher.create_marked_screenshot_for_single_template(title_template, threshold=0.45)
                            attach_screenshot_to_allure(driver, "title_not_found", "没有找到邮件标题")
                            pytest.exit("没有找到邮件标题", returncode=1)
                        else:
                            title_x, title_y, title_confidence = title_result
                            title_x, title_y, title_confidence = int(title_x), int(title_y), float(title_confidence)
                            allure.attach(f"邮件标题位置: ({title_x}, {title_y}), 置信度: {title_confidence:.3f}", "邮件标题查找结果", allure.attachment_type.TEXT)
                            image_matcher.create_marked_screenshot_for_single_template(title_template, threshold=0.6)
                            attach_screenshot_to_allure(driver, "title_found", "找到了邮件标题")
            
            except Exception as e:
                attach_screenshot_to_allure(driver, "email_detail_page_error", f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}")
                pytest.exit(f"测试进入邮件详情页面失败: {e}", returncode=1)

        with allure.step("返回大厅验证红点是否消失"):
            try:
                image_matcher = create_image_matcher(driver)
                
                # 第一步：找到并点击邮件详情页的关闭按钮
                with allure.step("点击邮件详情页关闭按钮"):
                    close_template = 'src/resources/templates/common/email_detail/email_detail_button/email_detail_close_button_common.png'
                    close_result = image_matcher.find_template_in_screenshot(close_template, threshold=0.6)
                    found_threshold = 0.6
                    if not close_result:
                        close_result = image_matcher.find_template_in_screenshot(close_template, threshold=0.45)
                        found_threshold = 0.45
                    if not close_result:
                        image_matcher.create_marked_screenshot_for_single_template(close_template, threshold=0.45)
                        attach_screenshot_to_allure(driver, "close_button_not_found", "没有找到邮件详情页关闭按钮")
                        pytest.exit("没有找到邮件详情页关闭按钮", returncode=1)
                    else:
                        close_x, close_y, close_confidence = close_result
                        close_x, close_y, close_confidence = int(close_x), int(close_y), float(close_confidence)
                        allure.attach(f"关闭按钮位置: ({close_x}, {close_y}), 置信度: {close_confidence:.3f}, 查找阈值: {found_threshold}", "关闭按钮查找结果", allure.attachment_type.TEXT)
                        image_matcher.create_marked_screenshot_for_single_template(close_template, threshold=found_threshold)
                        attach_screenshot_to_allure(driver, "close_button_found", "找到了关闭按钮")
                        driver.click(close_x, close_y)
                        time.sleep(2)
                
                # 第二步：找到并点击返回按钮
                with allure.step("点击返回按钮"):
                    back_template = 'src/resources/templates/common/email/email_button/email_back_button_common.png'
                    back_result = image_matcher.find_template_in_screenshot(back_template, threshold=0.6)
                    found_threshold = 0.6
                    if not back_result:
                        back_result = image_matcher.find_template_in_screenshot(back_template, threshold=0.45)
                        found_threshold = 0.45
                    if not back_result:
                        image_matcher.create_marked_screenshot_for_single_template(back_template, threshold=0.45)
                        attach_screenshot_to_allure(driver, "back_button_not_found", "没有找到返回按钮")
                        pytest.exit("没有找到返回按钮", returncode=1)
                    else:
                        back_x, back_y, back_confidence = back_result
                        back_x, back_y, back_confidence = int(back_x), int(back_y), float(back_confidence)
                        allure.attach(f"返回按钮位置: ({back_x}, {back_y}), 置信度: {back_confidence:.3f}, 查找阈值: {found_threshold}", "返回按钮查找结果", allure.attachment_type.TEXT)
                        image_matcher.create_marked_screenshot_for_single_template(back_template, threshold=found_threshold)
                        attach_screenshot_to_allure(driver, "back_button_found", "找到了返回按钮")
                        driver.click(back_x, back_y)
                        time.sleep(2)
                
                # 第三步：验证是否回到大厅，并检查邮件按钮红点是否消失
                with allure.step("验证回到大厅，检查邮件按钮红点是否消失"):
                    no_reddot_template = 'src/resources/templates/common/gamehome/gamehome_button/gamehome_email_button_not_reddot_common.png'
                    no_reddot_result = image_matcher.find_template_in_screenshot(no_reddot_template, threshold=0.6)
                    found_threshold = 0.6
                    if not no_reddot_result:
                        no_reddot_result = image_matcher.find_template_in_screenshot(no_reddot_template, threshold=0.45)
                        found_threshold = 0.45
                    if no_reddot_result:
                        # 找到了没有红点的邮件按钮，说明红点已消失，测试通过
                        no_reddot_x, no_reddot_y, no_reddot_confidence = no_reddot_result
                        no_reddot_x, no_reddot_y, no_reddot_confidence = int(no_reddot_x), int(no_reddot_y), float(no_reddot_confidence)
                        allure.attach(f"无红点邮件按钮位置: ({no_reddot_x}, {no_reddot_y}), 置信度: {no_reddot_confidence:.3f}, 查找阈值: {found_threshold}", "红点消失验证结果", allure.attachment_type.TEXT)
                        image_matcher.create_marked_screenshot_for_single_template(no_reddot_template, threshold=found_threshold)
                        attach_screenshot_to_allure(driver, "reddot_disappeared", "成功验证：邮件按钮红点已消失")
                    else:
                        # 未找到没有红点的邮件按钮，说明红点还在，测试失败
                        image_matcher.create_marked_screenshot_for_single_template(no_reddot_template, threshold=0.45)
                        attach_screenshot_to_allure(driver, "reddot_still_exists", "验证失败：邮件按钮红点仍然存在")
                        pytest.exit("验证失败：返回大厅后，邮件按钮红点仍然存在", returncode=1)
            
            except Exception as e:
                attach_screenshot_to_allure(driver, "return_to_gamehome_error", f"[{get_current_time_str()}] 返回大厅验证红点消失时发生异常: {e}")
                pytest.exit(f"返回大厅验证红点消失失败: {e}", returncode=1)
            
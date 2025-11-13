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
import os


from src.config.template_paths import TemplatePaths
from src.utils.image_utils import create_image_matcher
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str

os.environ["APP_PACKAGE"] = "com.duole.wuziqihd"


class TestDuoleWuZiQiAppEmail:
    """多乐五子棋应用邮件相关功能测试类"""

    @pytest.fixture(scope="function")
    def driver(self):
        """初始化UIAutomator2驱动并启动应用"""
        d = u2.connect()
        try:
            d.app_stop("com.duole.wuziqihd")
            time.sleep(1)
        except Exception:
            pass
        d.app_start("com.duole.wuziqihd")
        time.sleep(10)

        try:
            image_matcher = create_image_matcher(d)

            announcement_title_template = TemplatePaths.announcement.text.title
            announcement_close_template = TemplatePaths.announcement.button.close

            signin_title_template = TemplatePaths.signin_dialog.text.title
            signin_close_template = TemplatePaths.signin_dialog.button.close

            def close_popup(title_template, close_template, title_desc, close_desc):
                title_result = image_matcher.find_template_in_screenshot(
                    title_template, threshold=0.6
                )
                if not title_result:
                    title_result = image_matcher.find_template_in_screenshot(
                        title_template, threshold=0.45
                    )
                if not title_result:
                    return False

                close_result = image_matcher.find_template_in_screenshot(
                    close_template, threshold=0.6
                )
                if not close_result:
                    close_result = image_matcher.find_template_in_screenshot(
                        close_template, threshold=0.45
                    )
                if not close_result:
                    return False

                close_x, close_y, _ = close_result
                d.click(int(close_x), int(close_y))
                time.sleep(1)
                return True

            max_attempts = 3
            for _ in range(max_attempts):
                closed_any = False
                if close_popup(
                    announcement_title_template,
                    announcement_close_template,
                    "公告弹窗",
                    "公告关闭按钮",
                ):
                    closed_any = True
                if close_popup(
                    signin_title_template,
                    signin_close_template,
                    "签到弹窗",
                    "签到关闭按钮",
                ):
                    closed_any = True
                if not closed_any:
                    break
        except Exception:
            pass
        yield d

        try:
            d.app_stop("com.duole.wuziqihd")
        except Exception:
            pass

    @allure.feature("底导邮件")
    @allure.story("邮件入口红点")
    @allure.title("测试邮件红点展示和退场逻辑")
    def test_email_reddot_and_exit_logic(self, driver: u2.Device):
        """测试邮件红点展示和退场逻辑"""

        with allure.step("判断是否展示红点，如果没有红点，发请求展示红点"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.gamehome.button.email_reddot
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=1
                )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=1
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_reddot_not_found_before_request",
                        "未找到邮件红点，准备执行邮件请求脚本",
                    )

                    try:
                        url = "http://120.53.247.249:8012/mails/send"
                        mail_info = {
                            "userlist": [461684],
                            "addresser": "多乐五子棋团队",
                            "title": "测试红点退场逻辑",
                            "content": "测试红点退场逻辑",
                            "days": 1,
                            "type": 0,
                            "props": [
                                {"proptype": 0, "propid": 0, "delta": 400000},
                                {"proptype": 0, "propid": 2, "delta": 4},
                            ],
                            "from": 3,
                            "extraInfo": {"type": 1, "extra": ""},
                        }

                        for send_index in range(1):
                            payload = {
                                "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                                "mailInfo": json.dumps(mail_info),
                            }
                            response = requests.post(url, data=payload)
                            if response.status_code != 200:
                                allure.attach(
                                    f"第 {send_index + 1} 次发送失败\nHTTP状态码: {response.status_code}\n响应内容: {response.text}",
                                    "邮件请求失败",
                                    allure.attachment_type.TEXT,
                                )
                                pytest.exit(
                                    f"邮件请求失败(第 {send_index + 1} 次): HTTP {response.status_code}, {response.text}",
                                    returncode=1,
                                )

                            allure.attach(
                                response.text,
                                f"第 {send_index + 1} 次邮件请求响应",
                                allure.attachment_type.TEXT,
                            )
                            print(
                                f"第 {send_index + 1} 次邮件请求成功: {response.text}"
                            )
                            time.sleep(2)
                        time.sleep(5)

                        with allure.step("邮件请求后再次查找红点"):
                            found_threshold = 1.0
                            result = image_matcher.find_template_in_screenshot(
                                template, threshold=found_threshold
                            )
                            if not result:
                                found_threshold = 0.6
                                result = image_matcher.find_template_in_screenshot(
                                    template, threshold=found_threshold
                                )
                            if not result:
                                found_threshold = 0.45
                                result = image_matcher.find_template_in_screenshot(
                                    template, threshold=found_threshold
                                )
                            if result:
                                x, y, confidence = result
                                x, y, confidence = int(x), int(y), float(confidence)
                                allure.attach(
                                    f"邮件请求后找到红点位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                                    "邮件请求后红点查找结果",
                                    allure.attachment_type.TEXT,
                                )
                                image_matcher.create_marked_screenshot_for_single_template(
                                    template, threshold=found_threshold
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "email_reddot_found_after_request",
                                    "邮件请求后成功找到邮件红点",
                                )
                            else:
                                image_matcher.create_marked_screenshot_for_single_template(
                                    template, threshold=0.45
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "email_reddot_not_found_after_request",
                                    "邮件请求后仍未找到邮件红点",
                                )
                                pytest.exit("邮件请求后仍未找到邮件红点", returncode=1)

                    except requests.exceptions.Timeout:
                        attach_screenshot_to_allure(
                            driver,
                            "email_request_timeout",
                            f"[{get_current_time_str()}] 邮件请求超时",
                        )
                        pytest.exit("邮件请求超时", returncode=1)
                    except requests.exceptions.RequestException as e:
                        attach_screenshot_to_allure(
                            driver,
                            "email_request_error",
                            f"[{get_current_time_str()}] 邮件请求异常: {e}",
                        )
                        pytest.exit(f"执行邮件请求时发生异常: {e}", returncode=1)
                    except Exception as e:
                        attach_screenshot_to_allure(
                            driver,
                            "email_request_unknown_error",
                            f"[{get_current_time_str()}] 邮件请求发生未知异常: {e}",
                        )
                        pytest.exit(f"执行邮件请求时发生未知异常: {e}", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"首次查找即找到邮件红点位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: 1",
                        "邮件红点查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=1
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_reddot_found_on_first_attempt",
                        "首次查找即找到邮件红点",
                    )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_reddot_test_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试邮件红点失败: {e}", returncode=1)

        with allure.step("有红点，点击底导邮件按钮进入邮件页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.gamehome.button.email_reddot
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=1
                )
                found_threshold = 1.0
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.6
                    )
                    found_threshold = 0.6
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.6
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_not_found", "没有找到带有红点的邮件按钮"
                    )
                    pytest.exit("没有找到带有红点的邮件按钮", returncode=1)

                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"带有红点的邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找带红点的邮件按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了带有红点的邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)

                    with allure.step("验证是否进入邮件页面"):
                        unread_template = TemplatePaths.email.button.select_unread
                        unread_result = image_matcher.find_template_in_screenshot(
                            unread_template, threshold=0.6
                        )
                        if not unread_result:
                            unread_result = image_matcher.find_template_in_screenshot(
                                unread_template, threshold=0.45
                            )
                        if unread_result:
                            unread_x, unread_y, unread_confidence = unread_result
                            unread_x, unread_y, unread_confidence = (
                                int(unread_x),
                                int(unread_y),
                                float(unread_confidence),
                            )
                            allure.attach(
                                f"未读邮件按钮位置: ({unread_x}, {unread_y}), 置信度: {unread_confidence:.3f}",
                                "邮件页面验证结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                unread_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver, "email_page_verified", "成功进入邮件页面"
                            )
                        else:
                            image_matcher.create_marked_screenshot_for_single_template(
                                unread_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_page_not_found",
                                "未找到邮件页面，未读邮件按钮不存在",
                            )
                            pytest.exit(
                                "点击邮件按钮后，未找到邮件页面（未读邮件按钮不存在）",
                                returncode=1,
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击邮件按钮失败: {e}", returncode=1)

        with allure.step("点击查看按钮阅读邮件"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.view
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_not_found", "没有找到查看按钮"
                    )
                    pytest.exit("没有找到查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查看按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_found", "找到了查看按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)

                    # 验证是否进入邮件详情页面
                    with allure.step("验证是否进入邮件详情页面"):
                        title_template = TemplatePaths.email_detail.text.title
                        title_result = image_matcher.find_template_in_screenshot(
                            title_template, threshold=0.6
                        )
                        if not title_result:
                            title_result = image_matcher.find_template_in_screenshot(
                                title_template, threshold=0.45
                            )
                        if not title_result:
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "title_not_found", "没有找到邮件标题"
                            )
                            pytest.exit("没有找到邮件标题", returncode=1)
                        else:
                            title_x, title_y, title_confidence = title_result
                            title_x, title_y, title_confidence = (
                                int(title_x),
                                int(title_y),
                                float(title_confidence),
                            )
                            allure.attach(
                                f"邮件标题位置: ({title_x}, {title_y}), 置信度: {title_confidence:.3f}",
                                "邮件标题查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver, "title_found", "找到了邮件标题"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入邮件详情页面失败: {e}", returncode=1)

        with allure.step("返回大厅验证红点是否消失"):
            try:
                image_matcher = create_image_matcher(driver)

                with allure.step("点击邮件详情页关闭按钮"):
                    close_template = TemplatePaths.email_detail.button.close
                    close_result = image_matcher.find_template_in_screenshot(
                        close_template, threshold=0.6
                    )
                    found_threshold = 0.6
                    if not close_result:
                        close_result = image_matcher.find_template_in_screenshot(
                            close_template, threshold=0.45
                        )
                        found_threshold = 0.45
                    if not close_result:
                        image_matcher.create_marked_screenshot_for_single_template(
                            close_template, threshold=0.45
                        )
                        attach_screenshot_to_allure(
                            driver,
                            "close_button_not_found",
                            "没有找到邮件详情页关闭按钮",
                        )
                        pytest.exit("没有找到邮件详情页关闭按钮", returncode=1)
                    else:
                        close_x, close_y, close_confidence = close_result
                        close_x, close_y, close_confidence = (
                            int(close_x),
                            int(close_y),
                            float(close_confidence),
                        )
                        allure.attach(
                            f"关闭按钮位置: ({close_x}, {close_y}), 置信度: {close_confidence:.3f}, 查找阈值: {found_threshold}",
                            "关闭按钮查找结果",
                            allure.attachment_type.TEXT,
                        )
                        image_matcher.create_marked_screenshot_for_single_template(
                            close_template, threshold=found_threshold
                        )
                        attach_screenshot_to_allure(
                            driver, "close_button_found", "找到了关闭按钮"
                        )
                        driver.click(close_x, close_y)
                        time.sleep(2)

                with allure.step("点击返回按钮"):
                    back_template = TemplatePaths.email.button.back
                    back_result = image_matcher.find_template_in_screenshot(
                        back_template, threshold=0.6
                    )
                    found_threshold = 0.6
                    if not back_result:
                        back_result = image_matcher.find_template_in_screenshot(
                            back_template, threshold=0.45
                        )
                        found_threshold = 0.45
                    if not back_result:
                        image_matcher.create_marked_screenshot_for_single_template(
                            back_template, threshold=0.45
                        )
                        attach_screenshot_to_allure(
                            driver, "back_button_not_found", "没有找到返回按钮"
                        )
                        pytest.exit("没有找到返回按钮", returncode=1)
                    else:
                        back_x, back_y, back_confidence = back_result
                        back_x, back_y, back_confidence = (
                            int(back_x),
                            int(back_y),
                            float(back_confidence),
                        )
                        allure.attach(
                            f"返回按钮位置: ({back_x}, {back_y}), 置信度: {back_confidence:.3f}, 查找阈值: {found_threshold}",
                            "返回按钮查找结果",
                            allure.attachment_type.TEXT,
                        )
                        image_matcher.create_marked_screenshot_for_single_template(
                            back_template, threshold=found_threshold
                        )
                        attach_screenshot_to_allure(
                            driver, "back_button_found", "找到了返回按钮"
                        )
                        driver.click(back_x, back_y)
                        time.sleep(2)

                with allure.step("验证回到大厅，检查邮件按钮红点是否消失"):
                    no_reddot_template = TemplatePaths.gamehome.button.email
                    no_reddot_result = image_matcher.find_template_in_screenshot(
                        no_reddot_template, threshold=0.6
                    )
                    found_threshold = 0.6
                    if not no_reddot_result:
                        no_reddot_result = image_matcher.find_template_in_screenshot(
                            no_reddot_template, threshold=0.45
                        )
                        found_threshold = 0.45
                    if no_reddot_result:
                        no_reddot_x, no_reddot_y, no_reddot_confidence = (
                            no_reddot_result
                        )
                        no_reddot_x, no_reddot_y, no_reddot_confidence = (
                            int(no_reddot_x),
                            int(no_reddot_y),
                            float(no_reddot_confidence),
                        )
                        allure.attach(
                            f"无红点邮件按钮位置: ({no_reddot_x}, {no_reddot_y}), 置信度: {no_reddot_confidence:.3f}, 查找阈值: {found_threshold}",
                            "红点消失验证结果",
                            allure.attachment_type.TEXT,
                        )
                        image_matcher.create_marked_screenshot_for_single_template(
                            no_reddot_template, threshold=found_threshold
                        )
                        attach_screenshot_to_allure(
                            driver, "reddot_disappeared", "成功验证：邮件按钮红点已消失"
                        )
                    else:
                        image_matcher.create_marked_screenshot_for_single_template(
                            no_reddot_template, threshold=0.45
                        )
                        attach_screenshot_to_allure(
                            driver,
                            "reddot_still_exists",
                            "验证失败：邮件按钮红点仍然存在",
                        )
                        pytest.exit(
                            "验证失败：返回大厅后，邮件按钮红点仍然存在", returncode=1
                        )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "return_to_gamehome_error",
                    f"[{get_current_time_str()}] 返回大厅验证红点消失时发生异常: {e}",
                )
                pytest.exit(f"返回大厅验证红点消失失败: {e}", returncode=1)

    @allure.feature("邮件详情页")
    @allure.story("邮件奖励领取")
    @allure.title("测试未读邮件列表领取邮件奖励")
    @allure.label("order", "1")
    def test_email_unread_list_reward_logic(self, driver: u2.Device):
        """验证奖励领取逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)

                    with allure.step("验证是否进入了邮件页"):
                        unread_template = TemplatePaths.email.button.select_unread
                        first_found_threshold = 0.6
                        unread_result = image_matcher.find_template_in_screenshot(
                            unread_template, first_found_threshold
                        )
                        if not unread_result:
                            second_found_threshold = 0.45
                            unread_result = image_matcher.find_template_in_screenshot(
                                unread_template, first_found_threshold
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                unread_template, threshold=second_found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_button_not_found",
                                "没有找到未读邮件按钮",
                            )
                        else:
                            unread_x, unread_y, unread_confidence = unread_result
                            unread_x, unread_y, unread_confidence = (
                                int(unread_x),
                                int(unread_y),
                                float(unread_confidence),
                            )
                            allure.attach(
                                f"未读邮件按钮位置: ({unread_x}, {unread_y}), 置信度: {unread_confidence:.3f}",
                                "未读邮件按钮查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                unread_template, threshold=first_found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_button_found",
                                "找到了未读邮件按钮",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击邮件按钮失败: {e}", returncode=1)

        with allure.step("发请求发送邮件x个，x=1（可配置）"):
            try:
                url = "http://120.53.247.249:8012/mails/send"
                mail_info = {
                    "userlist": [461684],
                    "addresser": "多乐五子棋团队",
                    "title": "测试领取奖励逻辑",
                    "content": "测试领取奖励逻辑",
                    "days": 1,
                    "type": 0,
                    "props": [
                        {"proptype": 0, "propid": 0, "delta": 400000},
                        {"proptype": 0, "propid": 2, "delta": 4},
                    ],
                    "from": 3,
                    "extraInfo": {"type": 1, "extra": ""},
                }

                for send_index in range(1):
                    payload = {
                        "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                        "mailInfo": json.dumps(mail_info),
                    }
                    response = requests.post(url, data=payload)
                    if response.status_code != 200:
                        allure.attach(
                            f"第 {send_index + 1} 次发送失败\nHTTP状态码: {response.status_code}\n响应内容: {response.text}",
                            "邮件请求失败",
                            allure.attachment_type.TEXT,
                        )
                        pytest.exit(
                            f"邮件请求失败(第 {send_index + 1} 次): HTTP {response.status_code}, {response.text}",
                            returncode=1,
                        )

                    allure.attach(
                        response.text,
                        f"第 {send_index + 1} 次邮件请求响应",
                        allure.attachment_type.TEXT,
                    )
                    print(f"第 {send_index + 1} 次邮件请求成功: {response.text}")
                    time.sleep(2)

                time.sleep(5)
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_one_key_view_request_error",
                    f"[{get_current_time_str()}] 发送邮件请求失败: {e}",
                )
                pytest.exit(f"测试未读列表一键查看前置发送邮件失败: {e}", returncode=1)

        with allure.step("点击查看按钮阅读邮件，进入邮件详情页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.view
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_not_found", "没有找到查看按钮"
                    )
                    pytest.exit("没有找到查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查看按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_found", "找到了查看按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了邮件详情页"):
                        title_template = TemplatePaths.email_detail.text.title
                        title_result = image_matcher.find_template_in_screenshot(
                            title_template, threshold=0.6
                        )
                        if not title_result:
                            title_result = image_matcher.find_template_in_screenshot(
                                title_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "title_not_found", "没有找到邮件标题"
                            )
                            pytest.exit("没有找到邮件标题", returncode=1)
                        else:
                            title_x, title_y, title_confidence = title_result
                            title_x, title_y, title_confidence = (
                                int(title_x),
                                int(title_y),
                                float(title_confidence),
                            )
                            allure.attach(
                                f"邮件标题位置: ({title_x}, {title_y}), 置信度: {title_confidence:.3f}",
                                "邮件标题查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver, "title_found", "找到了邮件标题"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入邮件详情页面失败: {e}", returncode=1)

        with allure.step("点击领取按钮，领取奖励"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email_detail.button.receive
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "receive_button_not_found", "没有找到领取按钮"
                    )
                    pytest.exit("没有找到领取按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"领取按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "领取按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "receive_button_found", "找到了领取按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否领取了奖励"):
                        reward_template = TemplatePaths.email_detail.text.get
                        reward_result = image_matcher.find_template_in_screenshot(
                            reward_template, threshold=0.6
                        )
                        if not reward_result:
                            reward_result = image_matcher.find_template_in_screenshot(
                                reward_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "reward_not_found", "没有找到奖励动画"
                            )
                            pytest.exit("没有找到奖励动画", returncode=1)
                        else:
                            reward_x, reward_y, reward_confidence = reward_result
                            reward_x, reward_y, reward_confidence = (
                                int(reward_x),
                                int(reward_y),
                                float(reward_confidence),
                            )
                            allure.attach(
                                f"奖励动画位置: ({reward_x}, {reward_y}), 置信度: {reward_confidence:.3f}",
                                "奖励动画查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "reward_found", "找到了奖励动画"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试领取奖励失败: {e}", returncode=1)

    @allure.feature("邮件详情页")
    @allure.story("邮件奖励领取")
    @allure.title("测试已读邮件列表领取邮件奖励")
    @allure.label("order", "2")
    def test_email_read_list_reward_logic(self, driver: u2.Device):
        """验证已读邮件列表领取逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表失败: {e}", returncode=1)

        with allure.step("点击已读按钮，进入已读列表"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.unselect_read
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "unselect_read_button_not_found", "没有找到已读按钮"
                    )
                    pytest.exit("没有找到已读按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"已读按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "已读按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "unselect_read_button_found", "找到了已读按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了已读列表"):
                        read_list_template = TemplatePaths.email.button.select_read
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_not_found",
                                "没有找到已读邮件列表",
                            )
                            pytest.exit("没有找到已读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"已读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "已读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_found",
                                "找到了已读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入已读邮件列表失败: {e}", returncode=1)

        with allure.step("点击未领取按钮，进入未领取邮件详情页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.unreceive
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "unselect_receive_button_not_found",
                        "没有找到未领取按钮",
                    )
                    pytest.exit("没有找到未领取按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"未领取按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "未领取按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "unselect_receive_button_found", "找到了未领取按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未领取邮件详情页"):
                        receive_template = TemplatePaths.email_detail.button.receive
                        receive_result = image_matcher.find_template_in_screenshot(
                            receive_template, threshold=0.6
                        )
                        if not receive_result:
                            receive_result = image_matcher.find_template_in_screenshot(
                                receive_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                receive_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "receive_button_not_found", "没有找到领取按钮"
                            )
                            pytest.exit("没有找到领取按钮", returncode=1)
                        else:
                            receive_x, receive_y, receive_confidence = receive_result
                            receive_x, receive_y, receive_confidence = (
                                int(receive_x),
                                int(receive_y),
                                float(receive_confidence),
                            )
                            allure.attach(
                                f"领取按钮位置: ({receive_x}, {receive_y}), 置信度: {receive_confidence:.3f}",
                                "领取按钮查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "receive_button_found", "找到了领取按钮"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击未领取按钮失败: {e}", returncode=1)

        with allure.step("点击领取按钮，领取未领取邮件奖励"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email_detail.button.receive
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "receive_button_not_found", "没有找到领取按钮"
                    )
                    pytest.exit("没有找到领取按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"领取按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "领取按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "receive_button_found", "找到了领取按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否领取了奖励"):
                        reward_template = TemplatePaths.email_detail.text.get
                        reward_result = image_matcher.find_template_in_screenshot(
                            reward_template, threshold=0.6
                        )
                        if not reward_result:
                            reward_result = image_matcher.find_template_in_screenshot(
                                reward_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "reward_not_found", "没有找到奖励动画"
                            )
                            pytest.exit("没有找到奖励动画", returncode=1)
                        else:
                            reward_x, reward_y, reward_confidence = reward_result
                            reward_x, reward_y, reward_confidence = (
                                int(reward_x),
                                int(reward_y),
                                float(reward_confidence),
                            )
                            allure.attach(
                                f"奖励动画位置: ({reward_x}, {reward_y}), 置信度: {reward_confidence:.3f}",
                                "奖励动画查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "reward_found", "找到了奖励动画"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击领取按钮失败: {e}", returncode=1)

    @allure.feature("邮件详情页")
    @allure.story("邮件删除")
    @allure.label("order", "3")
    @allure.title("测试单个邮件删除")
    def test_email_single_delete_logic(self, driver: u2.Device):
        """验证单个邮件删除逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表失败: {e}", returncode=1)

        with allure.step("点击已读邮件进入已读邮件列表"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.unselect_read
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_select_read_list_not_found",
                        "没有找到已读邮件列表",
                    )
                    pytest.exit("没有找到已读邮件列表", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"已读邮件列表位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "已读邮件列表查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_select_read_list_found", "找到了已读邮件列表"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了已读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_read
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_not_found",
                                "没有找到已读邮件列表",
                            )
                            pytest.exit("没有找到已读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"已读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "已读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_found",
                                "找到了已读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入已读邮件列表失败: {e}", returncode=1)

        with allure.step("点击红点退场邮件，进入邮件详情页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.text.title
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_title_reddot_exit_text_not_found",
                        "没有找到红点退场邮件",
                    )
                    pytest.exit("没有找到红点退场邮件", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"红点退场邮件位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "红点退场邮件查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_title_reddot_exit_text_found",
                        "找到了红点退场邮件",
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了邮件详情页"):
                        detail_template = TemplatePaths.email_detail.text.title
                        detail_result = image_matcher.find_template_in_screenshot(
                            detail_template, threshold=0.6
                        )
                        if not detail_result:
                            detail_result = image_matcher.find_template_in_screenshot(
                                detail_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                detail_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_detail_title_text_not_found",
                                "没有找到邮件标题",
                            )
                            pytest.exit("没有找到邮件标题", returncode=1)
                        else:
                            detail_x, detail_y, detail_confidence = detail_result
                            detail_x, detail_y, detail_confidence = (
                                int(detail_x),
                                int(detail_y),
                                float(detail_confidence),
                            )
                            allure.attach(
                                f"邮件标题文本位置: ({detail_x}, {detail_y}), 置信度: {detail_confidence:.3f}",
                                "邮件标题文本查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                detail_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_detail_title_text_found",
                                "找到了邮件标题",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入已查看邮件详情页失败: {e}", returncode=1)

        with allure.step("点击删除按钮，展示二次确认弹窗"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email_detail.button.delete
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "delete_mail_button_not_found", "没有找到删除按钮"
                    )
                    pytest.exit("没有找到删除按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"删除按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "删除按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "delete_mail_button_found", "找到了删除按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)

                    with allure.step("验证是否展示二次确认弹窗"):
                        tip_template = TemplatePaths.email_detail.text.tip
                        tip_result = image_matcher.find_template_in_screenshot(
                            tip_template, threshold=0.6
                        )
                        if not tip_result:
                            tip_result = image_matcher.find_template_in_screenshot(
                                tip_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                tip_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_detail_tip_not_found",
                                "没有找到二次确认弹窗",
                            )
                            pytest.exit("没有找到二次确认弹窗", returncode=1)
                        else:
                            tip_x, tip_y, tip_confidence = tip_result
                            tip_x, tip_y, tip_confidence = (
                                int(tip_x),
                                int(tip_y),
                                float(tip_confidence),
                            )
                            allure.attach(
                                f"二次确认弹窗位置: ({tip_x}, {tip_y}), 置信度: {tip_confidence:.3f}",
                                "二次确认弹窗查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "email_detail_tip_found", "找到了二次确认弹窗"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击删除按钮失败: {e}", returncode=1)

        with allure.step("点击二次确认弹窗确定按钮，删除邮件，验证是否删除成功"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email_detail.button.confirm
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_detail_confirm_button_not_found",
                        "没有找到确定按钮",
                    )
                    pytest.exit("没有找到确定按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"确定按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "确定按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_detail_confirm_button_found", "找到了确定按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step(
                        "验证是否删除了邮件，查找已经删除的红点退场的邮件"
                    ):
                        delete_template = TemplatePaths.email.text.title
                        delete_result = image_matcher.find_template_in_screenshot(
                            delete_template, threshold=0.6
                        )
                        if delete_result:
                            delete_x, delete_y, delete_confidence = delete_result
                            delete_x, delete_y, delete_confidence = (
                                int(delete_x),
                                int(delete_y),
                                float(delete_confidence),
                            )
                            allure.attach(
                                f"红点退场邮件仍然存在，位置: ({delete_x}, {delete_y}), 置信度: {delete_confidence:.3f}",
                                "红点退场邮件查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                delete_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_title_reddot_exit_found",
                                "仍然找到了红点退场邮件",
                            )
                            pytest.exit(
                                "删除邮件失败，红点退场邮件仍然存在", returncode=1
                            )
                        else:
                            delete_result = image_matcher.find_template_in_screenshot(
                                delete_template, threshold=0.45
                            )
                            if delete_result:
                                delete_x, delete_y, delete_confidence = delete_result
                                delete_x, delete_y, delete_confidence = (
                                    int(delete_x),
                                    int(delete_y),
                                    float(delete_confidence),
                                )
                                allure.attach(
                                    f"红点退场邮件仍然存在(低阈值)，位置: ({delete_x}, {delete_y}), 置信度: {delete_confidence:.3f}",
                                    "红点退场邮件查找结果(低阈值)",
                                    allure.attachment_type.TEXT,
                                )
                                image_matcher.create_marked_screenshot_for_single_template(
                                    delete_template, threshold=0.45
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "email_title_reddot_exit_found_low_threshold",
                                    "低阈值仍然找到了红点退场邮件",
                                )
                                pytest.exit(
                                    "删除邮件失败，红点退场邮件仍然存在(低阈值)",
                                    returncode=1,
                                )
                            else:
                                allure.attach(
                                    "未找到红点退场邮件",
                                    "红点退场邮件查找结果",
                                    allure.attachment_type.TEXT,
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "email_title_reddot_exit_not_found",
                                    "未找到红点退场邮件，删除成功",
                                )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试确认删除邮件失败: {e}", returncode=1)

    @allure.feature("邮件页")
    @allure.story("未读邮件列表-一键查看")
    @allure.label("order", "4")
    @allure.title("测试未读邮件列表一键查看逻辑，有奖励")
    def test_email_unread_list_one_key_view_logic_with_reward(self, driver: u2.Device):
        """验证未读邮件列表一键查看逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表失败: {e}", returncode=1)

        with allure.step("进入邮件页，发请求发送邮件x个，x=3（可配置）"):
            try:
                url = "http://120.53.247.249:8012/mails/send"
                mail_info = {
                    "userlist": [461684],
                    "addresser": "多乐五子棋团队",
                    "title": "测试红点退场逻辑",
                    "content": "测试红点退场逻辑",
                    "days": 1,
                    "type": 0,
                    "props": [
                        {"proptype": 0, "propid": 0, "delta": 400000},
                        {"proptype": 0, "propid": 2, "delta": 4},
                    ],
                    "from": 3,
                    "extraInfo": {"type": 1, "extra": ""},
                }

                for send_index in range(3):
                    payload = {
                        "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                        "mailInfo": json.dumps(mail_info),
                    }
                    response = requests.post(url, data=payload)
                    if response.status_code != 200:
                        allure.attach(
                            f"第 {send_index + 1} 次发送失败\nHTTP状态码: {response.status_code}\n响应内容: {response.text}",
                            "邮件请求失败",
                            allure.attachment_type.TEXT,
                        )
                        pytest.exit(
                            f"邮件请求失败(第 {send_index + 1} 次): HTTP {response.status_code}, {response.text}",
                            returncode=1,
                        )

                    allure.attach(
                        response.text,
                        f"第 {send_index + 1} 次邮件请求响应",
                        allure.attachment_type.TEXT,
                    )
                    print(f"第 {send_index + 1} 次邮件请求成功: {response.text}")
                    time.sleep(2)

                time.sleep(5)
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_one_key_view_request_error",
                    f"[{get_current_time_str()}] 发送邮件请求失败: {e}",
                )
                pytest.exit(f"测试未读列表一键查看前置发送邮件失败: {e}", returncode=1)

        with allure.step("点击未读邮件列表一键查看按钮，进入邮件详情页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.one_key_view
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_view_button_not_found",
                        "没有找到一键查看按钮",
                    )
                    pytest.exit("没有找到一键查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"一键查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "一键查看按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_one_key_view_button_found", "找到了一键查看按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证奖励邮件标题是否展示"):
                        reward_template = TemplatePaths.email.text.get
                        reward_result = image_matcher.find_template_in_screenshot(
                            reward_template, threshold=0.6
                        )
                        found_threshold = 0.6
                        if not reward_result:
                            reward_result = image_matcher.find_template_in_screenshot(
                                reward_template, threshold=0.45
                            )
                            found_threshold = 0.45
                        if reward_result:
                            reward_x, reward_y, reward_confidence = reward_result
                            reward_x, reward_y, reward_confidence = (
                                int(reward_x),
                                int(reward_y),
                                float(reward_confidence),
                            )
                            allure.attach(
                                f"奖励标题位置: ({reward_x}, {reward_y}), 置信度: {reward_confidence:.3f}, 查找阈值: {found_threshold}",
                                "奖励标题查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_reward_title_found",
                                "找到了奖励邮件标题",
                            )
                        else:
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_reward_title_not_found",
                                "未找到奖励邮件标题",
                            )
                            pytest.exit("未找到奖励邮件标题", returncode=1)

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表一键查看失败: {e}", returncode=1)

    @allure.feature("邮件页")
    @allure.story("未读邮件列表-一键查看")
    @allure.label("order", "5")
    @allure.title("测试未读邮件列表一键查看逻辑，无奖励")
    def test_email_unread_list_one_key_view_logic_no_reward(self, driver: u2.Device):
        """验证未读邮件列表一键查看逻辑，无奖励"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表: {e}", returncode=1)

        with allure.step("进入邮件页，发请求发送邮件x个，x=3（可配置）"):
            try:
                url = "http://120.53.247.249:8012/mails/send"
                mail_info = {
                    "userlist": [461684],
                    "addresser": "多乐五子棋团队",
                    "title": "测试红点退场逻辑",
                    "content": "测试红点退场逻辑",
                    "days": 1,
                    "type": 0,
                    "props": [],
                    "from": 3,
                    "extraInfo": {"type": 1, "extra": ""},
                }

                for send_index in range(3):
                    payload = {
                        "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                        "mailInfo": json.dumps(mail_info),
                    }
                    response = requests.post(url, data=payload)
                    if response.status_code != 200:
                        allure.attach(
                            f"第 {send_index + 1} 次发送失败\nHTTP状态码: {response.status_code}\n响应内容: {response.text}",
                            "邮件请求失败",
                            allure.attachment_type.TEXT,
                        )
                        pytest.exit(
                            f"邮件请求失败(第 {send_index + 1} 次): HTTP {response.status_code}, {response.text}",
                            returncode=1,
                        )

                    allure.attach(
                        response.text,
                        f"第 {send_index + 1} 次邮件请求响应",
                        allure.attachment_type.TEXT,
                    )
                    print(f"第 {send_index + 1} 次邮件请求成功: {response.text}")
                    time.sleep(2)

                time.sleep(5)
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_one_key_view_request_error",
                    f"[{get_current_time_str()}] 发送邮件请求失败: {e}",
                )
                pytest.exit(f"测试未读列表一键查看前置发送邮件失败: {e}", returncode=1)

        with allure.step("点击未读邮件列表一键查看按钮"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.one_key_view
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_view_button_not_found",
                        "没有找到一键查看按钮",
                    )
                    pytest.exit("没有找到一键查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"一键查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "一键查看按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_one_key_view_button_found", "找到了一键查看按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否显示空列表图标"):
                        null_template = TemplatePaths.email.icon.none
                        null_result = image_matcher.find_template_in_screenshot(
                            null_template, threshold=0.6
                        )
                        if not null_result:
                            null_result = image_matcher.find_template_in_screenshot(
                                null_template, threshold=0.45
                            )
                        if null_result:
                            null_x, null_y, null_confidence = null_result
                            null_x, null_y, null_confidence = (
                                int(null_x),
                                int(null_y),
                                float(null_confidence),
                            )
                            allure.attach(
                                f"空列表图标位置: ({null_x}, {null_y}), 置信度: {null_confidence:.3f}",
                                "空列表图标查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                null_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_null_icon_found",
                                "找到了空列表图标",
                            )
                        else:
                            image_matcher.create_marked_screenshot_for_single_template(
                                null_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_null_icon_not_found",
                                "未找到空列表图标",
                            )
                            pytest.exit("未找到空列表图标", returncode=1)

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表一键查看失败: {e}", returncode=1)

    @allure.feature("邮件页")
    @allure.story("已读邮件列表-一键删除")
    @allure.label("order", "5")
    @allure.title("测试已读邮件列表一键删除逻辑，无奖励")
    def test_email_read_list_one_key_delete_logic(self, driver: u2.Device):
        """验证已读邮件列表一键删除逻辑"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表失败: {e}", returncode=1)

        with allure.step("点击已读邮件进入已读邮件列表"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.unselect_read
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_select_read_list_not_found",
                        "没有找到已读邮件列表",
                    )
                    pytest.exit("没有找到已读邮件列表", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"已读邮件列表位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "已读邮件列表查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_select_read_list_found", "找到了已读邮件列表"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了已读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_read
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_not_found",
                                "没有找到已读邮件列表",
                            )
                            pytest.exit("没有找到已读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"已读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "已读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_read_list_found",
                                "找到了已读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入已读邮件列表失败: {e}", returncode=1)

        with allure.step("点击已读邮件列表一键删除按钮，展示二次确认弹窗"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.email.button.one_key_delete
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_delete_button_not_found",
                        "没有找到一键删除按钮",
                    )
                    pytest.exit("没有找到一键删除按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"一键删除按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "一键删除按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_delete_button_found",
                        "找到了一键删除按钮",
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否展示二次确认弹窗"):
                        tip_template = TemplatePaths.email_detail.text.tip
                        tip_result = image_matcher.find_template_in_screenshot(
                            tip_template, threshold=0.6
                        )
                        if not tip_result:
                            tip_result = image_matcher.find_template_in_screenshot(
                                tip_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                tip_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_detail_tip_not_found",
                                "没有找到二次确认弹窗",
                            )
                            pytest.exit("没有找到二次确认弹窗", returncode=1)
                        else:
                            tip_x, tip_y, tip_confidence = tip_result
                            tip_x, tip_y, tip_confidence = (
                                int(tip_x),
                                int(tip_y),
                                float(tip_confidence),
                            )
                            allure.attach(
                                f"二次确认弹窗位置: ({tip_x}, {tip_y}), 置信度: {tip_confidence:.3f}",
                                "二次确认弹窗查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "email_detail_tip_found", "找到了二次确认弹窗"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击一键删除按钮失败: {e}", returncode=1)

        with allure.step("点击二次确认弹窗确定按钮删除邮件，验证空态图标是否展示"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.confirm_delete
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_confirm_delete_button_not_found",
                        "没有找到确定删除按钮",
                    )
                    pytest.exit("没有找到确定删除按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"确定删除按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "确定删除按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_confirm_delete_button_found",
                        "找到了确定删除按钮",
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否删除了邮件，查找空态图标是否展示"):
                        null_template = TemplatePaths.email.icon.none
                        null_result = image_matcher.find_template_in_screenshot(
                            null_template, threshold=0.6
                        )
                        if not null_result:
                            null_result = image_matcher.find_template_in_screenshot(
                                null_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                null_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "email_null_icon_not_found", "没有找到空态图标"
                            )
                            pytest.exit("没有找到空态图标", returncode=1)
                        else:
                            null_x, null_y, null_confidence = null_result
                            null_x, null_y, null_confidence = (
                                int(null_x),
                                int(null_y),
                                float(null_confidence),
                            )
                            allure.attach(
                                f"空态图标位置: ({null_x}, {null_y}), 置信度: {null_confidence:.3f}",
                                "空态图标查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "email_null_icon_found", "找到了空态图标"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击确定删除按钮失败: {e}", returncode=1)

    @allure.feature("邮件页")
    @allure.story("已读邮件列表-一键删除")
    @allure.label("order", "6")
    @allure.title("测试已读邮件列表一键删除逻辑，有奖励")
    def test_email_read_list_one_key_delete_logic_with_reward(self, driver: u2.Device):
        """验证已读邮件列表一键删除逻辑，有奖励"""
        with allure.step("点击邮件进入邮件页"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.gamehome.button.email
                first_found_threshold = 0.6
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=first_found_threshold
                )
                if not result:
                    second_found_threshold = 0.45
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=second_found_threshold
                    )
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=second_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_not_reddot_button_not_found", "没有找到邮件按钮"
                    )
                    pytest.exit(f"没有找到邮件按钮{e}",returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {first_found_threshold}",
                        "邮件钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=first_found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "email_button_found", "找到了邮件按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了未读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_unread
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                read_list_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_not_found",
                                "没有找到未读邮件列表",
                            )
                            pytest.exit("没有找到未读邮件列表", returncode=1)
                        else:
                            read_list_x, read_list_y, read_list_confidence = (
                                read_list_result
                            )
                            read_list_x, read_list_y, read_list_confidence = (
                                int(read_list_x),
                                int(read_list_y),
                                float(read_list_confidence),
                            )
                            allure.attach(
                                f"未读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                "未读邮件列表查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_select_unread_list_found",
                                "找到了未读邮件列表",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入未读邮件列表失败: {e}", returncode=1)

        with allure.step("发请求发送邮件x个，x=3（可配置）"):
            with allure.step("进入邮件页，发请求发送邮件x个，x=3（可配置）"):
                try:
                    url = "http://120.53.247.249:8012/mails/send"
                    mail_info = {
                        "userlist": [461684],
                        "addresser": "多乐五子棋团队",
                        "title": "测试红点退场逻辑",
                        "content": "测试红点退场逻辑",
                        "days": 1,
                        "type": 0,
                        "props": [
                            {"proptype": 0, "propid": 0, "delta": 400000},
                            {"proptype": 0, "propid": 2, "delta": 4},
                        ],
                        "from": 3,
                        "extraInfo": {"type": 1, "extra": ""},
                    }

                    for send_index in range(1):
                        payload = {
                            "passwd": "sscvrbbt532dfdgnmjyukukueghkkuhegnklethjk7gcs",
                            "mailInfo": json.dumps(mail_info),
                        }
                        response = requests.post(url, data=payload)
                        if response.status_code != 200:
                            allure.attach(
                                f"第 {send_index + 1} 次发送失败\nHTTP状态码: {response.status_code}\n响应内容: {response.text}",
                                "邮件请求失败",
                                allure.attachment_type.TEXT,
                            )
                            pytest.exit(
                                f"邮件请求失败(第 {send_index + 1} 次): HTTP {response.status_code}, {response.text}",
                                returncode=1,
                            )

                        allure.attach(
                            response.text,
                            f"第 {send_index + 1} 次邮件请求响应",
                            allure.attachment_type.TEXT,
                        )
                        print(f"第 {send_index + 1} 次邮件请求成功: {response.text}")
                        time.sleep(2)

                    time.sleep(5)
                except Exception as e:
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_view_request_error",
                        f"[{get_current_time_str()}] 发送邮件请求失败: {e}",
                    )
                    pytest.exit(
                        f"测试未读列表一键查看前置发送邮件失败: {e}", returncode=1
                    )

        with allure.step("点击查看按钮阅读邮件"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.view
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_not_found", "没有找到查看按钮"
                    )
                    pytest.exit("没有找到查看按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"查看按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查看按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "view_button_found", "找到了查看按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)

                    # 验证是否进入邮件详情页面
                    with allure.step("验证是否进入邮件详情页面"):
                        title_template = TemplatePaths.email_detail.text.title
                        title_result = image_matcher.find_template_in_screenshot(
                            title_template, threshold=0.6
                        )
                        if not title_result:
                            title_result = image_matcher.find_template_in_screenshot(
                                title_template, threshold=0.45
                            )
                        if not title_result:
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "title_not_found", "没有找到邮件标题"
                            )
                            pytest.exit("没有找到邮件标题", returncode=1)
                        else:
                            title_x, title_y, title_confidence = title_result
                            title_x, title_y, title_confidence = (
                                int(title_x),
                                int(title_y),
                                float(title_confidence),
                            )
                            allure.attach(
                                f"邮件标题位置: ({title_x}, {title_y}), 置信度: {title_confidence:.3f}",
                                "邮件标题查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                title_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver, "title_found", "找到了邮件标题"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试进入邮件详情页面失败: {e}", returncode=1)

        with allure.step("点击返回按钮退出邮件详情页"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email_detail.button.close
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "close_button_not_found", "没有找到关闭按钮"
                    )
                    pytest.exit("没有找到关闭按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"关闭按钮位置: ({x}, {y}), 置信度: {confidence:.3f}",
                        "关闭按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "close_button_found", "找到了关闭按钮"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否退出了邮件详情页"):
                        back_template = TemplatePaths.email.button.back
                        back_result = image_matcher.find_template_in_screenshot(
                            back_template, threshold=0.6
                        )
                        if not back_result:
                            back_result = image_matcher.find_template_in_screenshot(
                                back_template, threshold=0.45
                            )
                        if not back_result:
                            image_matcher.create_marked_screenshot_for_single_template(
                                back_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver, "back_button_not_found", "没有找到返回按钮"
                            )
                            pytest.exit("没有找到返回按钮", returncode=1)
                        else:
                            back_x, back_y, back_confidence = back_result
                            back_x, back_y, back_confidence = (
                                int(back_x),
                                int(back_y),
                                float(back_confidence),
                            )
                            allure.attach(
                                f"返回按钮位置: ({back_x}, {back_y}), 置信度: {back_confidence:.3f}",
                                "返回按钮查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                back_template, threshold=0.6
                            )
                            attach_screenshot_to_allure(
                                driver, "back_button_found", "找到了返回按钮"
                            )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击返回按钮退出邮件详情页面失败: {e}", returncode=1)

        with allure.step("点击已读邮件进入已读邮件列表"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.unselect_read
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver, "unselect_read_button_not_found", "没有找到已读邮件列表"
                    )
                    pytest.exit("没有找到已读邮件列表", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"已读邮件列表位置: ({x}, {y}), 置信度: {confidence:.3f}",
                        "已读邮件列表查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "unselect_read_button_found", "找到了已读邮件列表"
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否进入了已读邮件列表"):
                        read_list_template = TemplatePaths.email.button.select_read
                        read_list_result = image_matcher.find_template_in_screenshot(
                            read_list_template, threshold=0.6
                        )
                        if not read_list_result:
                            read_list_result = (
                                image_matcher.find_template_in_screenshot(
                                    read_list_template, threshold=0.45
                                )
                            )
                            if not read_list_result:
                                image_matcher.create_marked_screenshot_for_single_template(
                                    read_list_template, threshold=0.45
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "read_list_not_found",
                                    "没有找到已读邮件列表",
                                )
                                pytest.exit("没有找到已读邮件列表", returncode=1)
                            else:
                                read_list_x, read_list_y, read_list_confidence = (
                                    read_list_result
                                )
                                read_list_x, read_list_y, read_list_confidence = (
                                    int(read_list_x),
                                    int(read_list_y),
                                    float(read_list_confidence),
                                )
                                allure.attach(
                                    f"已读邮件列表位置: ({read_list_x}, {read_list_y}), 置信度: {read_list_confidence:.3f}",
                                    "已读邮件列表查找结果",
                                    allure.attachment_type.TEXT,
                                )
                                image_matcher.create_marked_screenshot_for_single_template(
                                    read_list_template, threshold=0.6
                                )
                                attach_screenshot_to_allure(
                                    driver, "read_list_found", "找到了已读邮件列表"
                                )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_detail_page_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击已读邮件进入已读邮件列表失败: {e}", returncode=1)

        with allure.step("点击已读邮件列表一键删除按钮，展示二次确认弹窗"):
            image_matcher = create_image_matcher(driver)
            try:
                template = TemplatePaths.email.button.one_key_delete
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_delete_button_not_found",
                        "没有找到一键删除按钮",
                    )
                    pytest.exit("没有找到一键删除按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"一键删除按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "一键删除按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_one_key_delete_button_found",
                        "找到了一键删除按钮",
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证是否展示二次确认弹窗"):
                        tip_template = TemplatePaths.email_detail.text.tip
                        tip_result = image_matcher.find_template_in_screenshot(
                            tip_template, threshold=0.6
                        )
                        if not tip_result:
                            tip_result = image_matcher.find_template_in_screenshot(
                                tip_template, threshold=0.45
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                tip_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_detail_tip_not_found",
                                "没有找到二次确认弹窗",
                            )
                            pytest.exit("没有找到二次确认弹窗", returncode=1)
                        else:
                            tip_x, tip_y, tip_confidence = tip_result
                            tip_x, tip_y, tip_confidence = (
                                int(tip_x),
                                int(tip_y),
                                float(tip_confidence),
                            )
                            allure.attach(
                                f"二次确认弹窗位置: ({tip_x}, {tip_y}), 置信度: {tip_confidence:.3f}",
                                "二次确认弹窗查找结果",
                                allure.attachment_type.TEXT,
                            )
                            attach_screenshot_to_allure(
                                driver, "email_detail_tip_found", "找到了二次确认弹窗"
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击一键删除按钮失败: {e}", returncode=1)

        with allure.step("点击二次确认弹窗确定按钮删除邮件，验证空态图标是否展示"):
            try:
                image_matcher = create_image_matcher(driver)
                template = TemplatePaths.email.button.confirm_delete
                result = image_matcher.find_template_in_screenshot(
                    template, threshold=0.6
                )
                found_threshold = 0.6
                if not result:
                    result = image_matcher.find_template_in_screenshot(
                        template, threshold=0.45
                    )
                    found_threshold = 0.45
                if not result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=0.45
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_confirm_delete_button_not_found",
                        "没有找到确定删除按钮",
                    )
                    pytest.exit("没有找到确定删除按钮", returncode=1)
                else:
                    x, y, confidence = result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"确定删除按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "确定删除按钮查找结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "email_confirm_delete_button_found",
                        "找到了确定删除按钮",
                    )
                    driver.click(x, y)
                    time.sleep(2)
                    with allure.step("验证奖励邮件标题是否展示"):
                        reward_template = TemplatePaths.email.text.get
                        reward_result = image_matcher.find_template_in_screenshot(
                            reward_template, threshold=0.6
                        )
                        found_threshold = 0.6
                        if not reward_result:
                            reward_result = image_matcher.find_template_in_screenshot(
                                reward_template, threshold=0.45
                            )
                            found_threshold = 0.45
                        if reward_result:
                            reward_x, reward_y, reward_confidence = reward_result
                            reward_x, reward_y, reward_confidence = (
                                int(reward_x),
                                int(reward_y),
                                float(reward_confidence),
                            )
                            allure.attach(
                                f"奖励标题位置: ({reward_x}, {reward_y}), 置信度: {reward_confidence:.3f}, 查找阈值: {found_threshold}",
                                "奖励标题查找结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_reward_title_found",
                                "找到了奖励邮件标题",
                            )
                        else:
                            image_matcher.create_marked_screenshot_for_single_template(
                                reward_template, threshold=0.45
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "email_reward_title_not_found",
                                "未找到奖励邮件标题",
                            )
                            pytest.exit("未找到奖励邮件标题", returncode=1)

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "email_button_click_error",
                    f"[{get_current_time_str()}] 用例发生异常，立即退出: {e}",
                )
                pytest.exit(f"测试点击确定删除按钮失败: {e}", returncode=1)

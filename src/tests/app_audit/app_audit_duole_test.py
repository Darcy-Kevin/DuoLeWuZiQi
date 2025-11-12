"""
官方多乐包审核中测试
"""

import uiautomator2 as u2
import pytest
import time
import allure

from src.config.template_paths import TemplatePaths
from src.utils.image_utils import create_image_matcher
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str


class TestAppAuditDuole:
    """官方多乐包审核中测试"""

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

    @allure.feature("审核中")
    @allure.story("设置页面")
    @allure.title("切换为审核中状态")
    def test_switch_to_audit_mode(self, driver: u2.Device):
        """切换为审核中状态"""
        with allure.step("大厅点击更多按钮"):
            image_matcher = create_image_matcher(driver)
            try:
                more_template = TemplatePaths.gamehome.button.more
                found_threshold = 0.6
                more_result = image_matcher.find_template_in_screenshot(
                    more_template, threshold=found_threshold
                )
                if not more_result:
                    found_threshold = 0.45
                    more_result = image_matcher.find_template_in_screenshot(
                        more_template, threshold=found_threshold
                    )
                if not more_result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        more_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "more_button_not_found", "没有找到更多按钮"
                    )
                    pytest.exit("没有找到更多按钮", returncode=1)

                else:
                    x, y, confidence = more_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"带有红点的邮件按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找带红点的邮件按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        more_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "more_button_marked", "更多按钮匹配成功"
                    )
                    driver.click(x, y)
                    time.sleep(1)

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "more_button_test_error",
                    f"大厅点击更多按钮失败: {e}",
                )
                pytest.exit(f"大厅点击更多按钮失败: {e}", returncode=1)

        with allure.step("更多菜单中点击设置按钮"):
            image_matcher = create_image_matcher(driver)
            try:
                setting_template = TemplatePaths.gamehome.button.setting
                found_threshold = 0.6
                setting_result = image_matcher.find_template_in_screenshot(
                    setting_template, threshold=found_threshold
                )
                if not setting_result:
                    found_threshold = 0.45
                    setting_result = image_matcher.find_template_in_screenshot(
                        setting_template, threshold=found_threshold
                    )
                if not setting_result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        setting_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "setting_button_not_found", "没有找到设置按钮"
                    )
                    pytest.exit("没有找到设置按钮", returncode=1)

                else:
                    x, y, confidence = setting_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"设置按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找设置按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        setting_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "setting_button_marked", "设置按钮匹配成功"
                    )
                    driver.click(x, y)
                    time.sleep(1)

                with allure.step("验证是否进入了设置页"):
                    image_matcher = create_image_matcher(driver)
                    gamesetting_template = TemplatePaths.setting.button.gamesetting
                    found_threshold = 0.6
                    gamesetting_result = image_matcher.find_template_in_screenshot(
                        gamesetting_template, threshold=found_threshold
                    )
                    if not gamesetting_result:
                        found_threshold = 0.45
                        gamesetting_result = image_matcher.find_template_in_screenshot(
                            gamesetting_template, threshold=found_threshold
                        )
                    if not gamesetting_result:
                        image_matcher.create_marked_screenshot_for_single_template(
                            gamesetting_template, threshold=found_threshold
                        )
                        attach_screenshot_to_allure(
                            driver,
                            "gamesetting_button_not_found",
                            "没有找到游戏设置按钮",
                        )
                        pytest.exit("没有找到游戏设置按钮", returncode=1)

                    else:
                        x, y, confidence = gamesetting_result
                        x, y, confidence = int(x), int(y), float(confidence)
                        allure.attach(
                            f"游戏设置按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                            "查找游戏设置按钮结果",
                            allure.attachment_type.TEXT,
                        )
                        image_matcher.create_marked_screenshot_for_single_template(
                            gamesetting_template, threshold=found_threshold
                        )
                        attach_screenshot_to_allure(
                            driver,
                            "gamesetting_button_marked",
                            "游戏设置按钮匹配成功",
                        )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "setting_button_test_error",
                    f"更多菜单中点击设置按钮失败: {e}",
                )

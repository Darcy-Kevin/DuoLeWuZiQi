"""
本项目用于非审核时间测试审核中状态，以及审核中状态的切换
"""

import uiautomator2 as u2
import pytest
import time
import allure

from src.config.template_paths import TemplatePaths
from src.utils.image_utils import create_image_matcher
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str


class TestAppAuditDuoleStaging:
    """多乐包审核中测试"""

    @pytest.fixture(scope="class")
    def driver(self):
        """初始化UIAutomator2驱动并启动应用（类级别，所有测试用例共享）"""
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

        # 类级别的清理：所有测试用例执行完后才停止app
        try:
            d.app_stop("com.duole.wuziqihd")
        except Exception:
            pass

    @allure.feature("审核中")
    @allure.story("设置页面")
    @allure.title("切换为审核中状态")
    def test_switch_to_audit_mode_staging(self, driver: u2.Device):
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

        with allure.step("快速点击背景音乐文案10次，开启审核中状态"):
            image_matcher = create_image_matcher(driver)
            try:
                music_template = TemplatePaths.setting.text.music
                found_threshold = 0.6
                music_result = image_matcher.find_template_in_screenshot(
                    music_template, threshold=found_threshold
                )
                if not music_result:
                    found_threshold = 0.45
                    music_result = image_matcher.find_template_in_screenshot(
                        music_template, threshold=found_threshold
                    )
                if not music_result:
                    image_matcher.create_marked_screenshot_for_single_template(
                        music_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "music_text_not_found",
                        "没有找到背景音乐文案",
                    )
                    pytest.exit("没有找到背景音乐文案", returncode=1)

                else:
                    x, y, confidence = music_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"背景音乐文案位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找背景音乐文案结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        music_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "music_text_marked",
                        "背景音乐文案匹配成功",
                    )
                    image_matcher.quick_click(x, y, times=10, interval=0.05)
                    time.sleep(0.2)  # 短暂等待，让提示出现

                    with allure.step("双重校验：检查审核中或已审核状态"):
                        image_matcher = create_image_matcher(driver)
                        review_template = TemplatePaths.setting.text.review
                        reviewed_template = TemplatePaths.setting.text.reviewed
                        found_threshold = 0.6

                        # 由于提示会在3-5秒消失，需要快速多次检查
                        # 在5秒内，每0.2秒检查一次
                        max_attempts = 25  # 5秒 / 0.2秒 = 25次
                        check_interval = 0.2
                        review_found = False
                        reviewed_found = False

                        for attempt in range(max_attempts):
                            # 先检查 review（审核中）
                            review_result = image_matcher.find_template_in_screenshot(
                                review_template, threshold=found_threshold
                            )
                            if not review_result:
                                review_threshold = 0.45
                                review_result = (
                                    image_matcher.find_template_in_screenshot(
                                        review_template, threshold=review_threshold
                                    )
                                )
                            else:
                                review_threshold = found_threshold

                            # 如果找到 review，则通过
                            if review_result:
                                x, y, confidence = review_result
                                x, y, confidence = int(x), int(y), float(confidence)
                                review_found = True

                                allure.attach(
                                    f"✅ 找到审核中提示 - 位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {review_threshold}, 尝试次数: {attempt + 1}",
                                    "双重校验结果：审核中状态",
                                    allure.attachment_type.TEXT,
                                )
                                image_matcher.create_marked_screenshot_for_single_template(
                                    review_template, threshold=review_threshold
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "review_text_marked",
                                    "审核中提示匹配成功",
                                )
                                break

                            # 如果没找到 review，检查 reviewed（已审核）
                            reviewed_result = image_matcher.find_template_in_screenshot(
                                reviewed_template, threshold=found_threshold
                            )
                            if not reviewed_result:
                                reviewed_threshold = 0.45
                                reviewed_result = (
                                    image_matcher.find_template_in_screenshot(
                                        reviewed_template, threshold=reviewed_threshold
                                    )
                                )
                            else:
                                reviewed_threshold = found_threshold

                            # 如果找到 reviewed，则失败
                            if reviewed_result:
                                x, y, confidence = reviewed_result
                                x, y, confidence = int(x), int(y), float(confidence)
                                reviewed_found = True

                                allure.attach(
                                    f"❌ 找到已审核提示 - 位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {reviewed_threshold}, 尝试次数: {attempt + 1}",
                                    "双重校验结果：已审核状态（失败）",
                                    allure.attachment_type.TEXT,
                                )
                                image_matcher.create_marked_screenshot_for_single_template(
                                    reviewed_template, threshold=reviewed_threshold
                                )
                                attach_screenshot_to_allure(
                                    driver,
                                    "reviewed_text_marked",
                                    "已审核提示匹配成功（验证失败）",
                                )
                                pytest.exit(
                                    "找到已审核状态，当前已经是审核中了，验证失败",
                                    returncode=1,
                                )

                            time.sleep(check_interval)

                        # 如果两个都没找到，也失败
                        if not review_found and not reviewed_found:
                            image_matcher.create_marked_screenshot_for_single_template(
                                review_template, threshold=found_threshold
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                reviewed_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "both_text_not_found",
                                "既没有找到审核中提示，也没有找到已审核提示",
                            )
                            pytest.exit(
                                "既没有找到审核中提示，也没有找到已审核提示，验证失败",
                                returncode=1,
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "review_text_test_error",
                    f"切换审核中状态失败: {e}",
                )
                pytest.exit(f"切换审核中状态失败: {e}", returncode=1)

    @allure.feature("审核中")
    @allure.story("设置页面")
    @allure.title("测试审核中不展示检查更新按钮")
    def test_audit_mode_staging_not_show_update_button(self, driver: u2.Device):
        """测试审核中不展示检查更新按钮"""
        with allure.step("设置页寻找检查更新按钮"):
            image_matcher = create_image_matcher(driver)
            try:
                update_button_template = TemplatePaths.setting.button.update
                found_threshold = 0.6
                update_result = image_matcher.find_template_in_screenshot(
                    update_button_template, threshold=found_threshold
                )
                if update_result:
                    x, y, confidence = update_result
                    x, y, confidence = int(x), int(y), float(confidence)

                    allure.attach(
                        f"找到检查更新按钮 - 位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "验证结果：找到检查更新按钮（失败）",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        update_button_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "update_button_found",
                        "找到检查更新按钮（验证失败）",
                    )
                    pytest.exit(
                        "审核中状态下不应该显示检查更新按钮，但找到了，验证失败",
                        returncode=1,
                    )

                # 如果没找到检查更新按钮，则成功（符合预期）
                else:
                    allure.attach(
                        f"未找到检查更新按钮 - 查找阈值: {found_threshold}",
                        "验证结果：未找到检查更新按钮（成功）",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        update_button_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "update_button_not_found",
                        "未找到检查更新按钮（验证成功）",
                    )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "update_button_test_error",
                    f"验证检查更新按钮失败: {e}",
                )
                pytest.exit(f"验证检查更新按钮失败: {e}", returncode=1)

        with allure.step("返回游戏大厅"):
            try:
                image_matcher = create_image_matcher(driver)
                back_template = TemplatePaths.setting.button.back
                found_threshold = 0.6
                back_result = image_matcher.find_template_in_screenshot(
                    back_template, threshold=found_threshold
                )
                if not back_result:
                    found_threshold = 0.45
                    back_result = image_matcher.find_template_in_screenshot(
                        back_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver, "back_button_not_found", "没有找到返回按钮"
                    )
                    pytest.exit("没有找到返回按钮", returncode=1)
                else:
                    x, y, confidence = back_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"返回按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找返回按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        back_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "back_button_marked",
                        "返回按钮匹配成功",
                    )
                    driver.click(x, y)
                    time.sleep(1)

                    with allure.step("验证是否回到了游戏大厅"):
                        image_matcher = create_image_matcher(driver)
                        more_template = TemplatePaths.gamehome.button.more
                        found_threshold = 0.6
                        more_result = image_matcher.find_template_in_screenshot(
                            more_template, threshold=found_threshold
                        )
                        if not more_result:
                            pytest.exit("没有找到更多按钮", returncode=1)
                        else:
                            x, y, confidence = more_result
                            x, y, confidence = (
                                int(x),
                                int(y),
                                float(confidence),
                            )
                            allure.attach(
                                f"更多按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                                "查找更多按钮结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                more_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "more_button_marked",
                                "更多按钮匹配成功",
                            )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "back_button_test_error",
                    f"返回按钮测试失败: {e}",
                )
                pytest.exit(f"返回按钮测试失败: {e}", returncode=1)

    @allure.feature("审核中")
    @allure.story("设置页面")
    @allure.title("测试审核中签到不支持分享功能")
    def test_audit_mode_staging_not_support_share_signin(self, driver: u2.Device):
        """测试审核中签到不支持分享功能"""
        with allure.step("点击签到按钮打开签到弹窗"):
            try:
                image_matcher = create_image_matcher(driver)
                signin_template = TemplatePaths.gamehome.button.signin
                found_threshold = 0.6
                signin_result = image_matcher.find_template_in_screenshot(
                    signin_template, threshold=found_threshold
                )
                if not signin_result:
                    found_threshold = 0.45
                    signin_result = image_matcher.find_template_in_screenshot(
                        signin_template, threshold=found_threshold
                    )
                else:
                    x, y, confidence = signin_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"签到按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找签到按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        signin_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "signin_button_marked",
                        "签到按钮匹配成功",
                    )
                    driver.click(x, y)
                    time.sleep(1)

                    with allure.step("验证签到弹窗是否打开"):
                        image_matcher = create_image_matcher(driver)
                        signin_dialog_title_template = (
                            TemplatePaths.signin_dialog.text.title
                        )
                        found_threshold = 0.6
                        signin_dialog_title_result = (
                            image_matcher.find_template_in_screenshot(
                                signin_dialog_title_template,
                                threshold=found_threshold,
                            )
                        )
                        if not signin_dialog_title_result:
                            found_threshold = 0.45
                            signin_dialog_title_result = (
                                image_matcher.find_template_in_screenshot(
                                    signin_dialog_title_template,
                                    threshold=found_threshold,
                                )
                            )
                        else:
                            x, y, confidence = signin_dialog_title_result
                            x, y, confidence = int(x), int(y), float(confidence)
                            allure.attach(
                                f"签到弹窗标题位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                                "查找签到弹窗标题结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                signin_dialog_title_template,
                                threshold=found_threshold,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "signin_dialog_title_marked",
                                "签到弹窗标题匹配成功",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "signin_button_test_error",
                    f"点击签到按钮失败: {e}",
                )
                pytest.exit(f"点击签到按钮失败: {e}", returncode=1)

        with allure.step("验证签到弹窗是否支持分享功能"):
            image_matcher = create_image_matcher(driver)
            try:
                share_template = TemplatePaths.signin_dialog.icon.share
                found_threshold = 0.6
                share_result = image_matcher.find_template_in_screenshot(
                    share_template, threshold=found_threshold
                )
                if share_result:
                    x, y, confidence = share_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"分享按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找分享按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        share_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "share_button_marked",
                        "分享按钮匹配成功",
                    )
                    pytest.exit(
                        "审核中状态下不应该显示分享按钮，但找到了，验证失败",
                        returncode=1,
                    )
                else:
                    allure.attach(
                        f"未找到分享按钮 - 查找阈值: {found_threshold}",
                        "验证结果：未找到分享按钮（成功）",
                        allure.attachment_type.TEXT,
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "share_button_not_found",
                        "未找到分享按钮（验证成功）",
                    )
            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "share_button_test_error",
                    f"验证分享按钮失败: {e}",
                )
                pytest.exit(f"验证分享按钮失败: {e}", returncode=1)

        with allure.step("关闭签到弹窗"):
            image_matcher = create_image_matcher(driver)
            try:
                signin_dialog_close_template = TemplatePaths.signin_dialog.button.close
                found_threshold = 0.6
                signin_dialog_close_result = image_matcher.find_template_in_screenshot(
                    signin_dialog_close_template, threshold=found_threshold
                )
                if not signin_dialog_close_result:
                    found_threshold = 0.45
                    signin_dialog_close_result = (
                        image_matcher.find_template_in_screenshot(
                            signin_dialog_close_template, threshold=found_threshold
                        )
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        signin_dialog_close_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "signin_dialog_close_button_marked",
                        "签到弹窗关闭按钮匹配成功",
                    )
                    pytest.exit("没有找到签到弹窗关闭按钮", returncode=1)
                else:
                    x, y, confidence = signin_dialog_close_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"签到弹窗关闭按钮位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找签到弹窗关闭按钮结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        signin_dialog_close_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "signin_dialog_close_button_marked",
                        "签到弹窗关闭按钮匹配成功",
                    )
                    driver.click(x, y)
                    time.sleep(1)
                    with allure.step("验证是否关闭了签到弹窗"):
                        pvp_template = TemplatePaths.gamehome.button.pvp
                        found_threshold = 0.6
                        pvp_result = image_matcher.find_template_in_screenshot(
                            pvp_template, threshold=found_threshold
                        )
                        if not pvp_result:
                            found_threshold = 0.45
                            pvp_result = image_matcher.find_template_in_screenshot(
                                pvp_template, threshold=found_threshold
                            )
                        if not pvp_result:
                            image_matcher.create_marked_screenshot_for_single_template(
                                pvp_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "gamehome_pvp_button_not_found",
                                "游戏大厅人机对战入口没有找到",
                            )

                        else:
                            x, y, confidence = pvp_result
                            x, y, confidence = int(x), int(y), float(confidence)
                            allure.attach(
                                f"人机对战位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                                "查找人机对战入口结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                pvp_template,
                                threshold=found_threshold,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "gamehome_pvp_button",
                                "在大厅找到了人机对战入口",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "signin_dialog_close_button_test_error",
                    f"关闭签到弹窗失败: {e}",
                )
                pytest.exit(f"关闭签到弹窗失败: {e}", returncode=1)

    @allure.feature("审核中")
    @allure.story("救济金")
    @allure.title("测试审核中救济金不支持分享功能")
    def test_audit_mode_staging_not_support_share_jiujijin(self, driver: u2.Device):
        with allure.step("点击棋力评测入口"):

            try:
                image_matcher = create_image_matcher(driver)
                pve_template = TemplatePaths.gamehome.button.pve
                found_threshold = 0.6
                pve_result = image_matcher.find_template_in_screenshot(
                    pve_template, threshold=found_threshold
                )
                if not pve_result:
                    found_threshold = 0.45
                    pve_result = image_matcher.find_template_in_screenshot(
                        pve_template, threshold=found_threshold
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        pve_template, threshold=found_threshold
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "gamehome_pve_button_not_found",
                        "游戏大厅棋力评测入口没有找到",
                    )
                    pytest.exit(
                        "没有找到棋力测评入口，验证失败",
                        returncode=1,
                    )
                else:
                    x, y, confidence = pve_result
                    x, y, confidence = int(x), int(y), float(confidence)
                    allure.attach(
                        f"棋力评测位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                        "查找棋力评测入口结果",
                        allure.attachment_type.TEXT,
                    )
                    image_matcher.create_marked_screenshot_for_single_template(
                        pve_template,
                        threshold=found_threshold,
                    )
                    attach_screenshot_to_allure(
                        driver,
                        "gamehome_pvp_button",
                        "在大厅找到了棋力评测入口",
                    )
                    driver.click(x, y)
                    time.sleep(1)

                    with allure.step("验证已经进入房间（未匹配状态）"):
                        image_matcher = create_image_matcher(driver)
                        start_template = TemplatePaths.pkhome.button.start
                        found_threshold = 0.6
                        start_result = image_matcher.find_template_in_screenshot(
                            start_template, threshold=found_threshold
                        )
                        if not start_result:
                            found_threshold = 0.45
                            start_result = image_matcher.find_template_in_screenshot(
                                start_template, threshold=found_threshold
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                start_template, threshold=found_threshold
                            )
                            attach_screenshot_to_allure(
                                driver, "start_button_not_found", "房间内没找到开始按钮"
                            )
                            pytest.exit(
                                "开始按钮没有找到，验证失败",
                                returncode=1,
                            )
                        else:
                            x, y, confidence = start_result
                            x, y, confidence = int(x), int(y), float(confidence)
                            allure.attach(
                                f"规则位置: ({x}, {y}), 置信度: {confidence:.3f}, 查找阈值: {found_threshold}",
                                "查找开始按钮结果",
                                allure.attachment_type.TEXT,
                            )
                            image_matcher.create_marked_screenshot_for_single_template(
                                start_template,
                                threshold=found_threshold,
                            )
                            attach_screenshot_to_allure(
                                driver,
                                "rule_text_found",
                                "房间内找到了开始按钮",
                            )

            except Exception as e:
                attach_screenshot_to_allure(
                    driver,
                    "signin_dialog_close_button_test_error",
                    f"点击棋力评测入口失败: {e}",
                )
                pytest.exit(f"点击棋力评测入口失败: {e}", returncode=1)

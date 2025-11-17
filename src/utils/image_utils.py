import cv2
import numpy as np
import uiautomator2 as u2
from typing import Tuple, Optional, List
import os
import allure
from .time_utils import get_current_time_str


class ImageMatcher:
    """图像匹配工具类，用于截图对比和模糊搜索"""

    def __init__(self, driver: u2.Device):
        self.driver = driver
        self.template_dir = "src/resources/templates"
        self.screenshots_dir = "src/resources/screenshots"

        # 确保目录存在
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def take_screenshot(self, filename: str = None) -> str:
        """截取当前屏幕截图"""
        if filename is None:
            filename = f"screenshot_{get_current_time_str()}.png"

        screenshot_path = os.path.join(self.screenshots_dir, filename)
        self.driver.screenshot(screenshot_path)
        return screenshot_path

    def find_template_in_screenshot(
        self,
        template_path: str,
        threshold: float = 0.8,
        take_new_screenshot: bool = True,
    ) -> Optional[Tuple[int, int, float]]:
        """
        在当前屏幕截图中查找模板图像

        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值 (0-1)
            take_new_screenshot: 是否重新截图

        Returns:
            如果找到匹配，返回 (x, y, confidence)，否则返回 None
        """
        try:
            # 截取当前屏幕
            if take_new_screenshot:
                screenshot_path = self.take_screenshot()
            else:
                # 使用最新的截图
                screenshots = [
                    f for f in os.listdir(self.screenshots_dir) if f.endswith(".png")
                ]
                if not screenshots:
                    screenshot_path = self.take_screenshot()
                else:
                    screenshot_path = os.path.join(
                        self.screenshots_dir, max(screenshots)
                    )

            # 读取图像
            screenshot = cv2.imread(screenshot_path)
            template = cv2.imread(template_path)

            if screenshot is None or template is None:
                print(
                    f"无法读取图像文件: screenshot={screenshot_path}, template={template_path}"
                )
                return None

            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # 扫描整个屏幕区域，找到所有可能的匹配位置
            locations = np.where(result >= threshold)
            matches = []

            # 收集所有匹配位置和置信度
            for pt in zip(*locations[::-1]):  # 转换坐标顺序
                confidence = result[pt[1], pt[0]]
                matches.append((pt[0], pt[1], confidence))

            if matches:
                # 按置信度排序，选择最佳匹配
                matches.sort(key=lambda x: x[2], reverse=True)
                best_match = matches[0]

                # 计算模板中心点坐标
                h, w = template.shape[:2]
                center_x = best_match[0] + w // 2
                center_y = best_match[1] + h // 2

                print(f"扫描完成，找到{len(matches)}个匹配位置")
                print(
                    f"最佳匹配: 位置({center_x}, {center_y}), 置信度={best_match[2]:.3f}"
                )

                # 打印前5个最佳匹配
                for i, (x, y, conf) in enumerate(matches[:5]):
                    center_x_temp = x + w // 2
                    center_y_temp = y + h // 2
                    print(
                        f"  匹配{i+1}: 位置({center_x_temp}, {center_y_temp}), 置信度={conf:.3f}"
                    )

                return (center_x, center_y, best_match[2])
            else:
                # 如果没有达到阈值的匹配，找到最高置信度的位置
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                print(f"扫描完成，未找到符合阈值的匹配")
                print(
                    f"最高置信度位置: ({int(center_x)}, {int(center_y)}), 置信度={float(max_val):.3f}, 阈值={threshold}"
                )
                return None

        except Exception as e:
            print(f"图像匹配过程中出错: {e}")
            return None

    def find_multiple_templates(
        self, template_paths: List[str], threshold: float = 0.8
    ) -> List[Tuple[str, int, int, float]]:
        """
        在当前屏幕中查找多个模板图像

        Args:
            template_paths: 模板图像路径列表
            threshold: 匹配阈值

        Returns:
            匹配结果列表 [(template_path, x, y, confidence), ...]
        """
        results = []
        screenshot_path = self.take_screenshot()

        for template_path in template_paths:
            match_result = self.find_template_in_screenshot(
                template_path, threshold, False
            )
            if match_result:
                x, y, confidence = match_result
                results.append((template_path, x, y, confidence))

        return results

    def verify_element_exists(
        self, template_path: str, threshold: float = 0.8, timeout: int = 10
    ) -> bool:
        """
        验证指定元素是否存在于屏幕上

        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值
            timeout: 超时时间（秒）

        Returns:
            True if element exists, False otherwise
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            match_result = self.find_template_in_screenshot(template_path, threshold)
            if match_result:
                x, y, confidence = match_result
                print(f"元素验证成功: 位置({x}, {y}), 置信度={confidence:.3f}")
                return True

            time.sleep(1)  # 等待1秒后重试

        print(f"元素验证失败: 在{timeout}秒内未找到匹配的元素")
        return False

    def click_template_if_found(
        self, template_path: str, threshold: float = 0.8
    ) -> bool:
        """
        如果找到模板图像，则点击它

        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值

        Returns:
            True if clicked, False if not found
        """
        match_result = self.find_template_in_screenshot(template_path, threshold)
        if match_result:
            x, y, confidence = match_result
            self.driver.click(x, y)
            print(f"点击了位置({x}, {y}), 置信度={confidence:.3f}")
            return True
        else:
            print("未找到可点击的元素")
            return False

    def quick_click(
        self, x: int, y: int, times: int = 5, interval: float = 0.05
    ) -> None:
        """
        快速点击指定位置多次

        Args:
            x: 点击的x坐标
            y: 点击的y坐标
            times: 点击次数，默认为5次
            interval: 每次点击之间的间隔（秒），默认为0.05秒（50毫秒）
        """
        import time

        for i in range(times):
            self.driver.click(x, y)
            if i < times - 1:  # 最后一次点击后不需要等待
                time.sleep(interval)
        print(f"快速点击了位置({x}, {y}) {times}次，间隔{interval}秒")

    def quick_click_template(
        self,
        template_path: str,
        threshold: float = 0.8,
        times: int = 5,
        interval: float = 0.05,
    ) -> bool:
        """
        找到模板图像后快速点击多次

        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值
            times: 点击次数，默认为5次
            interval: 每次点击之间的间隔（秒），默认为0.05秒（50毫秒）

        Returns:
            True if clicked, False if not found
        """
        match_result = self.find_template_in_screenshot(template_path, threshold)
        if match_result:
            x, y, confidence = match_result
            self.quick_click(x, y, times, interval)
            print(f"快速点击了位置({x}, {y}) {times}次，置信度={confidence:.3f}")
            return True
        else:
            print("未找到可点击的元素")
            return False

    def _apply_nms(
        self, matches, template_width, template_height, overlap_threshold=0.3
    ):
        """
        应用非最大值抑制来过滤重叠的匹配

        Args:
            matches: 匹配列表 [(x, y, confidence, template_path), ...]
            template_width: 模板宽度
            template_height: 模板高度
            overlap_threshold: 重叠阈值

        Returns:
            过滤后的匹配列表
        """
        if not matches:
            return []

        # 按置信度排序
        matches = sorted(matches, key=lambda x: x[2], reverse=True)

        filtered_matches = []

        for current_match in matches:
            x1, y1, conf, template_path = current_match

            # 检查与已选择的匹配是否重叠
            is_overlapping = False
            for selected_match in filtered_matches:
                x2, y2, _, _ = selected_match

                # 计算重叠区域
                overlap_x1 = max(x1, x2)
                overlap_y1 = max(y1, y2)
                overlap_x2 = min(x1 + template_width, x2 + template_width)
                overlap_y2 = min(y1 + template_height, y2 + template_height)

                # 计算重叠面积
                if overlap_x2 > overlap_x1 and overlap_y2 > overlap_y1:
                    overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
                    template_area = template_width * template_height
                    overlap_ratio = overlap_area / template_area

                    if overlap_ratio > overlap_threshold:
                        is_overlapping = True
                        break

            # 如果不重叠，添加到结果中
            if not is_overlapping:
                filtered_matches.append(current_match)

        return filtered_matches

    def create_marked_screenshot_for_single_template(
        self, template_path: str, threshold: float = 0.8
    ) -> Optional[str]:
        """
        为单个模板创建带匹配区域标记的截图并保存到Allure报告

        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值

        Returns:
            标记后的截图路径，如果失败返回None
        """
        try:
            # 截取当前屏幕
            screenshot_path = self.take_screenshot()
            screenshot = cv2.imread(screenshot_path)

            if screenshot is None:
                print(f"无法读取截图: {screenshot_path}")
                return None

            if not os.path.exists(template_path):
                print(f"模板文件不存在: {template_path}")
                return None

            template = cv2.imread(template_path)
            if template is None:
                print(f"无法读取模板: {template_path}")
                return None

            template_name = os.path.basename(template_path)
            h, w = template.shape[:2]

            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # 找到最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 创建标记的截图
            marked_screenshot = screenshot.copy()

            if max_val >= threshold:
                # 找到匹配，绘制标记
                x, y = max_loc
                center_x = int(x + w // 2)
                center_y = int(y + h // 2)

                # 绘制绿色圆形圈选框
                radius = max(w, h) // 2 + 15
                cv2.circle(
                    marked_screenshot, (center_x, center_y), radius, (0, 255, 0), 4
                )

                # 绘制绿色矩形框
                cv2.rectangle(marked_screenshot, (x, y), (x + w, y + h), (0, 255, 0), 3)

                # 添加"匹配成功"标签
                success_label = "匹配成功"
                label_size = cv2.getTextSize(
                    success_label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
                )[0]
                label_x = center_x - label_size[0] // 2
                label_y = center_y - radius - 10

                # 绘制标签背景
                cv2.rectangle(
                    marked_screenshot,
                    (label_x - 5, label_y - label_size[1] - 5),
                    (label_x + label_size[0] + 5, label_y + 5),
                    (0, 255, 0),
                    -1,
                )
                cv2.putText(
                    marked_screenshot,
                    success_label,
                    (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                # 添加详细信息
                info_label = f"{template_name}: {float(max_val):.3f}"
                info_y = y - 15 if y > 30 else y + h + 25
                cv2.putText(
                    marked_screenshot,
                    info_label,
                    (x, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

                print(
                    f"[{get_current_time_str()}]模板匹配成功: {template_name}, 位置({center_x}, {center_y}), 置信度={float(max_val):.3f}"
                )
            else:
                # 未找到匹配，标记最高置信度位置
                x, y = max_loc
                center_x = int(x + w // 2)
                center_y = int(y + h // 2)

                # 绘制红色圆形圈选框
                radius = max(w, h) // 2 + 15
                cv2.circle(
                    marked_screenshot, (center_x, center_y), radius, (0, 0, 255), 4
                )

                # 绘制红色矩形框
                cv2.rectangle(marked_screenshot, (x, y), (x + w, y + h), (0, 0, 255), 3)

                # 添加"匹配失败"标签
                fail_label = "匹配失败"
                label_size = cv2.getTextSize(
                    fail_label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
                )[0]
                label_x = center_x - label_size[0] // 2
                label_y = center_y - radius - 10

                # 绘制标签背景
                cv2.rectangle(
                    marked_screenshot,
                    (label_x - 5, label_y - label_size[1] - 5),
                    (label_x + label_size[0] + 5, label_y + 5),
                    (0, 0, 255),
                    -1,
                )
                cv2.putText(
                    marked_screenshot,
                    fail_label,
                    (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                # 添加详细信息
                info_label = f"{template_name}: {float(max_val):.3f}"
                info_y = y - 15 if y > 30 else y + h + 25
                cv2.putText(
                    marked_screenshot,
                    info_label,
                    (x, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

                print(
                    f"模板匹配失败: {template_name}, 最高置信度位置({center_x}, {center_y}), 置信度={float(max_val):.3f}"
                )

            # 保存标记后的截图
            import time

            marked_screenshot_path = os.path.join(
                self.screenshots_dir, f"marked_{template_name}_{int(time.time())}.png"
            )
            cv2.imwrite(marked_screenshot_path, marked_screenshot)

            # 附加到Allure报告
            try:
                with open(marked_screenshot_path, "rb") as f:
                    status = "成功" if max_val >= threshold else "失败"
                    allure.attach(
                        f.read(),
                        name=f"🎯 匹配区域标记图 - {template_name} ({status})",
                        attachment_type=allure.attachment_type.PNG,
                    )

                # 添加匹配详情
                details_text = f"模板匹配详细信息:\n"
                details_text += f"模板文件: {template_name}\n"
                details_text += f"匹配位置: ({center_x}, {center_y})\n"
                details_text += f"置信度: {float(max_val):.3f}\n"
                details_text += f"阈值: {threshold}\n"
                details_text += (
                    f"匹配状态: {'成功' if max_val >= threshold else '失败'}\n"
                )
                details_text += f"标记截图路径: {marked_screenshot_path}\n"

                allure.attach(
                    details_text,
                    name=f"📊 {template_name} 匹配详情",
                    attachment_type=allure.attachment_type.TEXT,
                )

                print(f"已将标记截图附加到Allure报告: {marked_screenshot_path}")

            except ImportError:
                print("Allure未安装，跳过报告附加")
            except Exception as e:
                print(f"附加标记截图到Allure报告时出错: {e}")

            return marked_screenshot_path

        except Exception as e:
            print(f"创建标记截图时出错: {e}")
            return None

    def verify_and_mark_matches(
        self, template_paths: List[str], threshold: float = 0.8
    ) -> Tuple[bool, List[dict]]:
        """
        验证模板匹配并返回详细的匹配结果，同时在报告中圈选匹配区域

        Args:
            template_paths: 模板图像路径列表
        Returns:
            (是否找到匹配, 匹配结果列表)
            匹配结果格式: [{'template_name': str, 'center_x': int, 'center_y': int, 'confidence': float, 'bbox': tuple}]
        """
        try:
            # 截取当前屏幕
            screenshot_path = self.take_screenshot()
            screenshot = cv2.imread(screenshot_path)

            if screenshot is None:
                print(f"无法读取截图: {screenshot_path}")
                return False, []

            found_any_match = False
            all_matches = []  # 存储所有模板的匹配结果
            match_results = []  # 存储格式化的匹配结果

            # 对每个模板进行匹配
            for template_path in template_paths:
                if not os.path.exists(template_path):
                    print(f"模板文件不存在: {template_path}")
                    continue

                template = cv2.imread(template_path)
                if template is None:
                    print(f"无法读取模板: {template_path}")
                    continue

                template_name = os.path.basename(template_path)
                h, w = template.shape[:2]

                # 模板匹配
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

                # 扫描整个屏幕区域，找到所有可能的匹配位置
                locations = np.where(result >= threshold)
                template_matches = []

                # 收集所有匹配位置和置信度
                for pt in zip(*locations[::-1]):  # 转换坐标顺序
                    confidence = result[pt[1], pt[0]]
                    template_matches.append((pt[0], pt[1], confidence, template_path))

                if template_matches:
                    # 按置信度排序
                    template_matches.sort(key=lambda x: x[2], reverse=True)

                    # 应用非最大值抑制（NMS）来过滤重叠的匹配
                    filtered_matches = self._apply_nms(
                        template_matches, w, h, overlap_threshold=0.3
                    )

                    if filtered_matches:
                        all_matches.extend(filtered_matches)
                        found_any_match = True

                        print(
                            f"模板 {template_name} 找到 {len(filtered_matches)} 个匹配:"
                        )

                        # 只取最佳匹配添加到结果中
                        best_match = filtered_matches[0]
                        x, y, conf, _ = best_match
                        center_x = x + w // 2
                        center_y = y + h // 2

                        match_results.append(
                            {
                                "template_name": template_name,
                                "center_x": center_x,
                                "center_y": center_y,
                                "confidence": conf,
                                "bbox": (x, y, x + w, y + h),  # 边界框坐标
                            }
                        )

                        for i, (x, y, conf, _) in enumerate(
                            filtered_matches[:3]
                        ):  # 只显示前3个
                            center_x_temp = x + w // 2
                            center_y_temp = y + h // 2
                            print(
                                f"  匹配{i+1}: 位置({center_x_temp}, {center_y_temp}), 置信度={conf:.3f}"
                            )
                else:
                    # 显示最高置信度位置
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    center_x = int(max_loc[0] + w // 2)
                    center_y = int(max_loc[1] + h // 2)
                    print(f"模板 {template_name} 未找到符合阈值的匹配")
                    print(
                        f"  最高置信度位置: ({center_x}, {center_y}), 置信度={float(max_val):.3f}"
                    )

            # 在截图上标记所有匹配位置并保存到报告
            if all_matches:
                # 按置信度排序所有匹配
                all_matches.sort(key=lambda x: x[2], reverse=True)

                # 创建圈选标记的截图
                marked_screenshot = screenshot.copy()

                for i, (x, y, confidence, template_path) in enumerate(all_matches):
                    template = cv2.imread(template_path)
                    h, w = template.shape[:2]
                    template_name = os.path.basename(template_path)

                    # 绘制圆形圈选框（更醒目）
                    center_x = x + w // 2
                    center_y = y + h // 2
                    radius = max(w, h) // 2 + 10

                    # 不同匹配用不同颜色
                    colors = [
                        (0, 255, 0),
                        (0, 255, 255),
                        (255, 0, 255),
                        (255, 165, 0),
                        (0, 0, 255),
                    ]
                    color = colors[i % len(colors)]

                    # 绘制圆形圈选
                    cv2.circle(
                        marked_screenshot, (center_x, center_y), radius, color, 4
                    )

                    # 绘制矩形框
                    cv2.rectangle(marked_screenshot, (x, y), (x + w, y + h), color, 2)

                    # 添加序号标签
                    label_bg_size = cv2.getTextSize(
                        f"{i+1}", cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
                    )[0]
                    cv2.rectangle(
                        marked_screenshot,
                        (
                            center_x - label_bg_size[0] // 2 - 5,
                            center_y - label_bg_size[1] // 2 - 5,
                        ),
                        (
                            center_x + label_bg_size[0] // 2 + 5,
                            center_y + label_bg_size[1] // 2 + 5,
                        ),
                        color,
                        -1,
                    )
                    cv2.putText(
                        marked_screenshot,
                        f"{i+1}",
                        (
                            center_x - label_bg_size[0] // 2,
                            center_y + label_bg_size[1] // 2,
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )

                    # 添加详细信息标签
                    info_label = f"{template_name}: {confidence:.3f}"
                    label_y = y - 15 if y > 30 else y + h + 25
                    cv2.putText(
                        marked_screenshot,
                        info_label,
                        (x, label_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2,
                    )

                # 保存圈选标记后的截图
                import time

                marked_screenshot_path = os.path.join(
                    self.screenshots_dir, f"marked_matches_{int(time.time())}.png"
                )
                cv2.imwrite(marked_screenshot_path, marked_screenshot)

                # 附加到Allure报告
                try:
                    import allure

                    with open(marked_screenshot_path, "rb") as f:
                        allure.attach(
                            f.read(),
                            name=f"匹配区域圈选图 - 找到{len(all_matches)}个匹配",
                            attachment_type=allure.attachment_type.PNG,
                        )

                    # 创建匹配详情表格
                    details_text = "匹配区域详细信息:\n" + "=" * 50 + "\n"
                    for i, result in enumerate(match_results):
                        details_text += f"匹配区域 {i+1}:\n"
                        details_text += f"  模板文件: {result['template_name']}\n"
                        details_text += f"  中心位置: ({result['center_x']}, {result['center_y']})\n"
                        details_text += f"  置信度: {result['confidence']:.3f}\n"
                        details_text += f"  边界框: {result['bbox']}\n"
                        details_text += "-" * 30 + "\n"

                    allure.attach(
                        details_text,
                        name="匹配区域详细信息",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                except ImportError:
                    print("Allure未安装，跳过报告附加")

            return found_any_match, match_results

        except Exception as e:
            print(f"验证和标记匹配时出错: {e}")
            return False, []


def create_image_matcher(driver: u2.Device) -> ImageMatcher:
    """创建图像匹配器实例"""
    return ImageMatcher(driver)

# -*- coding: utf-8 -*-
"""
列表滑动自动化工具函数
提供多种列表滑动方式和滑动查找元素的功能
"""

import time
import uiautomator2 as u2
from src.utils.screenshot_utils import attach_screenshot_to_allure
from src.utils.time_utils import get_current_time_str


def scroll_up(driver, steps=10, percent=0.6, duration=0.5):
    """
    向上滑动页面
    
    Args:
        driver: uiautomator2驱动实例
        steps: 滑动步数，值越大滑动越精确
        percent: 滑动距离占屏幕高度的比例，默认0.6（滑动屏幕高度的60%）
        duration: 滑动持续时间（秒），默认0.5秒
    
    Returns:
        bool: 滑动是否成功
    """
    try:
        # 获取屏幕尺寸
        window_size = driver.window_size()
        width, height = window_size
        
        # 计算起始和结束坐标
        start_x = width / 2  # 屏幕中心X坐标
        start_y = height * 0.7  # 起始Y坐标（屏幕下部）
        end_y = height * 0.1  # 结束Y坐标（屏幕上部）
        
        # 执行滑动操作
        driver.swipe(start_x, start_y, start_x, end_y, steps=steps, duration=duration)
        print(f"[{get_current_time_str()}] 向上滑动页面成功")
        return True
    except Exception as e:
        print(f"[{get_current_time_str()}] 向上滑动页面失败: {e}")
        return False


def scroll_down(driver, steps=10, percent=0.6, duration=0.5):
    """
    向下滑动页面
    
    Args:
        driver: uiautomator2驱动实例
        steps: 滑动步数，值越大滑动越精确
        percent: 滑动距离占屏幕高度的比例，默认0.6（滑动屏幕高度的60%）
        duration: 滑动持续时间（秒），默认0.5秒
    
    Returns:
        bool: 滑动是否成功
    """
    try:
        # 获取屏幕尺寸
        window_size = driver.window_size()
        width, height = window_size
        
        # 计算起始和结束坐标
        start_x = width / 2  # 屏幕中心X坐标
        start_y = height * 0.3  # 起始Y坐标（屏幕上部）
        end_y = height * 0.9  # 结束Y坐标（屏幕下部）
        
        # 执行滑动操作
        driver.swipe(start_x, start_y, start_x, end_y, steps=steps, duration=duration)
        print(f"[{get_current_time_str()}] 向下滑动页面成功")
        return True
    except Exception as e:
        print(f"[{get_current_time_str()}] 向下滑动页面失败: {e}")
        return False


def scroll_to_element(driver, element_selector, max_swipes=10, direction='down', 
                     screenshot=True, allure_description=""):
    """
    滑动直到找到指定元素
    
    Args:
        driver: uiautomator2驱动实例
        element_selector: 元素选择器，例如：{"text": "确定"} 或 {"resourceId": "com.example:id/button"}
        max_swipes: 最大滑动次数，防止无限循环
        direction: 滑动方向，'up'或'down'
        screenshot: 是否在每次滑动后截图
        allure_description: Allure报告中的描述
    
    Returns:
        tuple: (是否找到元素, 元素对象或None)
    """
    swipe_count = 0
    
    while swipe_count < max_swipes:
        # 尝试查找元素
        element = None
        if "text" in element_selector:
            element = driver(text=element_selector["text"])
        elif "resourceId" in element_selector:
            element = driver(resourceId=element_selector["resourceId"])
        elif "description" in element_selector:
            element = driver(description=element_selector["description"])
        
        # 检查元素是否存在且可见
        if element and element.exists and element.visible:
            print(f"[{get_current_time_str()}] 找到目标元素: {element_selector}")
            # 如果需要截图，捕获找到元素的屏幕
            if screenshot:
                attach_screenshot_to_allure(
                    driver, 
                    f"element_found_{swipe_count}", 
                    f"[{get_current_time_str()}] 第{swipe_count}次滑动后找到元素: {element_selector}"
                )
            return True, element
        
        # 执行滑动操作
        if direction == 'down':
            scroll_down(driver)
        else:
            scroll_up(driver)
        
        swipe_count += 1
        print(f"[{get_current_time_str()}] 第{swipe_count}次{direction}滑动")
        
        # 如果需要截图，捕获滑动后的屏幕
        if screenshot:
            attach_screenshot_to_allure(
                driver, 
                f"after_swipe_{swipe_count}", 
                f"[{get_current_time_str()}] 第{swipe_count}次{direction}滑动后"
            )
        
        # 等待滑动动画完成
        time.sleep(1)
    
    # 达到最大滑动次数仍未找到元素
    print(f"[{get_current_time_str()}] 达到最大滑动次数{max_swipes}，未找到元素: {element_selector}")
    if screenshot:
        attach_screenshot_to_allure(
            driver, 
            "element_not_found", 
            f"[{get_current_time_str()}] 达到最大滑动次数，未找到元素: {element_selector}"
        )
    return False, None


def scroll_to_bottom(driver, max_swipes=10, detect_end=True):
    """
    滑动到底部
    
    Args:
        driver: uiautomator2驱动实例
        max_swipes: 最大滑动次数
        detect_end: 是否检测滑动到底部（通过比较前后页面内容）
    
    Returns:
        int: 实际滑动次数
    """
    swipe_count = 0
    
    if detect_end:
        # 获取初始页面内容作为参考
        previous_content = driver.dump_hierarchy()
    
    while swipe_count < max_swipes:
        # 执行向下滑动
        scroll_down(driver)
        swipe_count += 1
        time.sleep(1)
        
        if detect_end:
            # 获取当前页面内容
            current_content = driver.dump_hierarchy()
            
            # 比较前后页面内容，如果相似则认为已到底部
            if current_content == previous_content:
                print(f"[{get_current_time_str()}] 已滑动到底部，共滑动{swipe_count}次")
                break
            
            previous_content = current_content
    
    print(f"[{get_current_time_str()}] 滑动到底部完成，共滑动{swipe_count}次")
    return swipe_count


def scroll_to_top(driver, max_swipes=10, detect_end=True):
    """
    滑动到顶部
    
    Args:
        driver: uiautomator2驱动实例
        max_swipes: 最大滑动次数
        detect_end: 是否检测滑动到顶部
    
    Returns:
        int: 实际滑动次数
    """
    swipe_count = 0
    
    if detect_end:
        # 获取初始页面内容作为参考
        previous_content = driver.dump_hierarchy()
    
    while swipe_count < max_swipes:
        # 执行向上滑动
        scroll_up(driver)
        swipe_count += 1
        time.sleep(1)
        
        if detect_end:
            # 获取当前页面内容
            current_content = driver.dump_hierarchy()
            
            # 比较前后页面内容，如果相似则认为已到顶部
            if current_content == previous_content:
                print(f"[{get_current_time_str()}] 已滑动到顶部，共滑动{swipe_count}次")
                break
            
            previous_content = current_content
    
    print(f"[{get_current_time_str()}] 滑动到顶部完成，共滑动{swipe_count}次")
    return swipe_count


def scroll_horizontally(driver, direction='right', steps=10, percent=0.6, duration=0.5):
    """
    水平滑动页面
    
    Args:
        driver: uiautomator2驱动实例
        direction: 滑动方向，'left'或'right'
        steps: 滑动步数
        percent: 滑动距离占屏幕宽度的比例
        duration: 滑动持续时间（秒）
    
    Returns:
        bool: 滑动是否成功
    """
    try:
        # 获取屏幕尺寸
        window_size = driver.window_size()
        width, height = window_size
        
        # 计算起始和结束坐标
        start_y = height / 2  # 屏幕中心Y坐标
        
        if direction == 'right':
            # 从左向右滑动
            start_x = width * 0.2
            end_x = width * 0.8
        else:
            # 从右向左滑动
            start_x = width * 0.8
            end_x = width * 0.2
        
        # 执行滑动操作
        driver.swipe(start_x, start_y, end_x, start_y, steps=steps, duration=duration)
        print(f"[{get_current_time_str()}] 水平{direction}滑动页面成功")
        return True
    except Exception as e:
        print(f"[{get_current_time_str()}] 水平{direction}滑动页面失败: {e}")
        return False


def scroll_until_text_appears(driver, text, max_swipes=10, direction='down'):
    """
    滑动直到文本出现
    
    Args:
        driver: uiautomator2驱动实例
        text: 要查找的文本
        max_swipes: 最大滑动次数
        direction: 滑动方向
    
    Returns:
        bool: 是否找到文本
    """
    return scroll_to_element(driver, {"text": text}, max_swipes, direction)[0]


def scroll_until_id_appears(driver, resource_id, max_swipes=10, direction='down'):
    """
    滑动直到指定resourceId的元素出现
    
    Args:
        driver: uiautomator2驱动实例
        resource_id: 要查找的元素resourceId
        max_swipes: 最大滑动次数
        direction: 滑动方向
    
    Returns:
        bool: 是否找到元素
    """
    return scroll_to_element(driver, {"resourceId": resource_id}, max_swipes, direction)[0]


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用模板生成工具
支持用户输入坐标、尺寸和模板名称来生成通用图像模板
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uiautomator2 as u2
from src.utils.image_utils import create_image_matcher
import cv2
import numpy as np

def get_user_input():
    """获取用户输入的参数"""
    print("=" * 50)
    print("📱 通用模板生成工具")
    print("=" * 50)
    
    try:
        # 获取坐标
        print("\n📍 请输入模板区域的坐标:")
        x = int(input("X坐标: "))
        y = int(input("Y坐标: "))
        
        # 获取尺寸
        print("\n📏 请输入模板区域的尺寸:")
        width = int(input("宽度 (默认60): ") or "60")
        height = int(input("高度 (默认60): ") or "60")
        
        # 获取模板名称
        print("\n📝 请输入模板名称:")
        template_name = input("模板名称: ").strip()
        
        if not template_name:
            print("❌ 模板名称不能为空!")
            return None
            
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'template_name': template_name
        }
        
    except ValueError as e:
        print(f"❌ 输入格式错误: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        return None

def generate_common_template_from_coordinates(params):
    """根据参数生成通用模板"""
    try:
        # 连接设备
        print("\n🔗 正在连接设备...")
        driver = u2.connect()
        print("✅ 设备连接成功!")
        print(f"📱 设备信息: {driver.info.get('brand', 'Unknown')} {driver.info.get('model', 'Unknown')}")

        # 创建图像匹配器
        image_matcher = create_image_matcher(driver)

        print(f"\n📊 模板参数:")
        print(f"   坐标: ({params['x']}, {params['y']})")
        print(f"   尺寸: {params['width']} x {params['height']}")
        print(f"   名称: {params['template_name']}")

        # 截取当前屏幕
        print("\n📸 正在截取屏幕...")
        screenshot_path = image_matcher.take_screenshot()
        screenshot = cv2.imread(screenshot_path)
        
        if screenshot is None:
            print("❌ 无法读取截图文件")
            return None

        height_img, width_img = screenshot.shape[:2]
        print(f"📏 截图尺寸: {width_img}x{height_img}")

        # 检查位置是否在截图范围内
        if params['x'] >= width_img or params['y'] >= height_img:
            print(f"❌ 指定位置({params['x']}, {params['y']})超出截图范围({width_img}x{height_img})")
            return None

        # 计算提取区域
        start_x = max(0, params['x'] - params['width'] // 2)
        end_x = min(width_img, start_x + params['width'])
        start_y = max(0, params['y'] - params['height'] // 2)
        end_y = min(height_img, start_y + params['height'])

        # 调整起始位置以确保模板大小一致
        if end_x - start_x < params['width']:
            start_x = max(0, end_x - params['width'])
        if end_y - start_y < params['height']:
            start_y = max(0, end_y - params['height'])

        print(f"📐 提取区域: ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
        print(f"📏 实际模板尺寸: {end_x - start_x}x{end_y - start_y}")

        # 提取模板区域
        template_region = screenshot[start_y:end_y, start_x:end_x]

        # 创建通用模板目录
        common_template_dir = 'src/resources/templates/common'
        os.makedirs(common_template_dir, exist_ok=True)

        # 保存通用模板
        common_template_path = os.path.join(common_template_dir, f'{params["template_name"]}_common.png')
        cv2.imwrite(common_template_path, template_region)
        print(f"✅ 通用模板已保存到: {common_template_path}")

        # 创建一个标记了提取区域的截图用于验证
        marked_screenshot = screenshot.copy()
        cv2.rectangle(marked_screenshot, (start_x, start_y), (end_x, end_y), (0, 255, 0), 3)
        cv2.putText(marked_screenshot, f"Common Template: ({start_x}, {start_y})", 
        (start_x, start_y - 10), 
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        verification_path = f'{params["template_name"]}_common_extraction.png'
        cv2.imwrite(verification_path, marked_screenshot)
        print(f"📋 提取验证图已保存到: {verification_path}")

        # 测试新模板的匹配效果
        print("\n🔍 测试新模板的匹配效果...")
        result = cv2.matchTemplate(screenshot, template_region, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"🎯 最佳匹配位置: {max_loc}")
        print(f"📊 最佳匹配置信度: {max_val:.3f}")

        # 检查是否在预期位置附近
        distance = np.sqrt((max_loc[0] - params['x'])**2 + (max_loc[1] - params['y'])**2)
        print(f"📏 与预期位置的距离: {distance:.1f} 像素")

        if distance < 50 and max_val > 0.8:
            print("✅ 新模板匹配效果良好!")
        elif distance < 100:
            print("⚠️ 新模板匹配位置接近预期，但可能需要微调")
        else:
            print("❌ 新模板匹配位置偏差较大，可能需要重新选择区域")

        print(f"\n🎉 现在可以在测试用例中使用 '{params['template_name']}_common' 模板了!")
        return common_template_path

    except Exception as e:
        print(f"\n❌ 生成通用模板时发生错误: {e}")
        return None

def main():
    """主函数"""
    while True:
        # 获取用户输入
        params = get_user_input()
        if params is None:
            break
            
        # 生成通用模板
        result = generate_common_template_from_coordinates(params)
        
        # 询问是否继续
        print("\n" + "=" * 50)
        continue_choice = input("是否继续生成其他模板? (y/n): ").strip().lower()
        if continue_choice not in ['y', 'yes', '是']:
            break
            
    print("\n👋 感谢使用模板生成工具!")

if __name__ == "__main__":
    main()
#!/bin/bash

# 清理旧的测试文件和数据
echo "清理测试环境..."

# 清理Allure结果和报告目录
if [ -d "allure-results" ]; then
  rm -rf allure-results/*
fi
if [ -d "allure-report" ]; then
  rm -rf allure-report/*
fi

# 清理测试截图目录
if [ -d "src/resources/screenshots" ]; then
  rm -rf src/resources/screenshots/*
fi

# 清理pytest缓存目录
if [ -d ".pytest_cache" ]; then
  rm -rf .pytest_cache/*
fi

# 清理__pycache__目录
find . -name "__pycache__" -type d | while read -r dir; do
  rm -rf "$dir"/* 2>/dev/null
done

# 激活虚拟环境
source venv/bin/activate

# 清理可能的跨项目环境污染并锁定当前环境
unset PYTHONPATH
export PYTHONNOUSERSITE=1

# 检查是否有连接的Android设备
echo "检查Android设备连接..."
adb devices
if [ $? -ne 0 ]; then
  echo "警告: 未找到adb命令，请安装Android Platform Tools"
fi

# 选择第一个已连接的设备作为默认设备
ANDROID_SERIAL_DEFAULT=$(adb devices | awk '/\tdevice$/{print $1; exit}')
if [ -n "$ANDROID_SERIAL_DEFAULT" ]; then
  export ANDROID_SERIAL="$ANDROID_SERIAL_DEFAULT"
  echo "使用设备: $ANDROID_SERIAL"
else
  echo "未检测到可用设备"
fi

# 初始化设备上的 uiautomator2 服务
echo "初始化uiautomator2服务..."
venv/bin/python3 -m uiautomator2 init >/dev/null 2>&1 || true

# 运行测试脚本
echo "运行测试..."
venv/bin/python3 -m pytest src/tests/app_email/app_email_test.py --alluredir=allure-results

# 显示测试结果信息
echo "测试完成，结果保存在allure-results目录"

# 检查allure命令是否可用并自动打开报告
if command -v allure &> /dev/null; then
  echo "启动Allure报告服务..."
  allure serve allure-results &
  sleep 3
else
  echo "提示: 安装allure后可查看详细报告: brew install allure"
fi

# # 询问用户是否启动 uiauto.dev
# echo "----------------------------------------"
# echo "是否启动uiauto.dev工具查看UI元素？(y/n): "
# read start_uiauto
# if [ "$start_uiauto" = "y" ] || [ "$start_uiauto" = "Y" ]; then
#   echo "启动uiauto.dev..."
#   # 检查并安装uiautodev（如果未安装）
#   if ! python -c "import uiautodev" 2>/dev/null; then
#     echo "安装uiautodev..."
#     pip install "uiautodev>=0.2.0" >/dev/null 2>&1
#   fi
  
#   if command -v uiauto.dev &> /dev/null; then
#     uiauto.dev &
#   else
#     python -m uiautodev &
#   fi
#   sleep 2
#   echo "uiauto.dev已启动"
# else
#   echo "已跳过uiauto.dev启动"
# fi


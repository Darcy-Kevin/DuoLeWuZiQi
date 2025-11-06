#!/bin/bash

# 单独运行一个测试用例的脚本
# 使用方法：
#   ./run_single_test.sh 文件路径::类名::方法名
#   例如: ./run_single_test.sh src/tests/app_launch/app_launch_test.py::TestDuoleWuZiQiApp::test_launch_app

# 检查参数
if [ -z "$1" ]; then
    echo "使用方法: $0 <测试用例路径或pytest参数>"
    echo ""
    echo "示例:"
    echo "  $0 src/tests/app_launch/app_launch_test.py::TestDuoleWuZiQiApp::test_launch_app"
    echo "  $0 src/tests/app_launch/app_launch_test.py::TestDuoleWuZiQiApp"
    echo "  $0 src/tests/app_launch/app_launch_test.py"
    echo "  $0 src/tests/daily_signin/app_signin_test.py::TestDailySignIn::test_daily_signin"
    echo "  $0 -k test_launch_app"
    echo "  $0 -k 'test_launch_app or test_daily_signin'"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 清理Allure结果目录
if [ -d "allure-results" ]; then
  rm -rf allure-results/*
fi

# 初始化设备上的 uiautomator2 服务
echo "初始化uiautomator2服务..."
venv/bin/python3 -m uiautomator2 init >/dev/null 2>&1 || true

# 运行测试（将所有参数传递给 pytest）
echo "运行测试: $@"
venv/bin/python3 -m pytest "$@" --alluredir=allure-results -v

# 显示测试结果
echo ""
echo "测试完成，结果保存在allure-results目录"

# 如果安装了allure，自动打开报告
if command -v allure &> /dev/null; then
  echo "启动Allure报告服务..."
  allure serve allure-results &
  sleep 3
else
  echo "提示: 安装allure后可查看详细报告: brew install allure"
fi


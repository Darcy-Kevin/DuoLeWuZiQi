#!/bin/bash

# 切换到项目根目录（脚本位于 scripts/run/ 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# 单独运行一个测试用例的脚本
# 使用方法：
#   ./scripts/run/run_single_test.sh 文件路径::类名::方法名
#   例如: ./scripts/run/run_single_test.sh src/tests/app_launch/app_launch_test.py::TestDuoleWuZiQiApp::test_launch_app

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

# 如果安装了allure，生成静态报告
if command -v allure &> /dev/null; then
  echo "生成Allure静态报告..."
  allure generate allure-results -o allure-report --clean
  
  if [ $? -eq 0 ]; then
    echo "✅ Allure报告已生成到 allure-report 目录"
    echo "📊 报告位置: $(pwd)/allure-report/index.html"
    
    # 询问用户是否自动打开报告
    echo "----------------------------------------"
    echo "是否自动在浏览器中打开报告？(y/n，默认y): "
    read -t 5 open_report || open_report="y"
    
    if [ "$open_report" = "y" ] || [ "$open_report" = "Y" ] || [ -z "$open_report" ]; then
      echo "正在打开报告..."
      
      # 先停止所有旧的报告服务器进程
      echo "检查并停止旧的报告服务器..."
      
      # 1. 停止保存的PID（如果存在）
      if [ -f ".allure_server.pid" ]; then
        OLD_PID=$(cat .allure_server.pid)
        if kill -0 $OLD_PID 2>/dev/null; then
          echo "  停止保存的服务器进程 (PID: $OLD_PID)..."
          kill $OLD_PID 2>/dev/null
        fi
        rm -f .allure_server.pid .allure_server.port
      fi
      
      # 2. 停止所有占用8000-8010端口的Python HTTP服务器
      STOPPED_COUNT=0
      for port in {8000..8010}; do
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$PID" ]; then
          # 检查是否是Python HTTP服务器
          if ps -p $PID -o command= 2>/dev/null | grep -q "python3 -m http.server"; then
            echo "  停止占用端口 $port 的服务器进程 (PID: $PID)..."
            kill $PID 2>/dev/null
            STOPPED_COUNT=$((STOPPED_COUNT + 1))
          fi
        fi
      done
      
      # 3. 等待进程完全停止
      if [ $STOPPED_COUNT -gt 0 ]; then
        echo "  等待进程停止..."
        sleep 2
      fi
      
      # 使用固定端口8000（现在应该可用了）
      REPORT_PORT=8000
      
      # 验证端口是否可用
      if lsof -Pi :$REPORT_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $REPORT_PORT 仍被占用，尝试直接打开文件..."
        REPORT_DIR=$(cd allure-report && pwd)
        open "$REPORT_DIR/index.html"
        echo "✅ 报告已在浏览器中打开（直接打开文件）"
        exit 0
      fi
      
      echo "✅ 使用端口: $REPORT_PORT"
      
      # 获取绝对路径
      REPORT_DIR=$(cd allure-report && pwd)
      
      # 在后台启动 HTTP 服务器（使用绝对路径确保在正确目录）
      (cd "$REPORT_DIR" && python3 -m http.server $REPORT_PORT > /dev/null 2>&1) &
      SERVER_PID=$!
      
      # 等待服务器启动
      sleep 2
      
      # 检查服务器是否成功启动
      if kill -0 $SERVER_PID 2>/dev/null; then
        # 验证服务器是否真的在监听端口
        if lsof -Pi :$REPORT_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
          # 保存 PID 到文件，方便后续管理
          echo $SERVER_PID > .allure_server.pid
          echo $REPORT_PORT > .allure_server.port
          
          open "http://localhost:$REPORT_PORT/index.html"
          echo "✅ 报告已在浏览器中打开 (http://localhost:$REPORT_PORT/index.html)"
          echo "💡 服务器进程 PID: $SERVER_PID"
          echo "   服务器目录: $REPORT_DIR"
          echo "   停止服务器方式:"
          echo "   1. ./scripts/report/stop_report_server.sh"
          echo "   2. kill $SERVER_PID"
          echo "   3. pkill -f 'python3 -m http.server $REPORT_PORT'"
        else
          echo "⚠️  服务器进程已启动但端口未监听，尝试直接打开文件..."
          kill $SERVER_PID 2>/dev/null
          open "$REPORT_DIR/index.html"
          echo "✅ 报告已在浏览器中打开（直接打开文件）"
        fi
      else
        # 如果服务器启动失败，直接打开 HTML 文件
        open "$REPORT_DIR/index.html"
        echo "✅ 报告已在浏览器中打开（直接打开文件）"
      fi
    else
      echo "💡 提示: 可以手动打开报告:"
      echo "   方式1: open allure-report/index.html (直接打开，可能功能受限)"
      echo "   方式2: cd allure-report && python3 -m http.server 8000 (启动本地服务器)"
      echo "   方式3: allure open allure-report (使用 Allure 服务器)"
    fi
  else
    echo "❌ 报告生成失败"
  fi
else
  echo "⚠️  提示: 安装allure后可查看详细报告: brew install allure"
  echo "   报告数据已保存在 allure-results 目录"
fi


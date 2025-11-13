#!/bin/bash

# 切换到项目根目录（脚本位于 scripts/report/ 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# 停止 Allure 报告服务器的辅助脚本

echo "正在查找报告服务器进程..."

# 首先尝试从保存的 PID 文件读取
if [ -f ".allure_server.pid" ]; then
  SAVED_PID=$(cat .allure_server.pid)
  if kill -0 $SAVED_PID 2>/dev/null; then
    echo "找到保存的服务器进程 PID: $SAVED_PID"
    kill $SAVED_PID 2>/dev/null && echo "✅ 已停止进程 $SAVED_PID" || echo "❌ 无法停止进程 $SAVED_PID"
    rm -f .allure_server.pid .allure_server.port
    exit 0
  else
    echo "保存的 PID 已失效，清理文件..."
    rm -f .allure_server.pid .allure_server.port
  fi
fi

# 查找 Python HTTP 服务器进程（用于 Allure 报告，包括8000-8010端口）
PIDS=$(ps aux | grep -E 'python3 -m http.server [0-9]+' | grep -v grep | awk '{print $2}')

# 也查找占用8000端口的进程（可能是之前的报告服务器）
PORT_8000_PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$PORT_8000_PID" ]; then
  PIDS="$PIDS $PORT_8000_PID"
fi

if [ -z "$PIDS" ]; then
  echo "❌ 未找到运行中的报告服务器"
  exit 0
fi

echo "找到以下报告服务器进程:"
if [ -n "$PIDS" ]; then
  for PID in $PIDS; do
    ps -p $PID -o pid,command 2>/dev/null
  done
else
  echo "（无）"
fi

echo ""
echo "是否停止这些进程？(y/n，默认y): "
read -t 5 confirm || confirm="y"

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ -z "$confirm" ]; then
  for PID in $PIDS; do
    kill $PID 2>/dev/null && echo "✅ 已停止进程 $PID" || echo "❌ 无法停止进程 $PID"
  done
  rm -f .allure_server.pid .allure_server.port
  echo "✅ 所有报告服务器已停止"
else
  echo "已取消操作"
fi


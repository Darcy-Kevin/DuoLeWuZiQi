#!/bin/bash

# 切换到项目根目录（脚本位于 scripts/report/ 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# 清理所有旧的 Allure 报告服务器进程

echo "正在清理所有报告服务器进程..."

STOPPED_COUNT=0

# 1. 停止保存的PID（如果存在）
if [ -f ".allure_server.pid" ]; then
  OLD_PID=$(cat .allure_server.pid)
  if kill -0 $OLD_PID 2>/dev/null; then
    echo "停止保存的服务器进程 (PID: $OLD_PID)..."
    kill $OLD_PID 2>/dev/null && STOPPED_COUNT=$((STOPPED_COUNT + 1))
  fi
  rm -f .allure_server.pid .allure_server.port
fi

# 2. 停止所有占用8000-8010端口的Python HTTP服务器
for port in {8000..8010}; do
  PID=$(lsof -ti:$port 2>/dev/null)
  if [ -n "$PID" ]; then
    # 检查是否是Python HTTP服务器
    if ps -p $PID -o command= 2>/dev/null | grep -q "python3 -m http.server"; then
      echo "停止占用端口 $port 的服务器进程 (PID: $PID)..."
      kill $PID 2>/dev/null && STOPPED_COUNT=$((STOPPED_COUNT + 1))
    fi
  fi
done

# 3. 等待进程完全停止
if [ $STOPPED_COUNT -gt 0 ]; then
  echo "等待进程停止..."
  sleep 2
  echo "✅ 已停止 $STOPPED_COUNT 个报告服务器进程"
else
  echo "✅ 未找到运行中的报告服务器"
fi


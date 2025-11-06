#!/usr/bin/env bash
set -euo pipefail

# 项目环境设置脚本（稳健版）
# 显式使用虚拟环境中的 python/pip，避免激活失败导致的 pip 未找到问题

echo "🚀 开始设置 DuoLe_WuZiQi_UI 项目环境..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"

# 检查 Python 可用性
echo "📋 检查Python版本..."
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "❌ 未找到 Python，请安装 Python 3.9 或更高版本"
  exit 1
fi
"${PYTHON_BIN}" --version || true

# 如 venv 目录存在但缺失 python，可视为损坏，先清理
echo "🔧 准备/创建虚拟环境..."
if [[ -d "${VENV_DIR}" ]] && [[ ! -x "${VENV_DIR}/bin/python" ]] && [[ ! -x "${VENV_DIR}/bin/python3" ]]; then
  echo "♻️ 检测到损坏的虚拟环境，正在重新创建..."
  rm -rf "${VENV_DIR}"
fi

# 创建虚拟环境（如不存在）
if [[ ! -d "${VENV_DIR}" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}" || {
    echo "❌ 创建虚拟环境失败，请确认 Python 版本支持 venv"
    exit 1
  }
  echo "✅ 虚拟环境创建成功"
else
  echo "ℹ️ 虚拟环境已存在"
fi

# 选择 venv 中的 python
if [[ -x "${VENV_DIR}/bin/python3" ]]; then
  VENV_PY="${VENV_DIR}/bin/python3"
elif [[ -x "${VENV_DIR}/bin/python" ]]; then
  VENV_PY="${VENV_DIR}/bin/python"
else
  echo "❌ 虚拟环境中未找到 python 可执行文件"
  exit 1
fi
VENV_PIP="${VENV_DIR}/bin/pip"

# 确保虚拟环境内 pip 可用
if [[ ! -x "${VENV_PIP}" ]]; then
  echo "⬆️ 初始化/升级pip..."
  "${VENV_PY}" -m ensurepip --upgrade || true
fi

echo "⬆️ 升级pip..."
"${VENV_PY}" -m pip install --upgrade pip

# 升级基础构建工具（可选但推荐）
echo "🔧 升级构建工具(setuptools/wheel)..."
"${VENV_PIP}" install --upgrade setuptools wheel

# 安装项目依赖
if [[ -f "${REQUIREMENTS_FILE}" ]]; then
  echo "📦 安装项目依赖..."
  "${VENV_PIP}" install -r "${REQUIREMENTS_FILE}"
else
  echo "ℹ️ 未找到 requirements.txt，跳过依赖安装"
fi

# 安装 Allure CLI（用于生成测试报告）
echo "🧪 检查/安装 Allure CLI..."
if command -v allure &> /dev/null; then
  echo "✅ Allure CLI 已安装"
  allure --version || true
else
  echo "ℹ️ 未检测到 Allure CLI，尝试自动安装..."
  if command -v brew &> /dev/null; then
    echo "🍺 使用 Homebrew 安装 Allure CLI..."
    if brew install allure; then
      echo "✅ Allure CLI 安装成功"
    else
      echo "⚠️ Homebrew 安装失败，尝试使用 npm 安装"
      if command -v npm &> /dev/null; then
        echo "⬇️ 使用 npm 全局安装 allure-commandline..."
        if npm install -g allure-commandline; then
          echo "✅ Allure CLI 安装成功"
        else
          echo "❌ 无法自动安装 Allure CLI。请手动安装：brew install allure 或 npm i -g allure-commandline"
        fi
      else
        echo "⚠️ 未找到 npm，请手动安装：brew install allure 或参考官方文档 https://docs.qameta.io/allure/"
      fi
    fi
  elif command -v npm &> /dev/null; then
    echo "⬇️ 使用 npm 全局安装 allure-commandline..."
    if npm install -g allure-commandline; then
      echo "✅ Allure CLI 安装成功"
    else
      echo "❌ npm 安装 Allure 失败，请手动安装或确保 npm 可用"
    fi
  else
    echo "⚠️ 未找到 Homebrew 或 npm，无法自动安装 Allure CLI。请手动安装：macOS 推荐 'brew install allure'"
  fi
fi

# 设置脚本执行权限
echo "🔐 设置脚本执行权限..."
chmod +x "${PROJECT_ROOT}/run_tests.sh" || true
chmod +x "${PROJECT_ROOT}/setup.sh" || true

# 检查ADB工具
echo "📱 检查ADB工具..."
if command -v adb &> /dev/null; then
    echo "✅ ADB工具已安装"
    adb version || true
else
    echo "⚠️ 未找到ADB工具，请安装Android Platform Tools"
    echo "   macOS: brew install android-platform-tools"
    echo "   Ubuntu: sudo apt-get install android-tools-adb"
    echo "   Windows: 下载Android SDK Platform Tools"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p "${PROJECT_ROOT}/src/resources/screenshots"
mkdir -p "${PROJECT_ROOT}/src/resources/templates/common"
mkdir -p "${PROJECT_ROOT}/src/resources/templates/mi"
mkdir -p "${PROJECT_ROOT}/allure-results"
mkdir -p "${PROJECT_ROOT}/allure-report"

echo ""
echo "🎉 项目环境设置完成！"
echo ""
echo "📋 使用说明："
echo "   1. 连接Android设备并启用USB调试"
echo "   2. 激活虚拟环境: source venv/bin/activate"
echo "   3. 运行测试: ./run_tests.sh"
echo "   4. 查看报告: allure serve allure-results"
echo ""
echo "🔧 如果遇到权限问题，请运行："
echo "   chmod +x *.sh"
echo ""


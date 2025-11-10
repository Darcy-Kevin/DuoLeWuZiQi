# 多乐五子棋应用 UI 自动化测试项目

## 项目简介
本仓库提供多乐五子棋（包名 `com.duole.wuziqihd`）的移动端 UI 自动化测试脚本，基于 `uiautomator2`、`pytest` 与 Allure 报告体系构建。测试用例覆盖游戏启动、邮件红点、每日签到等关键业务流程，并结合图像识别能力验证界面元素，适用于 Android 设备的回归测试与冒烟检查。

## 功能亮点
- **设备驱动自动管理**：通过 `uiautomator2` 快速连接真机或模拟器，脚本自动初始化服务。
- **多场景图像识别**：利用 OpenCV 模板匹配定位按钮、红点、标题等视觉元素，支持自定义模板生成工具。
- **API + UI 联动验证**：在邮件红点用例中结合接口造数与界面校验，确保端到端逻辑闭环。
- **Allure 报告集成**：测试执行后自动产出结构化报告，附带截图、标记图及调试信息。
- **脚本化流程**：提供一键环境配置、批量/单例运行、截图清理等辅助脚本，降低上手门槛。

## 目录结构
```
DuoLeWuZiQi/
├── src/
│   ├── config/                     # 坐标与包名配置（按模块封装）
│   ├── resources/
│   │   ├── screenshots/            # 测试运行时生成的截图（自动创建）
│   │   └── templates/              # 图像模板资源（common/mi 等子目录）
│   ├── tests/
│   │   ├── app_launch/             # 启动冒烟用例
│   │   ├── app_email/              # 邮件红点/退场用例
│   │   └── app_signin/             # 每日签到用例
│   └── utils/                      # 截图、时间、滑动、图像匹配等工具库
├── allure-results/                 # pytest --alluredir 输出目录
├── allure-report/                  # allure generate/serve 输出目录
├── artifacts/                      # 用例产物输出（流程图预览、说明文档等）
├── create_template/                # 模板生成辅助脚本
├── venv/                           # 项目虚拟环境（由 setup.sh 创建）
├── requirements.txt                # Python 依赖清单
├── setup.sh                        # 环境初始化脚本
├── run_tests.sh                    # 批量执行所有测试
├── run_single_test.sh              # 单个/筛选用例执行脚本
├── email_request.sh                # 邮件造数 curl 脚本
├── email_request_for_python.py     # 邮件造数 Python 示例
└── app_email_test_flowchart.md     # 邮件红点用例流程文档（Mermaid）
```

## 环境要求
- macOS 或 Linux（Windows 需自行调整 Shell 脚本）
- Python 3.9 及以上
- ADB（Android Platform Tools），并保证 `adb devices` 能识别目标设备
- 已启用开发者模式 & USB 调试的 Android 设备或模拟器
- Homebrew 或 npm（用于安装 Allure CLI，可选但推荐）
- 网络可访问邮件接口服务 `http://120.53.247.249:8012`

> 提示：项目自带 `venv/` 目录，如需重新创建可删除该目录后重新执行 `./setup.sh`。

## 快速开始
```bash
# 1. 赋予脚本执行权限（首次克隆后建议执行）
chmod +x *.sh create_template/*.py

# 2. 一键初始化虚拟环境与依赖
./setup.sh

# 3. 连接 Android 设备并确认 ADB 正常
adb devices

# 4. 运行全量 UI 测试
./run_tests.sh
```

执行完成后：
- Allure 原始结果保存在 `allure-results/`
- 若本机安装了 Allure CLI，脚本会自动启动 `allure serve allure-results`

## 运行方式详解
- **全量回归**：`./run_tests.sh`
  - 自动清理旧截图/缓存
  - 初始化 `uiautomator2` 服务
  - 默认执行 `src/tests/app_email/app_email_test.py`
  - 支持检测并选取首台在线设备（可通过 `ANDROID_SERIAL` 指定）
- **单用例执行**：`./run_single_test.sh <pytest 选择器>`
  - 示例：`./run_single_test.sh src/tests/app_launch/app_launch_test.py::TestDuoleWuZiQiApp::test_launch_app`
  - 支持传入 `-k`、`-m` 等原生 pytest 参数
- **手动执行**：
  ```bash
  source venv/bin/activate
  adb devices  # 确保设备在线
  ANDROID_SERIAL=<设备序列号> \
    pytest src/tests/app_email/app_email_test.py --alluredir=allure-results -v
  ```

## 测试场景概览
- `app_launch_test.py`：验证应用启动成功、包名匹配。
- `app_email_test.py`：
  - 启动并校验进入大厅（基于多组图像模板）
  - 通过接口触发邮件红点，验证红点展示 → 邮件详情 → 返回大厅红点消失的正向链路
  - 全流程包含异常兜底与限时等待逻辑
- `app_signin_test.py`：
  - 触发签到入口红点
  - 点击签到按钮并验证签到弹窗
  - 使用脚本 `email_request.sh` 进行造数支持

更多细节与流程可参考 `app_email_test_flowchart.md` 及 `artifacts/preview_markdown.html` 中的 Mermaid 流程图。

## 工具脚本与辅助资源
- `artifacts/`：集中存放用例相关产物，例如 `preview_markdown.html`（邮件用例流程图 HTML 预览），便于浏览器直接查看。
- `create_template/create_template_common.py`：交互式模板生成器，截取指定坐标的截图片段并保存为 `*_common.png`，便于扩展图像识别覆盖面。
- `email_request.sh` 与 `email_request_for_python.py`：快速调用后台邮件接口，支撑邮件红点、签到红点等场景的前置数据准备。
- `src/utils/` 下提供的通用能力：
  - `image_utils.py`：OpenCV 模板匹配、圈选、批量匹配等方法
  - `screenshot_utils.py`：统一的截图命名、Allure 附件工具
  - `scroll_utils.py`：常见上下/左右滑动与遍历查找封装
  - `time_utils.py`：时间戳格式化工具
- `src/config/coordinates.py`：按包名组织的资源 ID 映射，可通过 `set_current_app` 动态切换目标包。

## Allure 报告
1. 确认已安装 CLI（任选其一）：
   - `brew install allure`
   - `npm install -g allure-commandline`
2. 生成/查看报告：
   ```bash
   allure serve allure-results
   # 或
   allure generate allure-results --clean -o allure-report
   ```
3. 测试脚本在关键步骤会附加原始截图及带圈选的比对图，便于溯源问题。

## 常见问题排查
- **设备无法识别**：确认 USB 调试已开启，执行 `adb kill-server && adb start-server` 后重试。
- **uiautomator2 初始化失败**：执行 `venv/bin/python -m uiautomator2 init` 并留意控制台输出。
- **模板匹配失败**：检查 `src/resources/templates` 是否存在对应模板，可使用模板生成器重新提取。
- **邮件接口请求失败**：确认网络可达性与账号权限，查看 Allure 报告中的接口响应文本。

## 贡献说明
1. 新增图像模板时，请保持清晰命名并放入对应业务目录（例如 `gamehome_button/`）。
2. 如需扩展配置项，在 `src/config/coordinates.py` 中按模块补充并更新对应工具类。
3. 修改或新增用例后，确保本地执行 Allure 报告并检查截图是否正确附加。

---
如有问题或建议，欢迎提交 Issue / PR 共同完善测试体系。祝测试顺利 🎯

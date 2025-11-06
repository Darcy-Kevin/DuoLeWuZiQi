import os


# 分层坐标配置：
# 一级键：应用包名
# 二级键：模块名
# 三级键：参数名 -> 具体选择器（目前使用 resourceId）
COORDS = {
    # 多乐中国象棋（标准包）——示例占位，按需补充实际 resourceId
    "com.duole.chinachess": {
        "SDKPrivacy": {
            "resourceid-title": "com.duole.chinachess:id/dl_sdk_privacy_title",
            "agree": "com.tencent.tmgp.duole.chinachesshd:id/dl_sdk_privacy_agree",
        },
        "SDKLog": {
            "message": "com.duole.chinachess:id/dl_sdk_log_message",
            "left": "com.duole.chinachess:id/dl_sdk_log_left",
            "right": "com.duole.chinachess:id/dl_sdk_log_right",
        },
        "LoginButton": {
            "common_login_button": "com.duole.chinachess:id/dl_sdk_acc_login_common",
            "service_button": "com.duole.chinachess:id/dl_sdk_acc_login_service",
            "upload_log_button": "com.duole.chinachess:id/dl_sdk_acc_login_upload_log",
            "suitable_age_button": "com.duole.chinachess:id/dl_sdk_acc_login_suitable_age",
            "privacy_checkbox": "com.duole.chinachess:id/dl_sdk_privacy_checkbox",
        },
        "LoginDialog":{
            "resourceid-maintitle":"com.duole.chinachess:id/dl_sdk_acc_login_success_nick",
            "resourceid-subtitle":"com.duole.chinachess:id/dl_sdk_acc_login_success_acc",
            "text-maintitle":"欢迎您，巴拉巴拉",
            "text-subtitle":"微信登录"
        },
        "ChangeNameDialog":{
            "another_button":"com.duole.chinachess:id/dl_sdk_acc_change_data_random_nick_name", # 生成昵称按钮
            "input_box":"com.duole.chinachess:id/dl_sdk_acc_change_data_nick_name", # 输入框
            "edit_button":"com.duole.chinachess:id/dl_sdk_acc_change_data_commit", # 修改按钮
            "agree_button":"com.duole.chinachess:id/dl_sdk_acc_change_data_tip_commit"

        }
    },

    # 多乐中国象棋 HD 包（你提供的参数）
    "com.tencent.tmgp.duole.chinachesshd": {
        # 模块：App 启动后的隐私弹窗
        "SDKPrivacy": {
            # 已确认参数：隐私弹窗标题 resourceId
            "title": "com.tencent.tmgp.duole.chinachesshd:id/dl_sdk_privacy_title",
            # 其他参数待补充：同意按钮等（用于弹窗处理）
            # "agree": "com.tencent.tmgp.duole.chinachesshd:id/xxxx",
        },
        # 其他模块（LoginButton、SDKLog）可按需补充
        # "LoginButton": { ... },
        # "SDKLog": { ... },
    },
    "com.duole.chinachess.huawei":{
        # 模块：App启动后的隐私弹窗
        "SDKPrivacy":{
            # 参数：隐私弹窗顶部标题「欢迎来到多乐中国象棋」
            "title":"com.duole.chinachess.huawei:id/dl_sdk_privacy_title",
            # 参数：隐私弹窗按钮「不同意」
            "disagree":"com.duole.chinachess.huawei:id/dl_sdk_privacy_disagree",
            # 参数：隐私弹窗按钮「同意」
            "agree":"com.duole.chinachess.huawei:id/dl_sdk_privacy_agree",
        }
    }
}


# 当前应用包名选择：优先读取环境变量 APP_PACKAGE，否则使用默认
DEFAULT_APP = "com.duole.chinachess"
CURRENT_APP = os.environ.get("APP_PACKAGE", DEFAULT_APP)


def _get_value(module: str, param: str) -> str:
    """按当前应用读取模块参数；若当前应用缺失则回退到默认应用。

    Raises:
        KeyError: 当当前应用与默认应用均未配置该模块/参数时。
    """
    app_map = COORDS.get(CURRENT_APP, {})
    value = app_map.get(module, {}).get(param)
    if value:
        return value
    # fallback 到默认应用
    default_map = COORDS.get(DEFAULT_APP, {})
    value = default_map.get(module, {}).get(param)
    if value:
        return value
    raise KeyError(f"coordinates missing: app={CURRENT_APP}, module={module}, param={param}")


class SDKPrivacyConfig:
    @staticmethod
    def get_sdk_privacy_title() -> str:
        return _get_value("SDKPrivacy", "resourceid-title")

    @staticmethod
    def get_sdk_privacy_agree() -> str:
        return _get_value("SDKPrivacy", "agree")


class LoginButtonConfig:
    @staticmethod
    def get_common_login_button() -> str:
        return _get_value("LoginButton", "common_login_button")

    @staticmethod
    def get_service_button() -> str:
        return _get_value("LoginButton", "service_button")

    @staticmethod
    def get_upload_log_button() -> str:
        return _get_value("LoginButton", "upload_log_button")

    @staticmethod
    def get_suitable_age_button() -> str:
        return _get_value("LoginButton", "suitable_age_button")

    @staticmethod
    def get_privacy_checkbox() -> str:
        return _get_value("LoginButton", "privacy_checkbox")


class SDKLogConfig:
    @staticmethod
    def get_sdk_log_message() -> str:
        return _get_value("SDKLog", "message")

    @staticmethod
    def get_sdk_log_left() -> str:
        return _get_value("SDKLog", "left")

    @staticmethod
    def get_sdk_log_right() -> str:
        return _get_value("SDKLog", "right")

class ChangeNameDialogConfig:
    @staticmethod
    def get_resourceid_another_button() -> str:
        return _get_value("ChangeNameDialog", "another_button")

    @staticmethod
    def get_resourceid_input_box() -> str:
            return _get_value("ChangeNameDialog", "input_box")

    @staticmethod
    def get_resourceid_edit_button() -> str:
        return _get_value("ChangeNameDialog", "edit_button")

    @staticmethod
    def get_resourceid_agree_button() -> str:
        return _get_value("ChangeNameDialog", "agree_button")



def set_current_app(package_name: str) -> None:
    """在运行期切换当前应用包名（不建议在测试中频繁调用）。"""
    global CURRENT_APP
    CURRENT_APP = package_name


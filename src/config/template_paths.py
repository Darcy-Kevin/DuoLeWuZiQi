"""集中管理模板路径的配置模块。"""

from __future__ import annotations

from pathlib import Path

_TEMPLATE_ROOT = Path("src/resources/templates/common")


def _path(*parts: str) -> str:
    return str(_TEMPLATE_ROOT.joinpath(*parts))


class TemplatePaths:
    class gamehome:
        class button:
            email = _path(
                "gamehome",
                "gamehome_button",
                "gamehome_email_button_not_reddot_common.png",
            )
            email_reddot = _path(
                "gamehome",
                "gamehome_button",
                "gamehome_email_button_reddot_count_1_common.png",
            )
            signin = _path(
                "gamehome",
                "gamehome_button",
                "gamehome_signin_button_common.png",
            )
            signin_reddot = _path(
                "gamehome",
                "gamehome_button",
                "gamehome_signin_button_reddot_common.png",
            )

        class text:
            pass

        class icon:
            duolebi = _path(
                "gamehome",
                "gamehome_icon",
                "gamehome_duolebi_icon_common.png",
            )

    class email:
        class button:
            back = _path(
                "email",
                "email_button",
                "email_back_button_common.png",
            )
            select_unread = _path(
                "email",
                "email_button",
                "email_select_unread_button_common.png",
            )
            unselect_unread = _path(
                "email",
                "email_button",
                "email_unselect_unread_button_common.png",
            )
            select_read = _path(
                "email",
                "email_button",
                "email_select_read_button_common.png",
            )
            unselect_read = _path(
                "email",
                "email_button",
                "email_unselect_read_button_common.png",
            )
            unreceive = _path(
                "email",
                "email_button",
                "email_unreceive_button_common.png",
            )
            view = _path(
                "email",
                "email_button",
                "email_view_button_common.png",
            )
            viewed = _path(
                "email",
                "email_button",
                "email_viewed_button_common.png",
            )
            confirm_delete = _path(
                "email",
                "email_button",
                "email_confirm_delete_button_common.png",
            )
            one_key_view = _path(
                "email",
                "email_button",
                "email_one_key_view_button_common.png",
            )
            one_key_delete = _path(
                "email",
                "email_button",
                "email_one_key_delete_button_common.png",
            )

        class text:
            get = _path(
                "email",
                "email_text",
                "email_get_text_common.png",
            )
            title = _path(
                "email",
                "email_text",
                "email_title_reddot_exit_text_common.png",
            )

        class icon:
            none = _path("email", "email_icon", "email_null_icon_common.png")

    class email_detail:
        class button:
            close = _path(
                "email_detail",
                "email_detail_button",
                "email_detail_close_button_common.png",
            )
            receive = _path(
                "email_detail",
                "email_detail_button",
                "email_detail_receive_button_common.png",
            )
            delete = _path(
                "email_detail",
                "email_detail_button",
                "email_detail_delete_mail_button_common.png",
            )
            confirm = _path(
                "email_detail",
                "email_detail_button",
                "email_detail_confirm_button_common.png",
            )

        class text:
            title = _path(
                "email_detail",
                "email_detail_text",
                "email_detail_title_text_common.png",
            )
            tip = _path(
                "email_detail",
                "email_detail_text",
                "email_detail_tip_text_common.png",
            )
            get = _path(
                "email_detail",
                "email_detail_text",
                "email_detail_get_text_common.png",
            )

    class announcement:
        class button:
            close = _path(
                "announcement_detail",
                "announcement_detail_button",
                "announcement_detail_close_button_common.png",
            )

        class text:
            title = _path(
                "announcement_detail",
                "announcement_detail_text",
                "announcement_detail_title_text_common.png",
            )

    class signin_dialog:
        class button:
            close = _path(
                "signin_dialog",
                "signin_dialog_button",
                "signin_dialog_close_button_common.png",
            )

        class text:
            title = _path(
                "signin_dialog",
                "signin_dialog_text",
                "signin_dialog_title_text_common.png",
            )

from dialogs.user_dialog.dialog import user_dialog
from dialogs.admin_dialog.dialog import admin_dialog
from dialogs.profile_dialog.dialog import profile_dialog


def get_dialogs():
    return [user_dialog, profile_dialog, admin_dialog]
from aiogram.fsm.state import State, StatesGroup

# Обычная группа состояний


class startSG(StatesGroup):
    start = State()
    get_clothes = State()
    get_model = State()
    settings_menu = State()
    choose_category = State()
    get_bg_image = State()


class adminSG(StatesGroup):
    start = State()
    get_keyboard = State()
    get_mail = State()
    get_time = State()
    confirm_mail = State()
    deeplink_menu = State()
    get_deeplink_name = State()
    deeplink_del = State()
    admin_menu = State()
    admin_del = State()
    admin_add = State()
    rates_menu = State()
    gen_rate_menu = State()
    add_gen_rate_amount = State()
    add_gen_rate_price = State()
    choose_gen_rate = State()
    change_gen_menu = State()
    change_gen_amount = State()
    change_gen_price = State()
    sub_rate_menu = State()
    add_sub_rate_months = State()
    add_sub_rate_price = State()
    choose_sub_rate = State()
    change_sub_menu = State()
    change_sub_months = State()
    change_sub_price = State()
    vouchers_menu = State()
    get_voucher = State()
    get_voucher_amount = State()
    del_voucher = State()
    photos_menu = State()
    model_photos = State()
    add_model_photo = State()
    cloth_photos = State()
    add_cloth_photo = State()
    get_gen_amount = State()
    subs_menu = State()
    get_photos_count = State()
    texts_menu = State()
    get_text = State()


class profileSG(StatesGroup):
    start = State()
    info_menu = State()
    generations_menu = State()
    choose_pay_method = State()
    payment = State()
    success_payment = State()
    sub_menu = State()
    choose_sub_menu = State()
    ref_menu = State()
    get_voucher = State()
    images_menu = State()
    bg_photo_get = State()
    photos_menu = State()
    add_photo = State()
    help_menu = State()

from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.admin_dialog import getters
from states.state_groups import adminSG


admin_dialog = Dialog(
    Window(
        Const('Админ панель'),
        Button(Const('📊 Получить статистику'), id='get_static', on_click=getters.get_static),
        SwitchTo(Const('Управление привилегиями подписки'), id='sub_menu_switcher', state=adminSG.subs_menu),
        SwitchTo(Const('Управление тарифами'), id='rates_menu_switcher', state=adminSG.rates_menu),
        SwitchTo(Const('Управление текстами'), id='texts_menu_switcher', state=adminSG.texts_menu),
        SwitchTo(Const('Поменять стоимость генерации(не нужно)'), id='get_gen_amount', state=adminSG.get_gen_amount),
        SwitchTo(Const('Управление кодами ваучера'), id='vouchers_menu', state=adminSG.vouchers_menu),
        SwitchTo(Const('Управление фото'), id='photos_menu_switcher', state=adminSG.photos_menu),
        SwitchTo(Const('🔗 Управление диплинками'), id='deeplinks_menu_switcher', state=adminSG.deeplink_menu),
        SwitchTo(Const('👥 Управление админами'), id='admin_menu_switcher', state=adminSG.admin_menu),
        SwitchTo(Const('Сделать рассылку'), id='get_mail_switcher', state=adminSG.get_mail),
        Cancel(Const('Назад'), id='close_admin'),
        state=adminSG.start
    ),
    Window(
        Format('Текст для меню подписки:\n{sub_text}\n\nТекст для меню рефелаки:\n{ref_text}\n\n'
               'Текст для меню информации:\n{info_text}'),
        Column(
            Button(Const('Поменять текст подписки'), id='sub_get_text_switcher', on_click=getters.get_text_switcher),
            Button(Const('Поменять текст рефелаки'), id='ref_get_text_switcher', on_click=getters.get_text_switcher),
            Button(Const('Поменять текст информации'), id='info_get_text_switcher', on_click=getters.get_text_switcher),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.texts_menu_getter,
        state=adminSG.texts_menu
    ),
    Window(
        Const('Введите новый текст'),
        TextInput(
            id='get_text',
            on_success=getters.get_text
        ),
        SwitchTo(Const('🔙 Назад'), id='back_texts_menu', state=adminSG.texts_menu),
        state=adminSG.get_text
    ),
    Window(
        Const('Меню управления привилегиями подписки'),
        Format('Условия подписки:\n - Наличие водяного знака: {watermark}\n - Замена фона: {background}'
               '\n - Кол-во доп фото моделей: {photos}'),
        Column(
            Button(Format('{watermark}Водяной знак'), id='watermark_toggle', on_click=getters.sub_toggle),
            Button(Format('{background}Замена фона'), id='background_toggle', on_click=getters.sub_toggle),
            SwitchTo(Const('Поменять кол-во фото'), id='get_photo_count', state=adminSG.get_photos_count),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.sub_menu_getter,
        state=adminSG.subs_menu
    ),
    Window(
        Const('Введите кол-во допустимых фото моделей'),
        TextInput(
            id='get_photos_count',
            on_success=getters.get_photo_count
        ),
        SwitchTo(Const('Назад'), id='back_subs_menu', state=adminSG.subs_menu),
        state=adminSG.get_photos_count
    ),
    Window(
        Format('Стоимость одной генерации в яблоках: {price}, чтобы поставить новую стоимость введите кол-во'
               ' яблок за генерацию'),
        TextInput(
            id='get_get_amount',
            on_success=getters.get_gen_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.get_gen_amount_getter,
        state=adminSG.get_gen_amount
    ),
    Window(
        Const('Меню управления готовыми фото для одежды и моделей'),
        Column(
            SwitchTo(Const('Фото одежды'), id='cloth_photos_switcher', state=adminSG.cloth_photos),
            SwitchTo(Const('Фото моделей'), id='model_photos_switcher', state=adminSG.model_photos),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.photos_menu
    ),
    Window(
        DynamicMedia('media', when='media'),
        Const('Меню управления и просмотра фоток моделей, тут вы можете просматривать уже добавленные фотки'),
        Group(
            Row(
                Button(Const('<'), id='previous_model_page', on_click=getters.model_pager, when='not_first'),
                Button(Const('>'), id='next_model_page', on_click=getters.model_pager, when='not_last'),
            ),
            when='model'
        ),
        SwitchTo(Const('Добавить новое фото'), id='add_model_photo_switcher', state=adminSG.add_model_photo),
        Button(Const('Удалить фото'), id='del_photo', on_click=getters.del_photo),
        SwitchTo(Const('Назад'), id='back_photos_menu', state=adminSG.photos_menu),
        getter=getters.model_getter,
        state=adminSG.model_photos
    ),
    Window(
        Const('Отправьте саму фотографию модели или ссылку на нее'),
        TextInput(
            id='get_model',
            on_success=getters.get_model_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_model_photo
        ),
        SwitchTo(Const('Назад'), id='back_model_photos_menu', state=adminSG.model_photos),
        state=adminSG.add_model_photo
    ),
    Window(
        DynamicMedia('media', when='media'),
        Const('Меню управления и просмотра фоток одежды, тут вы можете просматривать уже добавленные фотки'),
        Group(
            Row(
                Button(Const('<'), id='previous_cloth_page', on_click=getters.cloth_pager, when='not_first'),
                Button(Const('>'), id='next_cloth_page', on_click=getters.cloth_pager, when='not_last'),
            ),
            when='model'
        ),
        SwitchTo(Const('Добавить новое фото'), id='add_model_photo_switcher', state=adminSG.add_cloth_photo),
        Button(Const('Удалить фото'), id='del_photo', on_click=getters.del_photo),
        SwitchTo(Const('Назад'), id='back_photos_menu', state=adminSG.photos_menu),
        getter=getters.cloth_getter,
        state=adminSG.cloth_photos
    ),
    Window(
        Const('Отправьте саму фотографию модели или ссылку на нее'),
        TextInput(
            id='get_model',
            on_success=getters.get_cloth_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_cloth_photo
        ),
        SwitchTo(Const('Назад'), id='back_cloth_photos_menu', state=adminSG.cloth_photos),
        state=adminSG.add_cloth_photo
    ),
    Window(
        Const('Меню управления кодами ваучера\n'),
        Format('Действующие коды:\n{codes}'),
        Column(
            SwitchTo(Const('Создать новый код'), id='get_voucher_kod_switcher', state=adminSG.get_voucher),
            SwitchTo(Const('Удалить существующий'), id='del_voucher_switcher', state=adminSG.del_voucher),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.voucher_menu_getter,
        state=adminSG.vouchers_menu
    ),
    Window(
        Const('Введите код ваучера'),
        TextInput(
            id='get_voucher_kod',
            on_success=getters.get_voucher_kod
        ),
        SwitchTo(Const('🔙 Назад'), id='back_voucher_menu', state=adminSG.vouchers_menu),
        state=adminSG.get_voucher
    ),
    Window(
        Const('Введите кол-во генераций которые получит юзер при вводе кода ваучера'),
        TextInput(
            id='get_voucher_amount',
            on_success=getters.get_voucher_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back_get_voucher', state=adminSG.get_voucher),
        state=adminSG.get_voucher_amount
    ),
    Window(
        Const('Выберите код ваучера который вы хотели бы удалить'),
        Group(
            Select(
                Format('{item[0]}'),
                id='voucher_del_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_voucher
            ),
            width=2
        ),
        SwitchTo(Const('🔙 Назад'), id='back_voucher_menu', state=adminSG.vouchers_menu),
        getter=getters.del_voucher_menu_getter,
        state=adminSG.del_voucher
    ),
    Window(
        Const('Выберите какую категорию тарифов вы хотели бы отредактировать'),
        Column(
            SwitchTo(Const('Управление тарифами подписки'), id='sub_rate_menu_switcher', state=adminSG.sub_rate_menu),
            SwitchTo(Const('Управление тарифами генераций'), id='gen_rate_menu_switcher', state=adminSG.gen_rate_menu),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        state=adminSG.rates_menu
    ),
    Window(
        Format('💵 *Действующие тарифы*:\n\n{rates}'),
        Column(
            SwitchTo(Const('➕ Добавить тариф'), id='add_gen_amount_switcher', state=adminSG.add_gen_rate_amount),
            SwitchTo(Const('✏️ Изменить тарифы'), id='choose_gen_rate_switcher', state=adminSG.choose_gen_rate),
            SwitchTo(Const('🔙 Назад'), id='back_rates_menu', state=adminSG.rates_menu)
        ),
        getter=getters.gen_rate_menu_getter,
        state=adminSG.gen_rate_menu
    ),
    Window(
        Const('💬 Введите количество генераций для тарифа'),
        TextInput(
            id='get_gen_rate_amount',
            on_success=getters.get_gen_rate_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back_gen_rate_menu', state=adminSG.gen_rate_menu),
        state=adminSG.add_gen_rate_amount
    ),
    Window(
        Const('💬 Введите цену за указанное количество токенов'),
        TextInput(
            id='get_gen_rate_price',
            on_success=getters.get_gen_rate_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_gen_rate_menu', state=adminSG.gen_rate_menu),
        state=adminSG.add_gen_rate_price
    ),
    Window(
        Const('🔍 Выберите тариф для изменения'),
        Group(
            Select(
                Format('💼 {item[0]}'),
                id='rate_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_gen_rate
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_gen_rate_menu', state=adminSG.gen_rate_menu),
        getter=getters.rate_gen_choose_builder,
        state=adminSG.choose_gen_rate
    ),
    Window(
        Format('💼 *Данные выбранного тарифа*:\n\n{rate}'),
        Column(
            SwitchTo(Const('🔄 Изменить количество генераций'), id='change_gen_amount_switcher', state=adminSG.change_gen_amount),
            SwitchTo(Const('💲 Изменить цену'), id='change_gen_price_switcher', state=adminSG.change_gen_price),
            Button(Const('Удалить тариф'), id='del_gen_rate', on_click=getters.del_rate),
        ),
        SwitchTo(Const('🔙 Назад'), id='back_gen_rate_menu', state=adminSG.gen_rate_menu),
        getter=getters.rate_gen_change_getter,
        state=adminSG.change_gen_menu
    ),
    Window(
        Const('💬 Введите количество генераций для изменения'),
        TextInput(
            id='change_gen_rate_amount',
            on_success=getters.change_gen_amount
        ),
        SwitchTo(Const('🔙 Назад'), id='back_change_gen_menu', state=adminSG.change_gen_menu),
        state=adminSG.change_gen_amount
    ),
    Window(
        Const('💬 Введите цену за данное количество генераций'),
        TextInput(
            id='change_gen_rate_price',
            on_success=getters.change_gen_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_gen_change_menu', state=adminSG.change_gen_menu),
        state=adminSG.change_gen_price
    ),
    Window(
        Format('💵 *Действующие тарифы*:\n\n{rates}'),
        Column(
            SwitchTo(Const('➕ Добавить тариф'), id='add_sub_amount_switcher', state=adminSG.add_sub_rate_months),
            SwitchTo(Const('✏️ Изменить тарифы'), id='choose_sub_rate_switcher', state=adminSG.choose_sub_rate),
            SwitchTo(Const('🔙 Назад'), id='back_rates_menu', state=adminSG.rates_menu)
        ),
        getter=getters.sub_rate_menu_getter,
        state=adminSG.sub_rate_menu
    ),
    Window(
        Const('💬 Введите количество месяцев для тарифа'),
        TextInput(
            id='get_sub_rate_months',
            on_success=getters.get_sub_rate_months
        ),
        SwitchTo(Const('🔙 Назад'), id='back_sub_rate_menu', state=adminSG.sub_rate_menu),
        state=adminSG.add_sub_rate_months
    ),
    Window(
        Const('💬 Введите цену за указанное количество месяцев'),
        TextInput(
            id='get_sub_rate_price',
            on_success=getters.get_sub_rate_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_sub_rate_menu', state=adminSG.sub_rate_menu),
        state=adminSG.add_sub_rate_price
    ),
    Window(
        Const('🔍 Выберите тариф для изменения'),
        Group(
            Select(
                Format('💼 {item[0]}'),
                id='rate_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_sub_rate
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_sub_rate_menu', state=adminSG.sub_rate_menu),
        getter=getters.rate_sub_choose_builder,
        state=adminSG.choose_sub_rate
    ),
    Window(
        Format('💼 *Данные выбранного тарифа*:\n\n{rate}'),
        Column(
            SwitchTo(Const('🔄 Изменить количество месяцев'), id='change_sub_amount_switcher',
                     state=adminSG.change_sub_months),
            SwitchTo(Const('💲 Изменить цену'), id='change_sub_price_switcher', state=adminSG.change_sub_price),
            Button(Const('Удалить тариф'), id='del_sub_rate', on_click=getters.del_rate),
        ),
        SwitchTo(Const('🔙 Назад'), id='back_sub_rate_menu', state=adminSG.sub_rate_menu),
        getter=getters.rate_sub_change_getter,
        state=adminSG.change_sub_menu
    ),
    Window(
        Const('💬 Введите количество месяцев для изменения'),
        TextInput(
            id='change_sub_rate_months',
            on_success=getters.change_sub_months
        ),
        SwitchTo(Const('🔙 Назад'), id='back_change_sub_menu', state=adminSG.change_sub_menu),
        state=adminSG.change_sub_months
    ),
    Window(
        Const('💬 Введите цену за данное количество месяцев'),
        TextInput(
            id='change_sub_rate_price',
            on_success=getters.change_sub_price
        ),
        SwitchTo(Const('🔙 Назад'), id='back_sub_change_menu', state=adminSG.change_sub_menu),
        state=adminSG.change_sub_price
    ),
    Window(
        Format('🔗 *Меню управления диплинками*\n\n'
               '🎯 *Имеющиеся диплинки*:\n{links}'),
        Column(
            Button(Const('➕ Добавить диплинк'), id='add_deeplink', on_click=getters.add_deeplink),
            SwitchTo(Const('❌ Удалить диплинки'), id='del_deeplinks', state=adminSG.deeplink_del),
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.deeplink_menu_getter,
        state=adminSG.deeplink_menu
    ),
    Window(
        Const('❌ Выберите диплинк для удаления'),
        Group(
            Select(
                Format('🔗 {item[0]}'),
                id='deeplink_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_deeplink
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='deeplinks_back', state=adminSG.deeplink_menu),
        getter=getters.del_deeplink_getter,
        state=adminSG.deeplink_del
    ),
    Window(
        Format('👥 *Меню управления администраторами*\n\n {admins}'),
        Column(
            SwitchTo(Const('➕ Добавить админа'), id='add_admin_switcher', state=adminSG.admin_add),
            SwitchTo(Const('❌ Удалить админа'), id='del_admin_switcher', state=adminSG.admin_del)
        ),
        SwitchTo(Const('🔙 Назад'), id='back', state=adminSG.start),
        getter=getters.admin_menu_getter,
        state=adminSG.admin_menu
    ),
    Window(
        Const('👤 Выберите пользователя, которого хотите сделать админом\n'
              '⚠️ Ссылка одноразовая и предназначена для добавления только одного админа'),
        Column(
            Url(Const('🔗 Добавить админа (ссылка)'), id='add_admin',
                url=Format('http://t.me/share/url?url=https://t.me/AidaLook_bot?start={id}')),  # поменять ссылку
            Button(Const('🔄 Создать новую ссылку'), id='new_link_create', on_click=getters.refresh_url),
            SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu)
        ),
        getter=getters.admin_add_getter,
        state=adminSG.admin_add
    ),
    Window(
        Const('❌ Выберите админа для удаления'),
        Group(
            Select(
                Format('👤 {item[0]}'),
                id='admin_del_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.del_admin
            ),
            width=1
        ),
        SwitchTo(Const('🔙 Назад'), id='back_admin_menu', state=adminSG.admin_menu),
        getter=getters.admin_del_getter,
        state=adminSG.admin_del
    ),
    Window(
        Const('Введите сообщение которое вы хотели бы разослать'),
        MessageInput(
            content_types=ContentType.ANY,
            func=getters.get_mail
        ),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        state=adminSG.get_mail
    ),
    Window(
        Const('Введите время в которое сообщение должно разослаться всем юзерам'),
        TextInput(
            id='get_time',
            on_success=getters.get_time
        ),
        SwitchTo(Const('Продолжить без автоудаления'), id='get_keyboard_switcher', state=adminSG.get_keyboard),
        SwitchTo(Const('Назад'), id='back_get_mail', state=adminSG.get_mail),
        state=adminSG.get_time
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к рассылаемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_mail_keyboard',
            on_success=getters.get_mail_keyboard
        ),
        SwitchTo(Const('Продолжить без кнопок'), id='confirm_mail_switcher', state=adminSG.confirm_mail),
        SwitchTo(Const('Назад'), id='back_get_time', state=adminSG.get_time),
        state=adminSG.get_keyboard
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            Button(Const('Нет'), id='cancel_malling', on_click=getters.cancel_malling),
        ),
        SwitchTo(Const('Назад'), id='back_get_keyboard', state=adminSG.get_keyboard),
        state=adminSG.confirm_mail
    ),
)
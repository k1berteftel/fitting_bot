from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Multiselect, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.profile_dialog import getters

from states.state_groups import profileSG


profile_dialog = Dialog(
    Window(
        Format('<b>👤 Профиль</b>\n\n<b>Юзернейм:</b> {username}\n<b>💰 Генерации:</b> {generations}\n'
                   '<b>✨ Подписка:</b> {sub}'),
        Column(
            SwitchTo(Const('💰Приобрести генерации'), id='generations_menu_switcher', state=profileSG.generations_menu),
            SwitchTo(Const('✨Управление подпиской'), id='sub_menu_switcher', state=profileSG.sub_menu),
            SwitchTo(Const('🏦Реферальная программа'), id='ref_menu_switcher', state=profileSG.ref_menu),
            SwitchTo(Const('🖼Управление фотографиями'), id='photos_menu_switcher', state=profileSG.photos_menu),
        ),
        Cancel(Const('🔙Назад'), id='close_dialog'),
        getter=getters.start_getter,
        state=profileSG.start
    ),
    Window(
        Const('<b>Выберите тариф генераций</b>'),
        Group(
            Select(
                Format('{item[0]}'),
                id='gen_rates_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_rate
            ),
            width=2
        ),
        SwitchTo(Const('🔼Ввести код ваучера'), id='get_voucher_switcher', state=profileSG.get_voucher),
        SwitchTo(Const('🔙Назад'), id='back', state=profileSG.start),
        getter=getters.generations_menu_getter,
        state=profileSG.generations_menu
    ),
    Window(
        Const('Пожалуйста произведите оплату по данной ссылке и потом ❗️<b>обязательно</b>❗️ '
              'после произведения оплаты не выходите из данного меню до ее подтверждения'),
        Column(
            Url(Const('🔗Оплатить'), id='payment_link', url=Format('{url}')),
        ),
        SwitchTo(Const('🔙Назад'), id='back_generations_menu', state=profileSG.generations_menu),
        getter=getters.payment_menu_getter,
        state=profileSG.payment
    ),
    Window(
        Format('<b>Подписка:</b> {sub}\n\n{text}'),
        Column(
            SwitchTo(Const('💰Приобрести подписку'), id='choose_sub_menu', state=profileSG.choose_sub_menu),
        ),
        SwitchTo(Const('🔙Назад'), id='back', state=profileSG.start),
        getter=getters.sub_menu_getter,
        state=profileSG.sub_menu
    ),
    Window(
        Const('Выберите тариф для покупки подписки'),
        Group(
            Select(
                Format('{item[0]}'),
                id='gen_rates_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_sub
            ),
            width=2
        ),
        SwitchTo(Const('🔙Назад'), id='back_sub_menu', state=profileSG.sub_menu),
        getter=getters.choose_sub_menu_getter,
        state=profileSG.choose_sub_menu
    ),
    Window(
        Format('<b>Ваши рефералы:</b> {refs}\n<b>Вознаграждения(за все время):</b> {prizes}\n\n'
               '<b>Ваша реферальная ссылка:</b> {link}\n{text}'),
        Column(
            Url(Const('Поделиться реферальной ссылкой'), id='ref_link', url=Format('{link}')),
        ),
        SwitchTo(Const('🔙Назад'), id='back', state=profileSG.start),
        getter=getters.ref_menu_getter,
        state=profileSG.ref_menu
    ),
    Window(
        Const('Введите код ваучера'),
        TextInput(
            id='get_voucher',
            on_success=getters.get_voucher
        ),
        SwitchTo(Const('🔙Назад'), id='back_ref_menu', state=profileSG.generations_menu),
        state=profileSG.get_voucher
    ),
    Window(
        DynamicMedia('media', when='media'),
        Format('Работа с фото модели и фоном. Фон меняется при подписке на бота'),
        TextInput(
            id='get_image',
            on_success=getters.get_image_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_image
        ),
        Row(
            Button(Const('◀️'), id='previous_photo_page', on_click=getters.photo_pager, when='not_first'),
            Button(Const('▶️'), id='next_photo_page', on_click=getters.photo_pager, when='not_last'),
            when='media'
        ),
        Button(Const('🌄Поменять у этого изображения фон'), id='get_bg_image_switcher', on_click=getters.get_bg_image_switcher, when='media'),
        Button(Const('➕Добавить фото'), id='add_photo_switcher', on_click=getters.add_photo_switcher),
        Button(Const('🗑Удалить фото'), id='del_photo', on_click=getters.del_photo, when='media'),
        SwitchTo(Const('🔙Назад'), id='back', state=profileSG.start),
        getter=getters.photos_menu_getter,
        state=profileSG.photos_menu
    ),
    Window(
        Const('Отправьте ссылку изображения или само изображение для замены фона'),
        TextInput(
            id='get_bg_image',
            on_success=getters.get_bg_image_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_bg_image
        ),
        SwitchTo(Const('🔙Назад'), id='back_photos_menu', state=profileSG.photos_menu),
        state=profileSG.bg_photo_get
    ),
    Window(
        Const('Отправьте фотографию модели или ссылку на нее'),
        TextInput(
            id='get_model',
            on_success=getters.get_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo
        ),
        SwitchTo(Const('🔙Назад'), id='back_model_photos_menu', state=profileSG.photos_menu),
        state=profileSG.add_photo
    ),
)
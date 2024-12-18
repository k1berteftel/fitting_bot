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
        Format('<b>Ваш username:</b> {username}\n'
               '<b>Доступные генерации:</b> {generations}\n'
               '<b>Подписка:</b> {sub}'),
        Column(
            SwitchTo(Const('Приобрести генерации'), id='generations_menu_switcher', state=profileSG.generations_menu),
            SwitchTo(Const('Управление подпиской'), id='sub_menu_switcher', state=profileSG.sub_menu),
            SwitchTo(Const('Реферальная программа'), id='ref_menu_switcher', state=profileSG.ref_menu),
            SwitchTo(Const('Управление фотографиями'), id='photos_menu_switcher', state=profileSG.photos_menu),
            Button(Format('{status}|Уведомления'), id='notifications_toggle', on_click=getters.notifications_toggle),
        ),
        Cancel(Const('Назад'), id='close_dialog'),
        getter=getters.start_getter,
        state=profileSG.start
    ),
    Window(
        Const('Выберите тариф генераций'),
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
        SwitchTo(Const('Ввести код ваучера'), id='get_voucher_switcher', state=profileSG.get_voucher),
        SwitchTo(Const('Назад'), id='back', state=profileSG.start),
        getter=getters.generations_menu_getter,
        state=profileSG.generations_menu
    ),
    Window(
        Const('Пожалуйста произведите оплату по данной ссылке и потом обязательно нажмите на кнопку проверки оплаты'),
        Column(
            Url(Const('Оплатить'), id='payment_link', url=Format('{url}')),
            Button(Const('Проверить оплату'), id='check_payment', on_click=getters.check_payment),
        ),
        SwitchTo(Const('Назад'), id='back_generations_menu', state=profileSG.generations_menu),
        getter=getters.payment_menu_getter,
        state=profileSG.payment
    ),
    Window(
        Format('<b>Подписка:</b> {sub}\n\nУсловия привилегии подписки'),
        Column(
            SwitchTo(Const('Приобрести подписку'), id='choose_sub_menu', state=profileSG.choose_sub_menu),
        ),
        SwitchTo(Const('Назад'), id='back', state=profileSG.start),
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
        SwitchTo(Const('Назад'), id='back_sub_menu', state=profileSG.sub_menu),
        getter=getters.choose_sub_menu_getter,
        state=profileSG.choose_sub_menu
    ),
    Window(
        Format('<b>Ваши рефералы:</b> {refs}\n<b>Вознаграждения:</b> {prizes}\n\n'
               '<b>Ваша реферальная ссылка:</b> {link}'),
        Column(
            Url(Const('Поделиться реферальной ссылкой'), id='ref_link', url=Format('{link}')),
        ),
        SwitchTo(Const('Назад'), id='back', state=profileSG.start),
        getter=getters.ref_menu_getter,
        state=profileSG.ref_menu
    ),
    Window(
        Const('Введите код ваучера'),
        TextInput(
            id='get_voucher',
            on_success=getters.get_voucher
        ),
        SwitchTo(Const('Назад'), id='back_ref_menu', state=profileSG.generations_menu),
        state=profileSG.get_voucher
    ),
    Window(
        DynamicMedia('media', when='media'),
        Const('Это меню просмотра всех ваших результатов, тут вы можете ознакомиться со всеми своими '
              'результатами примерки с добавления заднего фона и без'),
        Row(
            Button(Const('<'), id='previous_photo_page', on_click=getters.photo_pager, when='not_first'),
            Button(Const('>'), id='next_photo_page', on_click=getters.photo_pager, when='not_last'),
            when='model'
        ),
        Button(Const('Удалить фото'), id='del_photo', on_click=getters.del_photo, when='media'),
        SwitchTo(Const('Назад'), id='back', state=profileSG.start),
        getter=getters.photos_menu_getter,
        state=profileSG.photos_menu
    ),
)
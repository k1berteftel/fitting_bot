from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Multiselect
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog import getters

from states.state_groups import startSG, adminSG, profileSG

user_dialog = Dialog(
    Window(
        DynamicMedia('media', when='media'),
        Const('Выберите фото одежды из своего портфолио или отправьте новое'),
        TextInput(
            id='get_cloth',
            on_success=getters.get_cloth_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_cloth_photo
        ),
        Group(
            Row(
                Button(Const('<'), id='previous_cloth_page', on_click=getters.cloth_pager, when='not_first'),
                Button(Const('Выбрать это'), id='choose_cloth', on_click=getters.choose_cloth),
                Button(Const('>'), id='next_cloth_page', on_click=getters.cloth_pager, when='not_last'),
            ),
            when='cloth'
        ),
        Button(Const('Настройки'), id='cloth_settings_switcher', on_click=getters.settings_switcher),
        Start(Const('Админ панель'), id='start_admin', state=adminSG.start, when='admin'),
        Start(Const('Профиль'), id='start_profile', state=profileSG.start),
        getter=getters.cloth_getter,
        state=startSG.get_clothes
    ),
    Window(
        DynamicMedia('media', when='media'),
        Const('Выберите фото модели из своего портфолио или отправьте новое'),
        TextInput(
            id='get_model',
            on_success=getters.get_model_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_model_photo
        ),
        Group(
            Row(
                Button(Const('<'), id='previous_model_page', on_click=getters.model_pager, when='not_first'),
                Button(Const('Выбрать это'), id='choose_model', on_click=getters.choose_model),
                Button(Const('>'), id='next_model_page', on_click=getters.model_pager, when='not_last'),
            ),
            when='model'
        ),
        Button(Const('Настройки'), id='model_settings_switcher', on_click=getters.settings_switcher),
        Start(Const('Профиль'), id='start_profile', state=profileSG.start),
        SwitchTo(Const('Назад'), id='back_cloth', state=startSG.get_clothes),
        getter=getters.model_getter,
        state=startSG.get_model
    ),
    Window(
        Const('Выберите на какую часть тела будет производиться примерка одежды'),
        Column(
            Button(Const('Вверх'), id='high_category_choose', on_click=getters.choose_category),
            Button(Const('Низ'), id='low_category_choose', on_click=getters.choose_category),
            Button(Const('Полный комплект'), id='full_category_choose', on_click=getters.choose_category),
        ),
        state=startSG.choose_category
    ),
    Window(
        Const('Отправьте фото или изображение которое вы хотите подставить на '
              'задний фон получившего результата примерки'),
        TextInput(
            id='get_bg_image',
            on_success=getters.get_bg_image_link
        ),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_bg_image
        ),
        Column(
            Button(Const('Продолжить без заднего фона'), id='start_fitting', on_click=getters.start_fitting)
        ),
        SwitchTo(Const('Назад'), id='back_choose_category', state=startSG.choose_category),
        state=startSG.get_bg_image
    ),
    Window(
        Const('Тут вы можете настроить точечные моменты примерки'),
        Column(
            Button(Format('{param_1}Разрешить длинной одежде прикрывать(менять) ноги/обувь'), id='1_param', on_click=getters.on_param),
            Button(Format('{param_2}Разрешить изменение внешнего вида рук модели'), id='2_param', on_click=getters.on_param),
            Button(Format('{param_3}Сохранить исходный задний фон'), id='3_param', on_click=getters.on_param),
            Button(Format('{param_4}Сохранить внешний вид одежды которая не была заменена'), id='4_param', on_click=getters.on_param),
        ),
        Button(Const('Назад'), id='back_get_photos', on_click=getters.back_switcher),
        getter=getters.settings_getter,
        state=startSG.settings_menu
    ),
)
import datetime
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.action_data_class import DataInteraction
from database.model import DeeplinksTable, AdminsTable
from utils.build_ids import get_random_id
from utils.schdulers import send_messages
from config_data.config import load_config, Config
from states.state_groups import adminSG


async def get_text(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    type = dialog_manager.dialog_data.get('text')
    if type == 'sub':
        await session.set_text(sub_text=text)
    elif type == 'info':
        await session.set_text(info_text=text)
    elif type == 'image':
        await session.set_text(image_text=text)
    else:
        await session.set_text(ref_text=text)
    await msg.answer('Текст был успешно обновлен')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.texts_menu)


async def get_text_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['text'] = clb.data.split('_')[0]
    await dialog_manager.switch_to(adminSG.get_text)


async def texts_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    texts = await session.get_texts()
    return {
        'sub_text': texts.sub_text,
        'ref_text': texts.ref_text,
        'info_text': texts.info_text,
        'image_text': texts.image_text
    }


async def get_photo_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        photos = int(text)
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_sub_photos(photos)
    await dialog_manager.switch_to(adminSG.subs_menu)


async def sub_toggle(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    terms = await session.get_sub_terms()
    if clb.data.startswith('watermark'):
        if terms.watermark:
            await session.update_sub_terms(watermark=False)
        else:
            await session.update_sub_terms(watermark=True)
    else:
        if terms.background:
            await session.update_sub_terms(background=False)
        else:
            await session.update_sub_terms(background=True)
    await dialog_manager.switch_to(adminSG.subs_menu)


async def sub_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    terms = await session.get_sub_terms()
    return {
        'watermark': '✅' if terms.watermark else '❌',
        'background': '✅' if terms.background else '❌',
        'photos': terms.photos
    }


async def get_gen_amount_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    amount = await session.get_gen_amount()
    return {'price': amount}


async def get_gen_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        amount = int(text)
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_gen_amount(amount)
    await dialog_manager.switch_to(adminSG.get_gen_amount)


async def get_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    users = await session.get_users()
    active = 0
    today = 0
    activity = 0
    subs = 0
    for user in users:
        if user.active:
            active += 1
        if user.entry > datetime.datetime.today() - datetime.timedelta(days=1):
            today += 1
        if user.activity > datetime.datetime.today() - datetime.timedelta(days=1):
            activity += 1
        if user.sub:
            subs += 1
    counts = await session.get_counts()
    text = (f'Всего юзеров в боте: {len(users)}\nИз них: {active} Активных\nНеактивных: {len(users) - active}\n\n'
            f'Зашло в бота сегодня: {today}\nВзаимодействовало с ботом сегодня: {activity}\n'
            f'Приобрело подписку: {subs}\n\nЗамен фона(всего): {counts.background}\n'
            f'Замен одежды(всего): {counts.images}')
    await clb.message.answer(text=text)


async def get_cloth_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await msg.delete()
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ту ссылку на фото, пожалуйста попробуйте снова')
        return
    await session.add_photo(text, 'cloth')
    await dialog_manager.switch_to(adminSG.cloth_photos)


async def get_cloth_photo(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    await msg.delete()
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_photo(msg.photo[-1].file_id, 'cloth')
    await dialog_manager.switch_to(adminSG.cloth_photos)


async def del_cloth_photo(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_photos_by_category('cloth')
    page = dialog_manager.dialog_data.get('page')
    await session.del_photo(photos[page])
    await clb.answer('Фото было успешно удаленно')


async def cloth_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_photos_by_category('cloth')
    page = dialog_manager.dialog_data.get('page')
    if page is None:
        page = 0
        dialog_manager.dialog_data['page'] = page
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if len(photos) - 1 <= page:
        not_last = False
    if not photos:
        photo = False
    elif photos[page].startswith('http'):
        photo = MediaAttachment(type=ContentType.PHOTO, url=photos[page])
    else:
        photo = MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(file_id=photos[page]))
    return {
        'media': photo,
        'model': bool(photos),
        'not_first': not_first,
        'not_last': not_last
    }


async def cloth_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(adminSG.cloth_photos)


async def get_model_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await msg.delete()
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    await session.add_photo(text, 'model')
    await dialog_manager.switch_to(adminSG.model_photos)


async def get_model_photo(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    await msg.delete()
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_photo(msg.photo[-1].file_id, 'model')
    await dialog_manager.switch_to(adminSG.model_photos)


async def model_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_photos_by_category('model')
    page = dialog_manager.dialog_data.get('page')
    if page is None:
        page = 0
        dialog_manager.dialog_data['page'] = page
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if len(photos) - 1 <= page:
        not_last = False
    if not photos:
        photo = False
    elif photos[page].startswith('http'):
        photo = MediaAttachment(type=ContentType.PHOTO, url=photos[page])
    else:
        photo = MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(file_id=photos[page]))
    return {
        'media': photo,
        'model': bool(photos),
        'not_first': not_first,
        'not_last': not_last
    }


async def del_model_photo(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_photos_by_category('model')
    page = dialog_manager.dialog_data.get('page')
    await session.del_photo(photos[page])
    await clb.answer('Фото было успешно удаленно')


async def model_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(adminSG.model_photos)


async def voucher_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    vouchers = await session.get_vouchers()
    text = ''
    for voucher in vouchers:
        text += f'{voucher.code} - {voucher.amount} генераций - {voucher.inputs} вождений\n'
    return {
        'codes': text
    }


async def get_voucher_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        amount = int(text)
    except Exception:
        await msg.answer('Введенные данные должны быть числом, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    code = dialog_manager.dialog_data.get('code')
    await session.add_voucher(code, amount)
    await dialog_manager.switch_to(adminSG.vouchers_menu)


async def get_voucher_kod(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    dialog_manager.dialog_data['code'] = text
    await dialog_manager.switch_to(adminSG.get_voucher_amount)


async def del_voucher_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    vouchers = await session.get_vouchers()
    buttons = []
    for voucher in vouchers:
        buttons.append((f'{voucher.code} - {voucher.inputs}', voucher.id))
    return {
        'items': buttons
    }


async def del_voucher(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_voucher(int(item_id))
    await clb.answer('Данный код ваучера был успешно удален')


async def del_rate(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.del_rate(rate_id)
    await clb.answer('Тариф был успешно удален')
    if clb.data.split('_')[1] == 'gen':
        await dialog_manager.switch_to(adminSG.gen_rate_menu)
    else:
        await dialog_manager.switch_to(adminSG.sub_rate_menu)


async def change_gen_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_price(rate_id, int(text))


async def change_gen_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_amount(rate_id, int(text))


async def rate_gen_change_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    rate = await session.get_rate(rate_id)
    return {'rate': f'{rate.amount} - {rate.price}'}


async def choose_gen_rate(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['rate_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.change_gen_menu)


async def rate_gen_choose_builder(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('gen')
    buttons = []
    for rate in rates:
        buttons.append((f'{rate.amount}-{rate.price}', rate.id))
    return {'items': buttons}


async def get_gen_rate_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    amount = dialog_manager.dialog_data.get('amount')
    await session.add_rate(amount, int(text), 'gen')
    dialog_manager.dialog_data.clear()
    await msg.answer('Тариф был успешно добавлен')
    await dialog_manager.switch_to(adminSG.gen_rate_menu)


async def get_gen_rate_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    dialog_manager.dialog_data['amount'] = int(text)
    await dialog_manager.switch_to(adminSG.add_gen_rate_price)


async def gen_rate_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('gen')
    text = ''
    count = 0
    for rate in rates:
        text += f'{count}: {rate.amount} - {rate.price}\n'
        count += 1
    return {'rates': text}


###################### тарифы подписок


async def change_sub_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_price(rate_id, int(text))


async def change_sub_months(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    await session.set_rate_amount(rate_id, int(text))


async def rate_sub_change_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate_id = dialog_manager.dialog_data.get('rate_id')
    rate = await session.get_rate(rate_id)
    return {'rate': f'{rate.amount} - {rate.price}'}


async def choose_sub_rate(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['rate_id'] = int(item_id)
    await dialog_manager.switch_to(adminSG.change_sub_menu)


async def rate_sub_choose_builder(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('sub')
    buttons = []
    for rate in rates:
        buttons.append((f'{rate.amount}-{rate.price}', rate.id))
    return {'items': buttons}


async def get_sub_rate_price(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    amount = dialog_manager.dialog_data.get('amount')
    await session.add_rate(amount, int(text), 'sub')
    dialog_manager.dialog_data.clear()
    await msg.answer('Тариф был успешно добавлен')
    await dialog_manager.switch_to(adminSG.sub_rate_menu)


async def get_sub_rate_months(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.isdigit():
        await msg.answer('Пожалуйста введите число')
    dialog_manager.dialog_data['amount'] = int(text)
    await dialog_manager.switch_to(adminSG.add_sub_rate_price)


async def sub_rate_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('sub')
    text = ''
    count = 0
    for rate in rates:
        text += f'{count}: {rate.amount} - {rate.price}\n'
        count += 1
    return {'rates': text}


async def deeplink_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links: list[DeeplinksTable] = await session.get_deeplinks()
    text = ''
    for link in links:
        users = await session.get_users_by_join_link(link.link)
        active = 0
        today = 0
        activity = 0
        subs = 0
        for user in users:
            if user.active:
                active += 1
            if user.entry > datetime.datetime.today() - datetime.timedelta(days=1):
                today += 1
            if user.activity > datetime.datetime.today() - datetime.timedelta(days=1):
                activity += 1
            if user.sub:
                subs += 1
        text += (f'({link.name})https://t.me/AidaLook_bot?start={link.link}: {link.entry}\nЗашло: {len(users)}'
                 f', активных: {active}, зашло сегодня: {today}, приобрели подписку: {subs}, активны в последние 24 часа: {activity}\n')
    return {'links': text}


async def get_deeplink_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_deeplink(name=text, link=get_random_id())
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_deeplink(item_id)
    await clb.answer('Ссылка была успешно удаленна')
    await dialog_manager.switch_to(adminSG.deeplink_menu)


async def del_deeplink_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    links: list[DeeplinksTable] = await session.get_deeplinks()
    buttons = []
    for link in links:
        buttons.append((f'({link.name}){link.link}: {link.entry}', link.link))
    return {'items': buttons}


async def del_admin(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.del_admin(int(item_id))
    await clb.answer('Админ был успешно удален')
    await dialog_manager.switch_to(adminSG.admin_menu)


async def admin_del_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins: list[AdminsTable] = await session.get_admins()
    buttons = []
    for admin in admins:
        buttons.append((admin.name, admin.user_id))
    return {'items': buttons}


async def refresh_url(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id: str = dialog_manager.dialog_data.get('link_id')
    dialog_manager.dialog_data.clear()
    await session.del_link(id)
    await dialog_manager.switch_to(adminSG.admin_add)


async def admin_add_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    id = get_random_id()
    dialog_manager.dialog_data['link_id'] = id
    await session.add_link(id)
    return {'id': id}


async def admin_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    admins: list[AdminsTable] = await session.get_admins()
    text = ''
    for admin in admins:
        text += f'{admin.name}\n'
    return {'admins': text}


async def get_mail(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message'] = [msg.message_id, msg.chat.id]
    await dialog_manager.switch_to(adminSG.get_time)


async def get_time(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        times = text.split(':')
        time = datetime.time(hour=int(times[0]), minute=int(times[1]))
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['time'] = [time.hour, time.minute]
    await dialog_manager.switch_to(adminSG.get_keyboard)


async def get_mail_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[tuple] = [(i.split('-')[0], i.split('-')[1]) for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['keyboard'] = keyboard
    await dialog_manager.switch_to(adminSG.confirm_mail)


async def cancel_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(adminSG.start)


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    time = dialog_manager.dialog_data.get('time')
    message = dialog_manager.dialog_data.get('message')
    keyboard = dialog_manager.dialog_data.get('keyboard')
    if keyboard:
        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in keyboard]
    users = await session.get_users()
    if not time:
        for user in users:
            try:
                await bot.copy_message(
                    chat_id=user.user_id,
                    from_chat_id=message[1],
                    message_id=message[0],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                )
                if user.active == 0:
                    await session.set_active(user.user_id, 1)
            except Exception as err:
                print(err)
                await session.set_active(user.user_id, 0)
        await clb.answer('Рассылка прошла успешно')
    else:
        today = datetime.datetime.today()
        date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time[0], minute=time[1])
        scheduler.add_job(
            func=send_messages,
            args=[bot, session, InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None, message],
            next_run_time=date
        )
    await dialog_manager.switch_to(adminSG.start)


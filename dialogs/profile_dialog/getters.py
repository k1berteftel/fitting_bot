import uuid
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select, ManagedMultiselect
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.schdulers import check_sub
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import profileSG


Configuration.account_id = 286317
Configuration.secret_key = 'live_ZWfufpazd2XRr68N5w8U6gLel2YnN4CQXFyPlJWXPN0'


async def photos_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_user_photos(event_from_user.id)
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
    else:
        photo = MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(file_id=photos[page].photo))
        dialog_manager.dialog_data['id'] = photos[page].id
    return {
        'media': photo,
        'not_first': not_first,
        'not_last': not_last
    }


async def del_photo(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photo_id = dialog_manager.dialog_data.get('id')
    await session.del_user_photo(photo_id)


async def photo_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(profileSG.photos_menu)


async def choose_sub(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = await session.get_rate(int(item_id))
    dialog_manager.dialog_data['amount'] = rate.amount
    dialog_manager.dialog_data['price'] = rate.price
    dialog_manager.dialog_data['type'] = 'sub'
    await dialog_manager.switch_to(profileSG.payment)


async def choose_sub_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('sub')
    buttons = []
    for rate in rates:
        buttons.append((f'{rate.amount} мес - {rate.price} руб', rate.id))
    return {
        'items': buttons
    }


async def choose_rate(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = await session.get_rate(int(item_id))
    dialog_manager.dialog_data['amount'] = rate.amount
    dialog_manager.dialog_data['price'] = rate.price
    dialog_manager.dialog_data['type'] = 'gen'
    await dialog_manager.switch_to(profileSG.payment)


async def generations_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates_by_category('gen')
    buttons = []
    for rate in rates:
        buttons.append((f'{rate.amount} - {rate.price} руб', rate.id))
    return {
        'items': buttons
    }


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    return {
        'username': user.username,
        'generations': user.generations,
        'sub': f' до {user.sub}' if user.sub else 'Отсутствует',
        'status': '❌' if not user.notifications else '✅'
    }


async def notifications_toggle(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    if user.notifications:
        await session.set_notifications(clb.from_user.id, False)
    else:
        await session.set_notifications(clb.from_user.id, True)


async def payment_menu_getter(dialog_manager: DialogManager, **kwargs):
    price = dialog_manager.dialog_data.get('price')
    payment = await Payment.create({
        "amount": {
            "value": str(float(price)),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/Origandtocha_bot"
        },
        "capture": True,
        "description": "Приобретение 'яблок'" if dialog_manager.dialog_data.get('type') == 'gen' else "Приобретение подписки"
    }, uuid.uuid4())
    url = payment.confirmation.confirmation_url
    dialog_manager.dialog_data['payment_id'] = payment.id
    return {
        'url': url
    }


async def check_payment(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    payment_id: PaymentResponse = dialog_manager.dialog_data.get('payment_id')
    payment: PaymentResponse = await Payment.find_one(payment_id)
    if payment.paid:
        await clb.answer('Подтверждение оплаты')
        amount = dialog_manager.dialog_data.get('amount')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        bot: Bot = dialog_manager.middleware_data.get('bot')
        if dialog_manager.dialog_data.get('type') == 'gen':
            await session.update_user_generations(clb.from_user.id, amount)
            await dialog_manager.switch_to(profileSG.generations_menu)
        else:
            await session.update_user_sub(clb.from_user.id, amount)
            if not scheduler.get_job(str(clb.from_user.id)):
                scheduler.add_job(
                    check_sub,
                    'interval',
                    args=[bot, clb.from_user.id, session, scheduler],
                    hours=24,
                    id=str(clb.from_user.id)
                )
            await dialog_manager.switch_to(profileSG.sub_menu)
    else:
        await clb.answer('Оплата еще не была произведена, пожалуйста попробуйте снова')


async def sub_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    return {
        'sub': f' до {user.sub}' if user.sub else 'Отсутствует'
    }


async def ref_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    return {
        'refs': user.refs,
        'prizes': user.generations,
        'link': f't.me/AidaLook_bot?start={user.deeplink}'
    }


async def get_voucher(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    if await session.check_voucher(msg.from_user.id, text):
        amount = await session.voucher_amount(text)
        await session.update_user_generations(msg.from_user.id, amount)
        await msg.answer(f'Код ваучера был успешно активирован, вы получили {amount} яблок')
    else:
        await msg.answer('Код ваучера неверен, пожалуйста попробуйте еще раз')


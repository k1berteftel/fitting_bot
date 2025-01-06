import datetime
import uuid
import os
from aiohttp import ClientSession
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType, FSInputFile
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select, ManagedMultiselect
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.api_methods import add_background, add_watermark
from utils.schdulers import check_sub, check_payment
from database.action_data_class import DataInteraction
from states.state_groups import profileSG


Configuration.account_id = 286317
Configuration.secret_key = 'live_ZWfufpazd2XRr68N5w8U6gLel2YnN4CQXFyPlJWXPN0'


async def info_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    texts = await session.get_texts()
    return {'text': texts.info_text}


async def get_bg_image(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    file = await bot.get_file(msg.photo[-1].file_id)
    await bot.download_file(file.file_path, f'bg_image_{msg.from_user.id}.png')
    bg_image = f'bg_image_{msg.from_user.id}.png'
    image = dialog_manager.dialog_data.get('image')
    user = await session.get_user(msg.from_user.id)
    terms = await session.get_sub_terms()
    if not image.startswith('http'):
        bot: Bot = dialog_manager.middleware_data.get('bot')
        file = await bot.get_file(image)
        await bot.download_file(file.file_path, f'image_{msg.from_user.id}.png')
    else:
        try:
            async with ClientSession(trust_env=True) as client:
                async with client.get(image) as resp:
                    image = resp.content
                    with open(f'image_{msg.from_user.id}.png', 'wb') as file:
                        file.write(await image.read())
        except Exception as err:
            print(err)
            await msg.answer('Извините, но фото в котором надо поменять фон не подлежит скачиванию, '
                             'попробуйте выбрать или загрузить другую фотографию')
            await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)
            return
    image = f'image_{msg.from_user.id}.png'
    try:
        result = await add_background(
            image=image,
            bg_image=bg_image,
            user_id=msg.from_user.id
        )
    except Exception as err:
        print(err)
        await msg.answer('Во время замены фона что-то пошло не так, '
                         'пожалуйста попробуйте еще раз или обратитесь в поддержку')
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)
        return
    if not user.sub and terms.watermark:
        image = await add_watermark(result, msg.from_user.id)
        await msg.answer_photo(photo=FSInputFile(path=image))
        try:
            os.remove(image)
        except Exception as err:
            print(err)
    else:
        await msg.answer('Ваши результаты замены фона')
        await msg.answer_photo(photo=FSInputFile(path=result))
    try:
        os.remove(result)
        os.remove(bg_image)
        os.remove(image)
    except Exception as err:
        print(err)
    price = await session.get_gen_amount()
    await session.update_user_generations(msg.from_user.id, -price)
    dialog_manager.dialog_data.clear()
    await session.add_counts_background()
    await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)


async def get_bg_image_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(msg.from_user.id)
    terms = await session.get_sub_terms()
    await msg.answer('Начался процесс замены фона, пожалуйста ожидайте')
    try:
        async with ClientSession() as client:
            async with client.get(text) as resp:
                image = resp.content
                with open(f'bg_image_{msg.from_user.id}.png', 'wb') as file:
                    file.write(await image.read())
        bg_image = f'bg_image_{msg.from_user.id}.png'
    except Exception as err:
        print(err)
        await msg.answer('Извините, но фото для замены фона не подлежит скачиванию, '
                         'попробуйте выбрать или загрузить другую фотографию')
        await dialog_manager.switch_to(profileSG.bg_photo_get, show_mode=ShowMode.DELETE_AND_SEND)
        return
    image = dialog_manager.dialog_data.get('image')
    if not image.startswith('http'):
        bot: Bot = dialog_manager.middleware_data.get('bot')
        file = await bot.get_file(image)
        await bot.download_file(file.file_path, f'image_{msg.from_user.id}.png')
    else:
        try:
            async with ClientSession(trust_env=True) as client:
                async with client.get(image) as resp:
                    image = resp.content
                    with open(f'image_{msg.from_user.id}.png', 'wb') as file:
                        file.write(await image.read())
        except Exception as err:
            print(err)
            await msg.answer('Извините, но фото в котором надо поменять фон не подлежит скачиванию, '
                             'попробуйте выбрать или загрузить другую фотографию')
            await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)
            return
    image = f'image_{msg.from_user.id}.png'
    try:
        result = await add_background(
            image=image,
            bg_image=bg_image,
            user_id=msg.from_user.id
        )
    except Exception as err:
        print(err)
        await msg.answer('Во время замены фона что-то пошло не так, '
                         'пожалуйста попробуйте еще раз или обратитесь в поддержку')
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)
        return
    if not user.sub and terms.watermark:
        image = await add_watermark(result, msg.from_user.id)
        await msg.answer_photo(photo=FSInputFile(path=image))
        try:
            os.remove(image)
        except Exception as err:
            print(err)
    else:
        await msg.answer('Ваши результаты замены фона')
        await msg.answer_photo(photo=FSInputFile(path=result))
    try:
        os.remove(result)
        os.remove(bg_image)
        os.remove(image)
    except Exception as err:
        print(err)
    price = await session.get_gen_amount()
    await session.update_user_generations(msg.from_user.id, -price)
    dialog_manager.dialog_data.clear()
    await session.add_counts_background()
    await dialog_manager.switch_to(profileSG.photos_menu, show_mode=ShowMode.DELETE_AND_SEND)


async def get_image(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(msg.from_user.id)
    price = await session.get_gen_amount()
    if user.sub and user.generations < price:
        await msg.answer('К сожалению у вас не достаточно генераций для добавления заднего фона')
        return
    terms = await session.get_sub_terms()
    if not user.sub and not terms.background:
        await msg.answer('Эта функция доступна по подписке')
        return
    if not user.sub and user.generations < price:
        await msg.answer('К сожалению не хватает генераций для примерки')
        return
    dialog_manager.dialog_data['image'] = msg.photo[-1].file_id
    await dialog_manager.switch_to(profileSG.bg_photo_get)


async def get_image_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(msg.from_user.id)
    price = await session.get_gen_amount()
    if user.sub and user.generations < price:
        await msg.answer('К сожалению у вас не достаточно генераций для добавления заднего фона')
        return
    terms = await session.get_sub_terms()
    if not user.sub and not terms.background:
        await msg.answer('Эта функция доступна по подписке')
        return
    if not user.sub and user.generations < price:
        await msg.answer('К сожалению не хватает генераций для примерки')
        return
    dialog_manager.dialog_data['image'] = text
    await dialog_manager.switch_to(profileSG.bg_photo_get)


async def get_bg_image_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    price = await session.get_gen_amount()
    if user.sub and user.generations < price:
        await clb.answer('К сожалению у вас не достаточно генераций для добавления заднего фона')
        return
    terms = await session.get_sub_terms()
    if not user.sub and not terms.background:
        await clb.answer('Эта функция доступна по подписке')
        return
    if not user.sub and user.generations < price:
        await clb.answer('К сожалению не хватает генераций для примерки')
        return
    photo_id = dialog_manager.dialog_data.get('id')
    photo = await session.get_user_photo(photo_id)
    dialog_manager.dialog_data['image'] = photo.photo
    await dialog_manager.switch_to(profileSG.bg_photo_get)


async def get_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await msg.delete()
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    await session.add_user_photo(msg.from_user.id, text)
    await dialog_manager.switch_to(profileSG.photos_menu)


async def get_photo(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    await msg.delete()
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.add_user_photo(msg.from_user.id, msg.photo[-1].file_id)
    await dialog_manager.switch_to(profileSG.photos_menu)


async def add_photo_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    photos = await session.get_user_photos(clb.from_user.id)
    if user.sub:
        terms = await session.get_sub_terms()
        if len(photos) >= terms.photos:
            await clb.answer(f'Вы можете иметь единовременно не более {terms.photos} фото моделей')
            return
    else:
        if len(photos) >= 2:
            await clb.answer('Больше фото при подписке на бота')
            return
    await dialog_manager.switch_to(profileSG.add_photo)


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
    elif not photos[page].photo.startswith('http'):
        photo = MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(file_id=photos[page].photo))
        dialog_manager.dialog_data['id'] = photos[page].id
    else:
        photo = MediaAttachment(type=ContentType.PHOTO, url=photos[page].photo)
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    sub = '❌'
    if user.sub:
        terms = await session.get_sub_terms()
        if terms.background:
            sub = '✅'
    texts = await session.get_texts()
    return {
        'text': texts.image_text,
        'sub': sub,
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
        buttons.append((f'⚡️{rate.amount} мес - {rate.price} руб', rate.id))
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
        buttons.append((f'⚡️{rate.amount} - {rate.price} руб', rate.id))
    return {
        'items': buttons
    }


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    return {
        'username': user.username,
        'generations': user.generations,
        'sub': f" до {user.sub.strftime('%d-%m-%Y')}" if user.sub else 'Отсутствует',
    }


async def close_payment(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    job = scheduler.get_job(job_id=f'payment_{clb.from_user.id}')
    if job:
        job.remove()
    await dialog_manager.switch_to(profileSG.start, show_mode=ShowMode.DELETE_AND_SEND)


async def payment_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    price = dialog_manager.dialog_data.get('price')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    type = dialog_manager.dialog_data.get('type')
    payment = await Payment.create({
        "amount": {
            "value": str(float(price)),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/AidaLook_bot"
        },
        "receipt": {
            "customer": {
                "email": "kkulis985@gmail.com"
            },
            'items': [
                {
                    'description': "Приобретение генераций" if type == 'gen' else "Приобретение подписки",
                    "amount": {
                        "value": str(float(price)),
                        "currency": "RUB"
                    },
                    'vat_code': 1,
                    'quantity': 1
                }
            ]
        },
        "capture": True,
        "description": "Приобретение генераций" if type == 'gen' else "Приобретение подписки"
    }, uuid.uuid4())
    url = payment.confirmation.confirmation_url
    scheduler.add_job(
        check_payment,
        'interval',
        args=[payment.id, event_from_user.id, bot, scheduler, session],
        kwargs={'amount': dialog_manager.dialog_data.get('amount'), 'type': type},
        id=f'payment_{event_from_user.id}',
        seconds=5
    )
    return {
        'url': url
    }


async def sub_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    texts = await session.get_texts()
    return {
        'sub': f" до {user.sub.strftime('%d-%m-%Y')}" if user.sub else 'Отсутствует',
        'text': texts.sub_text
    }


async def ref_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    texts = await session.get_texts()
    return {
        'refs': user.refs,
        'prizes': user.prizes,
        'days': user.days,
        'link': f'http://t.me/share/url?url=t.me/AidaLook_bot?start={user.deeplink}',
        'text': texts.ref_text
    }


async def get_voucher(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    if await session.check_voucher(msg.from_user.id, text):
        amount = await session.voucher_amount(text)
        await session.update_user_generations(msg.from_user.id, amount)
        await msg.answer(f'Код ваучера был успешно активирован, вы получили {amount} генераций')
    else:
        await msg.answer('Код ваучера неверен, пожалуйста попробуйте еще раз')


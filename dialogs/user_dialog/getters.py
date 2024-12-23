import os

from aiohttp import ClientSession
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType, URLInputFile, FSInputFile
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select, ManagedMultiselect
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from pathlib import Path

from utils.api_methods import concatenate_images, add_background
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import startSG


config: Config = load_config()


async def get_bg_image_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    sub = '❌'
    if user.sub:
        terms = await session.get_sub_terms()
        if terms.background:
            sub = '✅'
    return {'sub': sub}


async def start_fitting(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    price = await session.get_gen_amount()
    print(price)
    if user.generations < price:
        await clb.message.answer('К сожалению не хватает яблок для примерки')
        return
    model = dialog_manager.dialog_data.get('model')
    if not model.startswith('http'):
        model = Path(model)
    cloth = dialog_manager.dialog_data.get('cloth')
    if not cloth.startswith('http'):
        cloth = Path(cloth)
    category = dialog_manager.dialog_data.get('category')
    await clb.message.answer('Начался процесс примерки, пожалуйста ожидайте')
    try:
        result = await concatenate_images(
            cloth=cloth,
            model=model,
            category=category
        )
    except Exception as err:
        print(err)
        await clb.message.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    if not result:
        await clb.message.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    await clb.message.answer('Ваши результаты примерки')
    for photo in result:
        await clb.message.answer_photo(photo=URLInputFile(url=photo))
    if not str(model).startswith('http'):
        try:
            os.remove(model)
        except Exception as err:
            print(err)
    if not str(cloth).startswith('http'):
        try:
            os.remove(cloth)
        except Exception as err:
            print(err)
    await session.update_user_generations(clb.from_user.id, -price)
    dialog_manager.dialog_data.clear()
    await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)


async def get_bg_image(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(msg.from_user.id)
    price = await session.get_gen_amount()
    if user.sub and user.generations < 2 * price:
        await msg.answer('К сожалению у вас не достаточно яблок для примерки и добавлению заднего фона')
        return
    terms = await session.get_sub_terms()
    if not user.sub and not terms.background:
        await msg.answer('К сожалению пока что это функция доступна только юзерам с подпиской')
        return
    if not user.sub and user.generations < 2 * price:
        await msg.answer('К сожалению не хватает яблок для примерки')
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    file = await bot.get_file(msg.photo[-1].file_id)
    await bot.download_file(file.file_path, f'bg_image_{msg.from_user.id}.jpg')
    bg_image = f'bg_image_{msg.from_user.id}.jpg'
    model = dialog_manager.dialog_data.get('model')
    if not model.startswith('http'):
        model = Path(model)
    cloth = dialog_manager.dialog_data.get('cloth')
    if not cloth.startswith('http'):
        cloth = Path(cloth)
    category = dialog_manager.dialog_data.get('category')
    await msg.answer('Начался процесс примерки, пожалуйста ожидайте')
    try:
        result = await concatenate_images(
            cloth=cloth,
            model=model,
            category=category
        )
    except Exception as err:
        print(err)
        await msg.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    if not result:
        await msg.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    async with ClientSession() as client:
        async with client.get(result[0]) as resp:
            image = resp.content
            with open(f'result_{msg.from_user.id}.png', 'wb') as file:
                file.write(await image.read())
            image = f'result_{msg.from_user.id}.png'
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
        await msg.answer_photo(FSInputFile(path=image))
        dialog_manager.dialog_data.clear()
        if not str(model).startswith('http'):
            try:
                os.remove(model)
            except Exception as err:
                print(err)
        if not str(cloth).startswith('http'):
            try:
                os.remove(cloth)
            except Exception as err:
                print(err)
        try:
            os.remove(image)
            os.remove(bg_image)
        except Exception as err:
            print(err)
        await dialog_manager.switch_to(startSG.get_bg_image)
        return
    await msg.answer('Ваши результаты примерки')
    message = await msg.answer_photo(photo=FSInputFile(path=result))
    if not str(model).startswith('http'):
        try:
            os.remove(model)
        except Exception as err:
            print(err)
    if not str(cloth).startswith('http'):
        try:
            os.remove(cloth)
        except Exception as err:
            print(err)
    await session.update_user_generations(msg.from_user.id, -price)
    dialog_manager.dialog_data.clear()
    await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)


async def get_bg_image_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(msg.from_user.id)
    price = await session.get_gen_amount()
    if user.sub and user.generations < 2 * price:
        await msg.answer('К сожалению у вас не достаточно яблок для примерки и добавлению заднего фона')
        return
    terms = await session.get_sub_terms()
    if not user.sub and not terms.background:
        await msg.answer('К сожалению пока что это функция доступна только юзерам с подпиской')
        return
    if not user.sub and user.generations < 2 * price:
        await msg.answer('К сожалению не хватает яблок для примерки')
        return

    model = dialog_manager.dialog_data.get('model')
    if not model.startswith('http'):
        model = Path(model)
    cloth = dialog_manager.dialog_data.get('cloth')
    if not cloth.startswith('http'):
        cloth = Path(cloth)
    category = dialog_manager.dialog_data.get('category')
    await msg.answer('Начался процесс примерки, пожалуйста ожидайте')
    try:
        result = await concatenate_images(
            cloth=cloth,
            model=model,
            category=category
        )
    except Exception as err:
        print(err)
        await msg.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    if not result:
        await msg.answer('К сожалению во время процесса примерки что-то пошло не так, пожалуйста попробуйте еще раз')
        await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)
        return
    async with ClientSession() as client:
        try:
            async with client.get(text) as resp:
                img_data = resp.content
                with open(f'bg_image_{msg.from_user.id}.png', 'wb') as file:
                    file.write(await img_data.read())
        except Exception as err:
            print(err)
            await msg.answer('Извините, но фото для замены фона не подлежит скачиванию, '
                             'попробуйте выбрать или загрузить другую фотографию')
            await dialog_manager.switch_to(startSG.get_bg_image)
            return
        bg_image = f'bg_image_{msg.from_user.id}.png'
        async with client.get(result[0]) as resp:
            image = resp.content
            with open(f'result_{msg.from_user.id}.png', 'wb') as file:
                file.write(await image.read())
            image = f'result_{msg.from_user.id}.png'
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
        await msg.answer_photo(FSInputFile(path=image))
        dialog_manager.dialog_data.clear()
        if not str(model).startswith('http'):
            try:
                os.remove(model)
            except Exception as err:
                print(err)
        if not str(cloth).startswith('http'):
            try:
                os.remove(cloth)
            except Exception as err:
                print(err)
        try:
            os.remove(image)
            os.remove(bg_image)
        except Exception as err:
            print(err)
        await dialog_manager.switch_to(startSG.get_bg_image)
        return
    await msg.answer('Ваши результаты примерки и замены фона')
    print(result)
    message = await msg.answer_photo(photo=FSInputFile(path=result))
    if not str(model).startswith('http'):
        try:
            os.remove(model)
        except Exception as err:
            print(err)
    if not str(cloth).startswith('http'):
        try:
            os.remove(cloth)
        except Exception as err:
            print(err)
    try:
        os.remove(image)
        os.remove(bg_image)
        os.remove(result)
    except Exception as err:
        print(err)
    await session.update_user_generations(msg.from_user.id, -price)
    dialog_manager.dialog_data.clear()
    await dialog_manager.start(startSG.get_clothes, mode=StartMode.RESET_STACK)


async def get_cloth_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await msg.delete()
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['cloth'] = text
    dialog_manager.dialog_data['page'] = None
    await dialog_manager.switch_to(startSG.get_model)


async def get_cloth_photo(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    file = await bot.get_file(msg.photo[-1].file_id)
    await bot.download_file(file.file_path, f'cloth_{msg.from_user.id}.jpg')
    dialog_manager.dialog_data['cloth'] = f'cloth_{msg.from_user.id}.jpg'
    dialog_manager.dialog_data['page'] = None
    await dialog_manager.switch_to(startSG.get_model)


async def cloth_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(startSG.get_clothes)


async def choose_cloth(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    photos = await session.get_photos_by_category('cloth')
    page = dialog_manager.dialog_data.get('page')
    if not photos[page].startswith('http'):
        file = await bot.get_file(photos[page])
        await bot.download_file(file.file_path, f'cloth_{clb.from_user.id}.jpg')
        photo = f'cloth_{clb.from_user.id}.jpg'
    else:
        photo = photos[page]
    dialog_manager.dialog_data['cloth'] = photo
    dialog_manager.dialog_data['page'] = None
    await dialog_manager.switch_to(startSG.get_model)


async def cloth_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
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
    admin = False
    admins = [user.user_id for user in await session.get_admins()]
    admins.extend(config.bot.admin_ids)
    if event_from_user.id in admins:
        admin = True
    return {
        'media': photo,
        'cloth': bool(photos),
        'not_first': not_first,
        'not_last': not_last,
        'admin': admin
    }


async def get_model_link(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await msg.delete()
    if not text.startswith('http'):
        await msg.answer('Вы ввели не ссылку на фото, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['model'] = text
    await dialog_manager.switch_to(startSG.choose_category)


async def get_model_photo(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    file = await bot.get_file(msg.photo[-1].file_id)
    await bot.download_file(file.file_path, f'model_{msg.from_user.id}.jpg')
    dialog_manager.dialog_data['model'] = f'model_{msg.from_user.id}.jpg'
    await dialog_manager.switch_to(startSG.choose_category)


async def model_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(startSG.get_model)


async def choose_model(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    photos = await session.get_photos_by_category('model')
    user_photos = await session.get_user_photos(clb.from_user.id)
    photos = [photo for photo in photos]
    photos.extend([photo.photo for photo in user_photos]) if user_photos else ...
    page = dialog_manager.dialog_data.get('page')
    if not photos[page].startswith('http'):
        file = await bot.get_file(photos[page])
        await bot.download_file(file.file_path, f'model_{clb.from_user.id}.jpg')
        photo = f'model_{clb.from_user.id}.jpg'
    else:
        photo = photos[page]
    dialog_manager.dialog_data['model'] = photo
    await dialog_manager.switch_to(startSG.choose_category)


async def model_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos = await session.get_photos_by_category('model')
    user_photos = await session.get_user_photos(event_from_user.id)
    photos = [photo for photo in photos]
    photos.extend([photo.photo for photo in user_photos]) if user_photos else ...
    print(photos)
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


async def choose_category(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('high'):
        dialog_manager.dialog_data['category'] = 'tops'
    elif clb.data.startswith('low'):
        dialog_manager.dialog_data['category'] = 'bottoms'
    else:
        dialog_manager.dialog_data['category'] = 'one-pieces'
    await dialog_manager.switch_to(startSG.get_bg_image)


async def settings_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['back'] = clb.data.split('_')[0]
    await dialog_manager.switch_to(startSG.settings_menu)


async def settings_getter(dialog_manager: DialogManager, **kwargs):
    param_1 = dialog_manager.dialog_data.get('param_1')
    param_2 = dialog_manager.dialog_data.get('param_2')
    param_3 = dialog_manager.dialog_data.get('param_3')
    param_4 = dialog_manager.dialog_data.get('param_4')

    text_1 = '✅'
    text_2 = '✅'
    text_3 = '✅'
    text_4 = '✅'

    if param_1 is None:
        text_1 = '❌'
    if param_2 is None:
        text_2 = '❌'
    if param_3 is None:
        text_3 = '❌'
    if param_4 is None:
        text_4 = '❌'

    return {
        'param_1': text_1,
        'param_2': text_2,
        'param_3': text_3,
        'param_4': text_4
    }


async def on_param(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if dialog_manager.dialog_data.get(f'param_{clb.data.split("_")[0]}') is None:
        dialog_manager.dialog_data[f'param_{clb.data.split("_")[0]}'] = True
    else:
        dialog_manager.dialog_data[f'param_{clb.data.split("_")[0]}'] = None


async def back_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if dialog_manager.dialog_data.get('back') == 'cloth':
        await dialog_manager.switch_to(startSG.get_clothes)
    else:
        await dialog_manager.switch_to(startSG.get_model)

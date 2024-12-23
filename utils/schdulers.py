import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.action_data_class import DataInteraction
from dateutil.relativedelta import relativedelta


async def check_sub(bot: Bot, user_id: int, session: DataInteraction, scheduler: AsyncIOScheduler):
    user = await session.get_user(user_id)
    today = datetime.today()
    date: timedelta = user.sub - today
    if user.sub > today and date.days == 5:
        await bot.send_message(
            chat_id=user_id,
            text='До конца подписки осталось 5 дней, чтобы подписка не отключилась продлите ее '
        )
    if user.sub > today and date.days == 1:
        await bot.send_message(
            chat_id=user_id,
            text='!!! До конца подписки остался всего 1 день, чтобы продолжить безлимитно пользоваться '
                 'всеми функциями примерки бота продлите подписку'
        )
    if user.sub <= today:
        await bot.send_message(
            chat_id=user_id,
            text='К сожалению ваша подписка подошла к концу, чтобы снова пользоваться всеми'
                 ' функциями бота без ограничений приобретите подписку снова'
        )
        await session.update_user_sub(user_id, None)
        scheduler.remove_job(str(user_id))


async def send_messages(bot: Bot, session: DataInteraction, keyboard: InlineKeyboardMarkup|None, message: list[int]):
    users = await session.get_users()
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.user_id,
                from_chat_id=message[1],
                message_id=message[0],
                reply_markup=keyboard
            )
            if user.active == 0:
                await session.set_active(user.user_id, 1)
        except Exception as err:
            print(err)
            await session.set_active(user.user_id, 0)
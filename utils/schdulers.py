import asyncio
from aiogram import Bot
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse
from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import InlineKeyboardMarkup
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.action_data_class import DataInteraction
from dateutil.relativedelta import relativedelta
from states.state_groups import profileSG


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


async def check_payment(payment_id: any, user_id: int, bot: Bot, scheduler: AsyncIOScheduler,
                        session: DataInteraction, **kwargs):
    payment: PaymentResponse = await Payment.find_one(payment_id)
    if payment.paid:
        user = await session.get_user(user_id)
        amount = kwargs.get('amount')
        print(amount, kwargs.values(), kwargs.get('type'))
        if kwargs.get('type') == 'gen':
            await session.update_user_generations(user_id, amount)
            if user.referral:
                referral = await session.get_user_by_deeplink(user.referral)
                gens = int(round(amount * 0.3))
                await session.add_prizes(user.referral, gens)
                await session.update_user_generations(referral.user_id, gens)
                await bot.send_message(
                    chat_id=referral.user_id,
                    text=f'Вы получили {gens} дополнительных генераций за счет покупки вашего реферала'
                )
            return
        else:
            await session.update_user_sub(user_id, amount * 30)
            if not scheduler.get_job(job_id=str(user_id)):
                scheduler.add_job(
                    check_sub,
                    'interval',
                    args=[bot, user_id, session, scheduler],
                    hours=24,
                    id=str(user_id)
                )
            if user.referral:
                days = int(round(amount * 30 * 0.3))
                referral = await session.get_user_by_deeplink(user.referral)
                await session.update_user_sub(referral.user_id, days=days)
                await bot.send_message(
                    chat_id=referral.user_id,
                    text=f'Вы получили {days} дополнительных дней подписки за счет покупки вашего реферала'
                )
        scheduler.remove_job(job_id=f'payment_{user_id}')
    return

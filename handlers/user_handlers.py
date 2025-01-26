from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.action_data_class import DataInteraction
from states.state_groups import startSG, profileSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, scheduler: AsyncIOScheduler, command: CommandObject):
    job = scheduler.get_job(job_id=f'payment_{msg.from_user.id}')
    if job:
        job.remove()
    deeplink = None
    referral = None
    args = command.args
    if args:
        if not await session.check_user(msg.from_user.id):
            users = await session.get_users()
            user_links = [i.deeplink for i in users]
            if args in user_links:
                await session.add_refs(link=args)
                referral = args
        link_ids = await session.get_links()
        ids = [i.link for i in link_ids]
        if args in ids:
            await session.add_admin(msg.from_user.id, msg.from_user.full_name)
            await session.del_link(args)
        if not await session.check_user(msg.from_user.id):
            deeplinks = await session.get_deeplinks()
            deep_list = [i.link for i in deeplinks]
            if args in deep_list:
                deeplink = args
                await session.add_entry(args)
    await session.add_user(msg.from_user.id, msg.from_user.username if msg.from_user.username else 'Отсутствует',
                           msg.from_user.full_name, join=deeplink, referral=referral)
    await dialog_manager.start(state=startSG.get_clothes, mode=StartMode.RESET_STACK)


@user_router.callback_query(F.data.in_(['buy_generations', 'buy_sub']))
async def start_buy_gens(clb: CallbackQuery, dialog_manager: DialogManager):
    data = clb.data.split('_')
    if data[1].startswith('gen'):
        await dialog_manager.start(profileSG.generations_menu, mode=StartMode.NORMAL)
    else:
        await dialog_manager.start(profileSG.choose_sub_menu, mode=StartMode.NORMAL)


@user_router.callback_query(F.data == 'close_widget')
async def del_widget_message(clb: CallbackQuery, dialog_manager: DialogManager):
    await clb.message.delete()

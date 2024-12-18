from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from database.action_data_class import DataInteraction
from states.state_groups import startSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction, command: CommandObject):
    args = command.args
    if args:
        users = await session.get_users()
        user_links = [i.deeplink for i in users]
        if args in user_links:
            await session.add_refs(link=args)
        link_ids = await session.get_links()
        ids = [i.link for i in link_ids]
        if args in ids:
            await session.add_admin(msg.from_user.id, msg.from_user.full_name)
            await session.del_link(args)
    await session.add_user(msg.from_user.id, msg.from_user.username if msg.from_user.username else 'Отсутствует',
                           msg.from_user.full_name)
    await dialog_manager.start(state=startSG.get_clothes, mode=StartMode.RESET_STACK)

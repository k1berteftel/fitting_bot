import asyncio
import logging
import os
import inspect

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.build import PostgresBuild
from database.model import Base
from database.action_data_class import configurate_prices
from config_data.config import load_config, Config
from handlers.user_handlers import user_router
from dialogs import get_dialogs
from middlewares.transfer_middleware import TransferObjectsMiddleware
from middlewares.condition_middleware import RemindMiddleware


module_path = inspect.getfile(inspect.currentframe())
module_dir = os.path.realpath(os.path.dirname(module_path))


format = '[{asctime}] #{levelname:8} {filename}:' \
         '{lineno} - {name} - {message}'

logging.basicConfig(
    level=logging.DEBUG,
    format=format,
    style='{'
)


logger = logging.getLogger(__name__)

config: Config = load_config()


async def main():
    database = PostgresBuild(config.db.dns)
    #await database.drop_tables(Base)
    #await database.create_tables(Base)
    session = database.session()
    #await configurate_prices(session)

    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.start()

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # подключаем роутеры
    dp.include_routers(user_router, *get_dialogs())

    # подключаем middleware
    dp.update.middleware(TransferObjectsMiddleware())
    dp.update.middleware(RemindMiddleware())

    # запуск
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    logger.info('Bot start polling')

    await dp.start_polling(bot, _session=session, _scheduler=scheduler)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


# файл config_reader.py можно взять из репозитория
# пример — в первой главе
from config import config
from handlers import common, model_form


bot = Bot(config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]

    dp.include_router(common.router)
    dp.include_router(model_form.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

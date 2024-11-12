from config import config

import re

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.simple_row import make_row_keyboard


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
router = Router()

pircing = ['helix', 'industriel', 'lobe', 'tragus']


class ModelInfo(StatesGroup):
    model_name = State()
    model_phone = State()
    model_pircing = State()


@router.message(StateFilter(None), Command('start'))
async def name(message: Message, state: FSMContext):
    await message.answer(text='Привет, как тебя зовут?')
    await state.set_state(ModelInfo.model_name)


@router.message(ModelInfo.model_name)
async def phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    await message.answer(text='Супер! Напиши свой номер телефона')
    await state.set_state(ModelInfo.model_phone)


@router.message(ModelInfo.model_phone)
async def pircing(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(phone=message.text.lower())
    await message.answer(f"Все получилось! Проверь что все верно\n"
                         f"{user_data['name']} \n{message.text.lower()}")
    await bot.send_message(
            "-4516436729", 
            text= f"Новая заявка!\nИмя: {user_data['name']}\nТелефон: {message.text.lower()}"
        )
    await state.clear()

@router.message(StateFilter('ModelInfo:model_phone'))
async def incorrect_phone(message: Message, state: FSMContext):
    user_data = await state.get_data()
    re_phone = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', user_data['phone'])
    if re.match(bool()) == False:
        await message.answer(text='incorret')


async def main():  
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
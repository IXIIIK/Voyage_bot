from aiogram import Router, F
from bot import bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, BufferedInputFile

from pathlib import Path

from keyboards.simple_row import make_row_keyboard

BASE_DIR = Path(__file__).parent
image_path = BASE_DIR / "img" / "ear_pircing.jpg"

router = Router()

start_button = ["Начать"]
license = ['Да, согласен(на)', 'Нет, хочу уточнить детали']
pircing_choose = ["Прокол ушка", "Прокол лица", 'Микродермал', 'Прокол сосков']
pircing_experience = ["У меня уже есть пирсинг", "Это мой первый раз"]
ear_pircing = ["1. Мочка", "2. Хеликс", "3. Трагус", "4. Дейс", "5. Руук", "6. Конч"]
face_pircing = ["Бровь", "Крыло носа", "Септум", "Прокол губы", "Медуза", "Смайл", "Язык"]
confirm_data = ['Да, всё верно', 'Нет, хочу изменить данные (возвращение к началу)']
CONTINUE = ['Продолжить']

class ModelPircing(StatesGroup):
    start_state = State()
    info_about_model = State()
    model_pircing = State()
    pircing_choosing = State()
    place_choosing = State()     # новое состояние для выбора места прокола
    pircing_exp = State()
    confirm = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text="<b>Привет!\nЭто студия VOYAGE.</b>\n\nВ нашей студии регулярно проходит обучение пирсингу"
             "и нашим ученикам нужны модели для отработки разных видов проколов В этом боте "
             "вы сможете оставить свои данные и выбрать типы проколов, которые хотите сделать"
             "в качестве модели.\n\nПроцедура для моделей бесплатная, <u>оплачивается только выбранное</u>"
             "<u>вами украшение из ассортимента нашей студии</u>.\n\n<b><u>Все проколы выполняются под контролем топ</u></b>"
             "<b><u>мастера Якова, так что вы в надежных руках</u></b> 🧡",
        reply_markup=make_row_keyboard(start_button)
    )
    await state.set_state(ModelPircing.start_state)


@router.message(ModelPircing.start_state, F.text.in_(start_button))
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(
        text="Вы согласны с условиями участия и готовы приступить к заполнению данных?",
        reply_markup=make_row_keyboard(license)
    )
    await state.set_state(ModelPircing.info_about_model)


@router.message(ModelPircing.info_about_model, F.text == license[0])
async def model_contact(message: Message, state: FSMContext):
    await state.update_data(model_info=message.text.lower())
    await message.answer(text=f"Пожалуйста, укажите свои данные одним сообщением в формате:\n\n"
                              f"<b>ФИО\nДата рождения (дд.мм.гггг)\nВаш номер телефона</b>\n\n<i>Пример: </i>"
                              f"<i>Иванов Иван Иванович\n01.01.2000\n+7 900 123 45 67</i>", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ModelPircing.model_pircing)


@router.message(ModelPircing.info_about_model, F.text == license[1])
async def manager_contact(message: Message, state: FSMContext):
    await message.answer(text=f"<b><a href='https://t.me/voyagemoscow'>Для уточнения деталей. Напишите нашему менеджеру</a></b>", reply_markup=make_row_keyboard(CONTINUE))
    await state.set_state(ModelPircing.model_pircing)


@router.message(ModelPircing.model_pircing)
async def pircing_model(message: Message, state: FSMContext):
    await state.update_data(model_pircing=message.text.lower())
    await message.answer(text="Теперь выберите, какой прокол/ы вы хотели бы сделать в качестве модели.",
                         reply_markup=make_row_keyboard(pircing_choose))
    await state.set_state(ModelPircing.pircing_choosing)


# Выбор прокола ушка — показываем картинку и переходим к выбору места
@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[0])
async def ear_choose(message: Message, state: FSMContext):
    with open(image_path, "rb") as image_from_buffer:
        await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="ear_pircing.jpg"
            ),
            caption="Выберете место для прокола",
            reply_markup=make_row_keyboard(ear_pircing)
        )
    await state.update_data(exp_pirc=pircing_choose[0])
    await state.set_state(ModelPircing.place_choosing)  # переход в новое состояние выбора места прокола


# Выбор прокола лица — показываем клавиатуру для выбора места лица
@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[1])
async def face_choose(message: Message, state: FSMContext):
    await message.answer(text='Дополнительный выбор для проколов лица', reply_markup=make_row_keyboard(face_pircing))
    await state.update_data(exp_pirc=pircing_choose[1])
    await state.set_state(ModelPircing.place_choosing)  # переход в новое состояние выбора места прокола


# Для остальных проколов сразу переходим к опыту
@router.message(ModelPircing.pircing_choosing, F.text.in_([pircing_choose[2], pircing_choose[3]]))
async def other_pircing(message: Message, state: FSMContext):
    await state.update_data(exp_pirc=message.text.lower())
    await ask_experience(message, state)


# Новый обработчик: выбор места прокола (для уха и лица)
@router.message(ModelPircing.place_choosing, F.text.in_(ear_pircing + face_pircing))
async def place_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_place=message.text)
    await ask_experience(message, state)


# Функция для уточнения опыта
async def ask_experience(message: Message, state: FSMContext):
    await message.answer(text='Уточните пожалуйста, был ли у вас опыт в пирсинге?',
                         reply_markup=make_row_keyboard(pircing_experience))
    await state.set_state(ModelPircing.pircing_exp)


@router.message(ModelPircing.pircing_exp, F.text.in_(pircing_experience))
async def pircing_experience_chosen(message: Message, state: FSMContext):
    await state.update_data(pircing_exp=message.text)
    user_data = await state.get_data()
    name = str(user_data.get("model_pircing", "")).title()
    # Формируем строку прокола с учётом выбора места, если есть
    pierce = user_data.get('exp_pirc', '')
    place = user_data.get('chosen_place', '')
    full_pierce = f"{pierce} - {place}" if place else pierce

    await message.answer(text=f"Проверьте введённые данные и выбранные проколы. Всё ли верно?\n"
                              f"Прокол: {full_pierce}\n"
                              f"{name}",
                         reply_markup=make_row_keyboard(confirm_data))
    await state.set_state(ModelPircing.confirm)


@router.message(ModelPircing.confirm, F.text == confirm_data[0])
async def confirm_submission(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = str(user_data.get("model_pircing", "")).title()
    pierce = user_data.get('exp_pirc', '')
    pirc_experience = user_data.get('pircing_exp', '')
    place = user_data.get('chosen_place', '')
    full_pierce = f"{pierce} - {place}" if place else pierce

    await message.answer(text=f"Спасибо за вашу заявку! 🧡\n\n"
                              f"Мы свяжемся с вами, как только появится возможность для участия в обучении\n\n"
                              f"До встречи в студии VOYAGE ✨",
                         reply_markup=ReplyKeyboardRemove())

    await bot.send_message('-4516436729',
                           text=f'Новая заявка\nМодель: {name}\n\
                           Пирсинг: {full_pierce}\n\
                           Опыт в пирсинге: {pirc_experience}')
    await state.clear()


@router.message(ModelPircing.confirm, F.text == confirm_data[1])
async def change_data(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Для повторной заявки напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )

from aiogram import Router, F
import logging
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.types import BufferedInputFile
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from pathlib import Path

BASE_DIR = Path(__file__).parent
image_path = BASE_DIR / "img" / "ear_pircing.jpg"

router = Router()

# --- Button Maps ---
start_button_map = {"start_0": "Начать"}
license_map = {"license_0": "Да, согласен(на)", "license_1": "Нет, хочу уточнить детали"}
pircing_choose_map = {
    "pircing_0": "Прокол ушка",
    "pircing_1": "Прокол лица",
    "pircing_2": "Микродермал",
    "pircing_3": "Прокол сосков"
}
ear_pircing_map = {
    "ear_0": "1. Мочка",
    "ear_1": "2. Хеликс",
    "ear_2": "3. Трагус",
    "ear_3": "4. Дейс",
    "ear_4": "5. Руук",
    "ear_5": "6. Конч"
}
pircing_exp_map = {
    "exp_0": "У меня уже есть пирсинг",
    "exp_1": "Это мой первый раз"
}
confirm_map = {
    "confirm_0": "Да, всё верно",
    "confirm_1": "Нет, хочу изменить данные"
}

face_pircing_map = {
    'face_0': "Бровь",
    'face_1': "Крыло носа",
    'face_2': "Септум",
    'face_3': "Прокол губы", 
    'face_4': "Медуза", 
    'face_5': "Смайл", 
    'face_6': "Язык"
    }


def make_inline_keyboard(button_map: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=callback)]
            for callback, label in button_map.items()
        ]
    )


class ModelPircing(StatesGroup):
    start_state = State()
    info_about_model = State()
    model_pircing = State()
    pircing_choosing = State()
    place_choosing = State()
    pircing_exp = State()
    confirm = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=(
            "<b>Привет!\nЭто студия VOYAGE.</b>\n\nВ нашей студии регулярно проходит обучение пирсингу "
            "и нашим ученикам нужны модели для отработки разных видов проколов. В этом боте "
            "вы сможете оставить свои данные и выбрать типы проколов, которые хотите сделать "
            "в качестве модели.\n\nПроцедура для моделей бесплатная, <u>оплачивается только выбранное</u>"
            "<u> вами украшение из ассортимента нашей студии</u>.\n\n"
            "<b><u>Все проколы выполняются под контролем топ-мастера Якова, так что вы в надежных руках</u></b> \U0001F9A1"
        ),
        reply_markup=make_inline_keyboard(start_button_map)
    )
    await state.set_state(ModelPircing.start_state)


@router.callback_query(F.data == "start_0", StateFilter(ModelPircing.start_state))
async def accept_license(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Вы согласны с условиями участия и готовы приступить к заполнению данных?",
        reply_markup=make_inline_keyboard(license_map)
    )
    await state.set_state(ModelPircing.info_about_model)


@router.callback_query(F.data == "license_0", StateFilter(ModelPircing.info_about_model))
async def ask_contact_data(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ModelPircing.model_pircing)
    await callback.message.edit_text(
        text=(
            "Пожалуйста, укажите свои данные одним сообщением в формате:\n\n"
            "<b>ФИО\nДата рождения (дд.мм.гггг)\nВаш номер телефона</b>\n\n"
            "<i>Пример: </i><i>Иванов Иван Иванович\n01.01.2000\n+7 900 123 45 67</i>"
        )
    )


@router.callback_query(F.data == "license_1", StateFilter(ModelPircing.info_about_model))
async def redirect_to_manager(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="<b><a href='https://t.me/voyagemoscow'>Для уточнения деталей. Напишите нашему менеджеру</a></b>"
    )


@router.message(StateFilter(ModelPircing.model_pircing))
async def choose_pircing(message: Message, state: FSMContext):
    await state.update_data(model_pircing=message.text)

    # Удаляем сообщение пользователя с контактными данными
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

    # Отправляем новое сообщение с кнопками
    await message.answer(
        text="Теперь выберите, какой прокол/ы вы хотели бы сделать в качестве модели.",
        reply_markup=make_inline_keyboard(pircing_choose_map)
    )

    await state.set_state(ModelPircing.pircing_choosing)


@router.callback_query(F.data == "pircing_0")
async def choose_ear_place(callback: CallbackQuery, state: FSMContext):
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    input_file = BufferedInputFile(
        file=image_bytes,
        filename="ear_pircing.jpg"
    )

    await callback.message.answer_photo(
        photo=input_file,
        caption="Выберете место для прокола",
        reply_markup=make_inline_keyboard(ear_pircing_map)
    )

    await state.update_data(exp_pirc=pircing_choose_map['pircing_0'])
    await state.set_state(ModelPircing.place_choosing)


@router.callback_query(F.data == "pircing_1", StateFilter(ModelPircing.pircing_choosing))
async def choose_face_place(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Выберите место на лице:',
        reply_markup=make_inline_keyboard(face_pircing_map)
    )
    await state.update_data(exp_pirc=pircing_choose_map['pircing_1'])  # Сохраняем тип
    await state.set_state(ModelPircing.place_choosing)


@router.callback_query(F.data.startswith("face_"), StateFilter(ModelPircing.place_choosing))
async def face_place_chosen(callback: CallbackQuery, state: FSMContext):
    place_code = callback.data
    place_name = face_pircing_map.get(place_code, "Неизвестно")

    await state.update_data(chosen_place=place_name)
    await ask_experience(callback.message, state)


@router.callback_query(F.data.in_(pircing_choose_map.keys() - {"pircing_0"}), StateFilter(ModelPircing.pircing_choosing))
async def choose_other_pircing(callback: CallbackQuery, state: FSMContext):
    await state.update_data(exp_pirc=pircing_choose_map[callback.data])
    await ask_experience(callback.message, state)


@router.callback_query(F.data.in_(ear_pircing_map.keys()), StateFilter(ModelPircing.place_choosing))
async def place_chosen(callback: CallbackQuery, state: FSMContext):
    place_code = callback.data
    place_name = ear_pircing_map.get(place_code, "Неизвестно")
    await state.update_data(chosen_place=place_name)
    await ask_experience(callback.message, state)


@router.callback_query(F.data.in_(pircing_choose_map.keys() - {"pircing_0"}), StateFilter(ModelPircing.pircing_choosing))
async def choose_other_pircing(callback: CallbackQuery, state: FSMContext):
    await state.update_data(exp_pirc=pircing_choose_map[callback.data])
    await ask_experience(callback.message, state)

async def ask_experience(message: Message, state: FSMContext):
    await message.answer(
        text='Уточните пожалуйста, был ли у вас опыт в пирсинге?',
        reply_markup=make_inline_keyboard(pircing_exp_map)
    )
    await state.set_state(ModelPircing.pircing_exp)


@router.callback_query(F.data.in_(pircing_exp_map.keys()), StateFilter(ModelPircing.pircing_exp))
async def confirm_data_func(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pircing_exp=pircing_exp_map[callback.data])
    user_data = await state.get_data()
    name = str(user_data.get("model_pircing", "")).title()
    pierce = user_data.get('exp_pirc', '')
    place = user_data.get('chosen_place', '')
    full_pierce = f"{pierce} - {place}" if place else pierce

    await callback.message.edit_text(
        text=(
            f"Проверьте введённые данные и выбранные проколы. Всё ли верно?\n"
            f"Прокол: {full_pierce}\n"
            f"{name}"
        ),
        reply_markup=make_inline_keyboard(confirm_map)
    )
    await state.set_state(ModelPircing.confirm)


@router.callback_query(F.data == "confirm_0", StateFilter(ModelPircing.confirm))
async def confirm_submission(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    name = str(user_data.get("model_pircing", "")).title()
    pierce = user_data.get('exp_pirc', '')
    pirc_experience = user_data.get('pircing_exp', '')
    place = user_data.get('chosen_place', '')
    full_pierce = f"{pierce} - {place}" if place else pierce

    await callback.message.edit_text(
        text=(
            "Спасибо за вашу заявку! \U0001F9A1\n\n"
            "Мы свяжемся с вами, как только появится возможность для участия в обучении\n\n"
            "До встречи в студии VOYAGE ✨"
        )
    )

    admin_chat_id = -4516436729
    await callback.bot.send_message(
        admin_chat_id,
        text=f'Новая заявка\nМодель: {name}\nПирсинг: {full_pierce}\nОпыт в пирсинге: {pirc_experience}'
    )
    await state.clear()


@router.callback_query(F.data == "confirm_1", StateFilter(ModelPircing.confirm))
async def change_data(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="Для повторной заявки напишите /start"
    )
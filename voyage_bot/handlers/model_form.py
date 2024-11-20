from aiogram import Router, F, types
from bot import bot, dp
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, URLInputFile, BufferedInputFile

from keyboards.simple_row import make_row_keyboard

router = Router()


# Эти значения далее будут подставляться в итоговый текст, отсюда
# такая на первый взгляд странная форма прилагательных
start_button = ["Начать"]
license = ['Да, согласен(на)', " Нет, хочу уточнить детали (переход на контакт для связи)"]
pircing_choose = ["Прокол ушка", "Прокол лица", 'Микродермал', 'Прокол сосков']
pircing_experience = [" У меня уже есть пирсинг", "Это мой первый раз"]
ear_pircing = ["1. Мочка", "2. Хеликс", "3. Трагус", "4. Дейс", "5. Руук", "6. Конч"]
face_pircing = ["Бровь", "Крыло носа", "Септум", "Прокол губы", "Медуза", "Смайл", "Язык"]
confirm_data = ['Да, всё верно', 'Нет, хочу изменить данные (возвращение к началу)']


class ModelPircing(StatesGroup):
    info_about_model = State()
    model_pircing = State()
    pircing_choosing = State()
    start_state = State()
    pircing_exp = State()
    all_data = State()
    confirm = State()


@router.message(Command("start"))
#@dp.message(content_types=['new_chat_members'])
async def cmd_food(message: Message, state: FSMContext):

    await message.answer(
        text="Привет! Это студия VOYAGE. В нашей студии регулярно проходит обучение пирсингу и нашим ученикам нужны модели для отработки разных видов проколов В этом боте вы сможете оставить свои данные и выбрать типы проколов, которые хотите сделать в качестве модели. Процедура для моделей бесплатная, оплачивается только выбранное вами украшение из ассортимента нашей студии. Все проколы выполняются под контролем топ мастера Якова, так что вы в надежных руках 🧡",
        reply_markup=make_row_keyboard(start_button)
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(ModelPircing.start_state)

# Этап выбора блюда #


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
    await message.answer(text='Пожалуйста, укажите свои данные одним сообщением в формате: ФИО, дата рождения (дд.мм.гггг), номер телефона.”\n• Пример: “Иванов Иван Иванович, 01.01.2000, +7 900 123 45 67.”', reply_markup=ReplyKeyboardRemove())
    await state.set_state(ModelPircing.model_pircing)


@router.message(ModelPircing.model_pircing)
async def pircing_model(message: Message, state: FSMContext):
    await state.update_data(model_pircing=message.text.lower())
    await message.answer(text="Теперь выберите, какой прокол/ы вы хотели бы сделать в качестве модели.",
                         reply_markup=make_row_keyboard(pircing_choose))
    await state.set_state(ModelPircing.pircing_choosing)
    

@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[0])
async def ear_choose(message: Message, state: FSMContext):
    file_ids = []
    ear_photo = FSInputFile("img/ear_pircing.jpg")
    await state.update_data(ear_pircing=message.text.lower())
    result = await message.answer_photo(
        ear_photo,
        caption="Выберете место для прокола",
        reply_markup=make_row_keyboard(ear_pircing)
    )
    file_ids.append(result.photo[-1].file_id)
    await state.set_state(ModelPircing.pircing_exp)


@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[1])
async def face_choose(message: Message, state: FSMContext):
    await state.update_data(face_pircing=message.text.lower())
    await message.answer(text='Дополнительный выбор для проколов лица', reply_markup=make_row_keyboard(face_pircing))
    await state.set_state(ModelPircing.pircing_exp)



@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[2])
async def exp_pirc(message: Message, state: FSMContext):
    await state.update_data(exp_pirc=message.text.lower())
    await state.set_state(ModelPircing.pircing_exp)


@router.message(ModelPircing.pircing_choosing, F.text == pircing_choose[3])
async def exp_pirc(message: Message, state: FSMContext):
    await state.update_data(exp_pirc=message.text.lower())
    await state.set_state(ModelPircing.pircing_exp)


@router.message(ModelPircing.pircing_exp)
async def exp_pirc(message: Message, state: FSMContext):
    await state.update_data(exp_pirc=message.text.lower())
    await message.answer(text='Уточните пожалуйста, был ли у вас опыт в пирсинге?',
                         reply_markup=make_row_keyboard(pircing_experience))
    await state.set_state(ModelPircing.all_data)


@router.message(ModelPircing.all_data)
async def correct_data(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = str(user_data["model_pircing"]).title()
    model_pircing = str(user_data['exp_pirc'])[2:]

    await message.answer(text=f'Проверьте введённые данные и выбранные проколы. Всё ли верно?\n'
                            f"{model_pircing}\n"
                            f"{name}", reply_markup=make_row_keyboard(confirm_data))
    await state.set_state(ModelPircing.confirm)



@router.message(ModelPircing.confirm, F.text == confirm_data[0])
async def exp_pirc(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = str(user_data["model_pircing"]).title()
    model_pircing = str(user_data['exp_pirc'])[2:]

    await message.answer(text='Спасибо за вашу заявку! Мы свяжемся с вами, как только появится возможность для участия в обучении. До встречи в студии VOYAGE!',
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_message('-4516436729',
                           text=f'Новая заявка\nМодель: {name}\nПирсинг: {model_pircing}')
    await state.set_state(ModelPircing.all_data)
    await state.clear()


@router.message(ModelPircing.confirm, F.text == confirm_data[1])
async def exp_pirc(message: Message, state: FSMContext):
    await state.set_state(ModelPircing.start_state)
    await state.clear()







# В целом, никто не мешает указывать стейты полностью строками
# Это может пригодиться, если по какой-то причине 
# ваши названия стейтов генерируются в рантайме (но зачем?)
@router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда.\n\n"
             "Пожалуйста, выберите одно из названий из списка ниже:",
        reply_markup=ReplyKeyboardRemove()
    )

# Этап выбора размера порции и отображение сводной информации #


# @router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
# async def food_size_chosen(message: Message, state: FSMContext):
#     user_data = await state.get_data()
#     await message.answer(
#         text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
#              f"Попробуйте теперь заказать напитки: /drinks",
#         reply_markup=ReplyKeyboardRemove()
#     )
#     # Сброс состояния и сохранённых данных у пользователя
#     await state.clear()


# @router.message(OrderFood.choosing_food_size)
# async def food_size_chosen_incorrectly(message: Message):
#     await message.answer(
#         text="Я не знаю такого размера порции.\n\n"
#              "Пожалуйста, выберите один из вариантов из списка ниже:",
#         reply_markup=make_row_keyboard(available_food_sizes)
#     )
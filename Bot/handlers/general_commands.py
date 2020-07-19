from aiogram import types
from aiogram.dispatcher.filters import Text

from Bot.misc import dp, bd

# создаем клавиатуры

main_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Профиль'),
            types.KeyboardButton(text='Поиск')
        ],
    ],
    resize_keyboard=True
)

main_menu_admin = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Профиль'),
        ],
        [
            types.KeyboardButton(text='Поиск'),
        ],
        [
            types.KeyboardButton(text='Панель Админа')
        ]
    ],
    resize_keyboard=True
)

search_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Поиск по категориям')
        ],
        [
            types.KeyboardButton(text='Поиск по ингредиентам')
        ],
        [
            types.KeyboardButton(text='Поиск по названию')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)

search_by_name = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Хочу найти рецепты с названием...')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)

search_by_categories = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Хочу найти рецепты с категорией...')
        ],
        [
            types.KeyboardButton(text='Показать все категории')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)

search_by_ingredients = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Точный поиск..')
        ],
        [
            types.KeyboardButton(text='Поиск блюд с ингридиентом...')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)
profile_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Избранное'),
            types.KeyboardButton(text='История')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)

admin_action = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Статистика по новым пользователям'),
            types.KeyboardButton(text='Статистика по активным')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)


# Прописываем все основные команды и переходы

@dp.message_handler(commands=["start"], state='*')
async def start_bot(message: types.Message):
    bd.bot_add_user(message.from_user.id, message.from_user.username)

    msg = f"Приветствуем в нашем боте {message.from_user.first_name}\nМы поможем тебе найти рецептики"
    if bd.bot_check_is_admin(message.from_user.id):
        await message.answer(
            msg, reply_markup=main_menu_admin)
    else:
        await message.answer(
            msg, reply_markup=main_menu)


@dp.message_handler(Text(equals='Вернуться'), state='*')
async def back(message: types.Message):
    if bd.bot_check_is_admin(message.from_user.id):
        await message.answer(f'Привет администратор, {message.from_user.full_name}', reply_markup=main_menu_admin)
    else:
        await message.answer(f"Вы вернулись", reply_markup=main_menu)


@dp.message_handler(Text(equals='Поиск'), state='*')
async def choose_search_type(msg: types.Message):
    await msg.answer(f'Вы перешли в {msg.text}', reply_markup=search_menu)


@dp.message_handler(Text(equals='Поиск по категориям'), state='*')
async def choose_search_type_categories(msg: types.Message):
    await msg.answer('Если  вы хотите начать поиск - сначала нажмите кнопку, потом введите текст',
                     reply_markup=search_by_categories)


@dp.message_handler(Text(equals='Поиск по ингредиентам'), state='*')
async def choose_search_type(msg: types.Message):
    await msg.answer(f'Выберите точность с который будет найден рецепт',
                     reply_markup=search_by_ingredients)


@dp.message_handler(Text(equals='Поиск по названию'), state='*')
async def choose_search_type_name(msg: types.Message):
    await msg.answer('Нажмите кнопку и введите название интересующего вас рецепта', reply_markup=search_by_name)


@dp.message_handler(Text(equals='Профиль'), state='*')
async def choose_search_type_name(msg: types.Message):
    await msg.answer('Что вы хотите посмотреть?', reply_markup=profile_menu)


@dp.message_handler(Text(equals='История'), state='*')
async def choose_search_type_name(msg: types.Message):
    history = bd.bot_get_history(msg.from_user.id)
    text = ""
    b = 0
    for i, story in enumerate(history):
        text += f'{i + 1}. {story[4]}  вы искали рецепт по {story[3]} {story[2]} {story[1]}\n'.replace("None", "")
    await msg.answer(text)


@dp.message_handler(Text(equals='Панель Админа'), state='*')
async def choose_admin_action(msg: types.Message):
    if bd.bot_check_is_admin(msg.from_user.id):
        await msg.answer('Доступ администратора', reply_markup=admin_action)
    else:
        await msg.answer('доступ закрыт', reply_markup=main_menu)

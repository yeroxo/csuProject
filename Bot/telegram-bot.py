import logging

from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import callback_data

from Bot import config
from aiogram import Bot, Dispatcher, executor, types
from Db.LogicalPart import LogicalPart as DataBase

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализация бд
bd = DataBase()

# иницилизируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

main_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Профиль'),
        ],
        [
            types.KeyboardButton(text='Поиск'),
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
            types.KeyboardButton(text='Поиск по ингредиентам'),
        ],
        [
            types.KeyboardButton(text='Поиск по по категориям'),
        ],
        [
            types.KeyboardButton(text='Поиск по названию'),
        ],
        [
            types.KeyboardButton(text='Вернуться'),
        ],
    ],
    resize_keyboard=True
)

search_menu_categories = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Начать поиск'),
            types.KeyboardButton(text='Показать все категории'),
        ],
        [
            types.KeyboardButton(text='Вернуться'),
        ],
    ],
    resize_keyboard=True
)
ss = types.InlineKeyboardButton("Первая кнопка", callback_data="button1")
page_inline_buttons = types.InlineKeyboardMarkup().add(ss)

profile_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Избранное'),
            types.KeyboardButton(text='История поисков'),
        ],
        [
            types.KeyboardButton(text='Вернуться'),
        ],
    ],
    resize_keyboard=True
)

hzchto = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='ku', callback_data="button1")
        ]
    ],
)


#            types.KeyboardButton(text='Избранное'),
#            types.KeyboardButton(text='История поисков'),
# клава

@dp.message_handler(Command("start"))
async def start_bot(message: types.Message):
    bd.bot_add_user(message.from_user.id, message.from_user.username)
    if bd.bot_check_is_admin(message.from_user.id):
        await message.answer(
            f"Приветствуем в нашем боте {message.from_user.first_name}\nМы поможем тебе найти рецептики",
            reply_markup=main_menu_admin)
    else:
        await message.answer(
            f"Приветствуем в нашем боте {message.from_user.first_name}\nМы поможем тебе найти рецептики",
            reply_markup=main_menu)


@dp.message_handler(Text(equals='История поисков'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='Избранное'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='Поиск'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=search_menu)


@dp.message_handler(Text(equals='Профиль'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=profile_menu)


@dp.message_handler(Text(equals='Поиск по по категориям'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=search_menu_categories)


@dp.message_handler(Text(equals='Вернуться'))
async def get_food(message: types.Message):
    await message.answer(f"Вы вернулись", reply_markup=main_menu)


# пример для будущего перелистывания страниц
@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_handler(callback_query: types.CallbackQuery):
    if callback_query.data == 'button1':
        await bot.send_message(callback_query.from_user.id, "Нажата первая кнопка")


inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


@dp.message_handler(Text(equals='Начать поиск'))
async def get_search(msg: types.Message):
    a = bd.bot_find_recipes(msg.from_user.id, -1, "молоко")
    await msg.answer(a, reply_markup=hzchto)


if __name__ == '__main__':
    executor.start_polling(dp)

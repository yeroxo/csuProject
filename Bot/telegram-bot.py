import logging

from aiogram.dispatcher.filters import Command, Text

from Bot import config
from aiogram import Bot, Dispatcher, executor, types

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# иницилизируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

main_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Профиль'),
            types.KeyboardButton(text='История поисков'),
        ],
        [
            types.KeyboardButton(text='Избранное'),
            types.KeyboardButton(text='Поиск'),
        ],
    ],
    resize_keyboard=True
)

search_menu = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='поиск по ингридеентам'),
            types.KeyboardButton(text='поиск по по категориям'),
            types.KeyboardButton(text='показать все категории'),
        ],
        [
            types.KeyboardButton(text='Вернуться'),
        ],
    ],
    resize_keyboard=True
)


# клава

@dp.message_handler(Command("start"))
async def show_menu(message: types.Message):
    await message.answer('Приветствуем в нашем боте\nМы поможем тебе найти рецептики', reply_markup=main_menu)


@dp.message_handler(Text(equals='Профиль'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='История поисков'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='Избранное'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='Поиск'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=search_menu)


@dp.message_handler(Text(equals='Вернуться'))
async def get_food(message: types.Message):
    await message.answer(f"Вы вернулись", reply_markup=main_menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

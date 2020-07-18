import logging
import urllib3
from urllib.parse import quote

from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from Bot import config
from aiogram import Bot, Dispatcher, executor, types
from Db.LogicalPart import LogicalPart as DataBase

from model.recipe import Recipe


# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализация бд
bd = DataBase()

# иницилизируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

recipe_cb = CallbackData('recipe', 'recipe_id', 'start_indx', 'action')
menu_cb = CallbackData('menu_type', 'action')

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
            types.KeyboardButton(text='Хочу найти...'),
            types.KeyboardButton(text='Показать все категории'),
        ],
        [
            types.KeyboardButton(text='Вернуться'),
        ],
    ],
    resize_keyboard=True
)

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


def get_reply_fmt(recipe_list, start_indx=0):
    if isinstance(start_indx, str):
        start_indx = int(start_indx)
    if start_indx < 0:
        start_indx = 0
    markup = types.InlineKeyboardMarkup()
    reply_msg = ''
    # markup_list = []  # для отображения в строку
    for i, recipe in enumerate(recipe_list[start_indx:start_indx + 10]):
        reply_msg += f'{i + 1}. {recipe.name}\n'
        # markup_list.append(  # для отображения в строку
        markup.add(
            types.InlineKeyboardButton(
                f'{i+1}',
                callback_data=recipe_cb.new(recipe_id=recipe.id, start_indx=start_indx, action='view')),
        )
    # markup.row(*markup_list)  # для отображения в строку
    if start_indx > 0:
        markup.add(types.InlineKeyboardButton(
                f'Previous page',
                callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx-10, action='list')))
    if start_indx+10 < len(recipe_list):
        markup.add(types.InlineKeyboardButton(
                f'Next page',
                callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx+10, action='list')))
    return {'markup': markup, 'msg': reply_msg.replace("\'", "")}


def format_recipe(recipe_id: str, start_indx: str, recipe: Recipe, user_id) -> (str, types.InlineKeyboardMarkup):
    text = f"ID: {recipe.id}\nTitle: {recipe.name}"
    favourites = bd.bot_get_favourites(user_id)
    is_favourite = False
    if favourites:
        for favourite in favourites:
            if int(recipe.id) == favourite[0]:
                is_favourite = True
                break
    markup = types.InlineKeyboardMarkup()
    if is_favourite:
        markup.add(
            types.InlineKeyboardButton('★', callback_data=recipe_cb.new(recipe_id=recipe_id, start_indx=start_indx, action='unfavourite'))
        )
    else:
        markup.add(
            types.InlineKeyboardButton('☆', callback_data=recipe_cb.new(recipe_id=recipe_id, start_indx=start_indx, action='favourite'))
        )
    link = recipe.link
    if 'https' in link:
        link = link[9:]
    elif 'http' in link:
        link = link[8:]

    markup.add(
        types.InlineKeyboardButton('Открыть на сайте', url=link)
    )
    markup.add(types.InlineKeyboardButton('<< Back', callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx, action='list')))
    return text, markup


@dp.message_handler(Command("start"))
async def start_bot(message: types.Message):
    bd.bot_add_user(message.from_user.id, message.from_user.username)

    msg = f"Приветствуем в нашем боте {message.from_user.first_name}\nМы поможем тебе найти рецептики"
    if bd.bot_check_is_admin(message.from_user.id):
        await message.answer(
            msg, reply_markup=main_menu_admin)
    else:
        await message.answer(
            msg, reply_markup=main_menu)


# @dp.message_handler(Text(equals='История поисков'))
# async def get_food(message: types.Message):
#     await message.answer("")


@dp.message_handler(Text(equals='История поисков'))
async def get_food(message: types.Message):
    await message.answer("")


@dp.message_handler(Text(equals='Избранное'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}")


@dp.message_handler(Text(equals='Поиск'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=search_menu)


@dp.message_handler(Text(equals='Профиль'))
async def get_food(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=profile_menu)


@dp.message_handler(Text(equals=['Поиск по ингредиентам', 'Поиск по по категориям', 'Поиск по названию']))
async def get_search(message: types.Message):
    await message.answer(f"Вы выбрали {message.text}", reply_markup=search_menu_categories)


@dp.message_handler(Text(equals='Вернуться'))
async def back(message: types.Message):
    await message.answer(f"Вы вернулись", reply_markup=main_menu)


@dp.message_handler(Text(equals='Хочу найти...'))
async def search(msg_search_type: types.Message):
    @dp.message_handler()
    async def user_answer_handler(msg_for_search: types.Message):
        recipes = bd.bot_find_recipes_by_categories(msg_for_search.from_user.id, msg_for_search.text)
        reply_fmt = get_reply_fmt(recipes)
        if len(recipes) <= 0:
            await bot.send_message(msg_for_search.chat.id, 'Не могу найти ничего по вашему запросу')
        else:
            await msg_for_search.answer(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

        @dp.callback_query_handler(recipe_cb.filter(action='list'))
        async def query_show_list(query: types.CallbackQuery, callback_data: dict):
            history_recipe = bd.bot_get_history(msg_for_search.from_user.id)[-1]
            last_recipes = bd.bot_find_recipes_by_categories(msg_for_search.from_user.id, history_recipe[2])
            reply_fmt = get_reply_fmt(last_recipes, callback_data['start_indx'])
            await query.message.edit_text(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

        @dp.callback_query_handler(recipe_cb.filter(action='view'))
        async def query_view(query: types.CallbackQuery, callback_data: dict):
            recipe_id = callback_data['recipe_id']
            recipe = bd.make_recipe_object(recipe_id)
            text, markup = format_recipe(recipe_id, callback_data['start_indx'], recipe, msg_for_search.from_user.id)
            await query.message.edit_text(text, reply_markup=markup)

        @dp.callback_query_handler(recipe_cb.filter(action=['unfavourite', 'favourite']))
        async def query_change_fav(query: types.CallbackQuery, callback_data: dict):
            recipe_id = callback_data['id']
            if callback_data['action'] == 'favourite':
                bd.bot_add_favourite(msg_for_search.from_user.id, recipe_id)
                suffix = '\n(Your favourite)'
                await query.answer('Added to favourite')
            else:
                bd.bot_delete_favourite(msg_for_search.from_user.id, recipe_id)
                suffix = ''
                await query.answer('Deleted from favourites')
            recipe = bd.make_recipe_object(recipe_id)
            text, markup = format_recipe(recipe_id, callback_data['start_indx'], recipe, msg_for_search.from_user.id)
            await query.message.edit_text(text+suffix, reply_markup=markup)


if __name__ == '__main__':
    executor.start_polling(dp)

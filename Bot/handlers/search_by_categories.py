from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from Bot.misc import bd, dp, bot
from model.recipe import Recipe

recipe_cb = CallbackData('recipe', 'recipe_id', 'start_indx', 'action')
menu_cb = CallbackData('menu_type', 'action')


class SearchByCategories(StatesGroup):
    waiting_for_user_answer = State()
    waiting_for_user_view = State()


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
                f'{i + 1}',
                callback_data=recipe_cb.new(recipe_id=recipe.id, start_indx=start_indx, action='view')),
        )
    # markup.row(*markup_list)  # для отображения в строку
    if start_indx > 0:
        markup.add(types.InlineKeyboardButton(
            f'Previous page',
            callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx - 10, action='list')))
    if start_indx + 10 < len(recipe_list):
        markup.add(types.InlineKeyboardButton(
            f'Next page',
            callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx + 10, action='list')))
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
            types.InlineKeyboardButton('★', callback_data=recipe_cb.new(recipe_id=recipe_id, start_indx=start_indx,
                                                                        action='unfavourite'))
        )
    else:
        markup.add(
            types.InlineKeyboardButton('☆', callback_data=recipe_cb.new(recipe_id=recipe_id, start_indx=start_indx,
                                                                        action='favourite'))
        )
    link = recipe.link
    if 'https' in link:
        link = link[9:]
    elif 'http' in link:
        link = link[8:]

    markup.add(
        types.InlineKeyboardButton('Открыть на сайте', url=link)
    )
    markup.add(types.InlineKeyboardButton('<< Back', callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx,
                                                                                 action='list')))
    return text, markup


@dp.message_handler(Text(equals='Хочу найти рецепты с категорией...'), state="*")
async def search_categories(msg_search_type: types.Message):
    await SearchByCategories.waiting_for_user_answer.set()

    @dp.message_handler(state=SearchByCategories.waiting_for_user_answer)
    async def user_answer_handler(msg_for_search: types.Message):
        recipes = bd.bot_find_recipes_by_categories(msg_for_search.from_user.id, msg_for_search.text)
        reply_fmt = get_reply_fmt(recipes)
        if len(recipes) <= 0:
            await bot.send_message(msg_for_search.chat.id, 'Не могу найти ничего по вашему запросу')
        else:
            await msg_for_search.answer(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

        await SearchByCategories.next()

        @dp.callback_query_handler(recipe_cb.filter(action='list'), state=SearchByCategories.waiting_for_user_view)
        async def query_show_list(query: types.CallbackQuery, callback_data: dict):
            history_recipe = bd.bot_get_history(msg_for_search.from_user.id)[-1]
            last_recipes = bd.bot_find_recipes_by_categories(msg_for_search.from_user.id, history_recipe[3])
            reply_fmt = get_reply_fmt(last_recipes, callback_data['start_indx'])
            await query.message.edit_text(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

        @dp.callback_query_handler(recipe_cb.filter(action='view'), state=SearchByCategories.waiting_for_user_view)
        async def query_view(query: types.CallbackQuery, callback_data: dict):
            recipe_id = callback_data['recipe_id']
            recipe = bd.make_recipe_object(recipe_id)
            text, markup = format_recipe(recipe_id, callback_data['start_indx'], recipe, msg_for_search.from_user.id)
            await query.message.edit_text(text, reply_markup=markup)

        @dp.callback_query_handler(recipe_cb.filter(action=['unfavourite', 'favourite']),
                                   state=SearchByCategories.waiting_for_user_view)
        async def query_change_fav(query: types.CallbackQuery, callback_data: dict):
            recipe_id = callback_data['recipe_id']
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
            await query.message.edit_text(text + suffix, reply_markup=markup)


@dp.message_handler(Text(equals='Показать все категории'), state="*")
async def search_categories(msg_search_type: types.Message):
    all_categories = bd.bot_get_categories()
    text = ""
    for i, category in enumerate(all_categories):
        text += f'{i + 1} {category[1]}\n'
    await msg_search_type.answer(text)

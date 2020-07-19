import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from Bot.handlers.inline_methods import get_reply_fmt, recipe_cb, format_recipe, query_handler_view
from Bot.misc import bd, dp, bot
from model.recipe import Recipe


class ShowFavourites(StatesGroup):
    waiting_for_user_view = State()


@dp.message_handler(Text(equals='Избранное'),state="*")
async def search_names_by_name(msg_search_type: types.Message):
    favourites = bd.bot_get_favourites(msg_search_type.from_user.id)
    reply_fmt = get_reply_fmt(favourites)
    if len(favourites) <= 0:
        await bot.send_message(msg_search_type.chat.id, 'Список избранного пуст')
    else:
        await msg_search_type.answer(reply_fmt['msg'], reply_markup=reply_fmt['markup'])
    await ShowFavourites.waiting_for_user_view.set()

    @dp.callback_query_handler(recipe_cb.filter(action='list'), state=ShowFavourites.waiting_for_user_view)
    async def query_show_list_by_name(query: types.CallbackQuery, callback_data: dict):
        history_recipe = bd.bot_get_history(msg_search_type.from_user.id)[0]
        last_recipes = bd.bot_find_recipes_by_name(msg_search_type.from_user.id, history_recipe[1])
        reply_fmt = get_reply_fmt(last_recipes, callback_data['start_indx'])
        await query.message.edit_text(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

    @dp.callback_query_handler(recipe_cb.filter(action='view'), state=ShowFavourites.waiting_for_user_view)
    async def query_view_by_name(query: types.CallbackQuery, callback_data: dict):
        data = query_handler_view(msg_search_type, callback_data)
        await query.message.answer_photo(open(data[2], 'rb'))
        os.remove(data[2])
        await query.message.answer_photo(data[0], reply_markup=data[1])


    @dp.callback_query_handler(recipe_cb.filter(action=['unfavourite', 'favourite']),
                               state=ShowFavourites.waiting_for_user_view)
    async def query_change_fav_by_name(query: types.CallbackQuery, callback_data: dict):
        recipe_id = callback_data['recipe_id']
        if callback_data['action'] == 'favourite':
            bd.bot_add_favourite(msg_search_type.from_user.id, recipe_id)
            suffix = '\n(Your favourite)'
            await query.answer('Added to favourite')
        else:
            bd.bot_delete_favourite(msg_search_type.from_user.id, recipe_id)
            suffix = ''
            await query.answer('Deleted from favourites')
        recipe = bd.make_recipe_object(recipe_id)
        text, markup,photo = format_recipe(recipe_id, callback_data['start_indx'], recipe, msg_search_type.from_user.id)
        await query.message.edit_text(text + suffix, reply_markup=markup)
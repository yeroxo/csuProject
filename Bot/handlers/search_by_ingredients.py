import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from Bot.handlers.inline_methods import get_reply_fmt, format_recipe, recipe_cb, query_handler_view
from Bot.misc import bd, dp, bot
from model.recipe import Recipe


class SearchByIngredients(StatesGroup):
    waiting_for_user_answer = State()
    waiting_for_user_view = State()


@dp.message_handler(Text(equals=['Точный поиск..', 'Поиск блюд с ингридиентом...']),
                    state="*")
async def search_ingredients(msg_search_type: types.Message, state: FSMContext):
    if msg_search_type.text == 'Точный поиск..':
        await state.update_data(diff=0)
    elif msg_search_type.text == 'Поиск блюд с ингридиентом...':
        await state.update_data(diff=-1)

    await msg_search_type.answer('Введите список продуктов через запятую')
    await SearchByIngredients.waiting_for_user_answer.set()

    @dp.message_handler(state=SearchByIngredients.waiting_for_user_answer)
    async def user_answer_handler_by_ingredients(msg_for_search: types.Message):
        diff = await state.get_data()
        recipes = bd.bot_find_recipes_by_ingredients(msg_for_search.from_user.id, msg_for_search.text.lower(),
                                                     diff['diff'])
        reply_fmt = get_reply_fmt(recipes)
        if len(recipes) <= 0:
            await bot.send_message(msg_for_search.chat.id, 'Не могу найти ничего по вашему запросу')
        else:
            await msg_for_search.answer(reply_fmt['msg'], reply_markup=reply_fmt['markup'])
        await SearchByIngredients.next()

        @dp.callback_query_handler(recipe_cb.filter(action='list'), state=SearchByIngredients.waiting_for_user_view)
        async def query_show_list_by_ingredients(query: types.CallbackQuery, callback_data: dict):
            diff = await state.get_data()
            history_recipe = bd.bot_get_history(msg_for_search.from_user.id)[0]
            last_recipes = bd.bot_find_recipes_by_ingredients(msg_for_search.from_user.id, history_recipe[2].lower(),
                                                              diff['diff'])
            reply_fmt = get_reply_fmt(last_recipes, callback_data['start_indx'])
            await query.message.edit_text(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

        @dp.callback_query_handler(recipe_cb.filter(action='view'), state=SearchByIngredients.waiting_for_user_view)
        async def query_view_by_ingredients(query: types.CallbackQuery, callback_data: dict,state:FSMContext):
            data = query_handler_view(msg_for_search, callback_data)

            await query.message.answer_photo(open(data[2],'rb'))
            os.remove(data[2])
            await query.message.answer(data[0], reply_markup=data[1])

        @dp.callback_query_handler(recipe_cb.filter(action=['unfavourite', 'favourite']),
                                   state=SearchByIngredients.waiting_for_user_view)
        async def query_change_fav_by_ingredients(query: types.CallbackQuery, callback_data: dict):
            recipe_id = callback_data['recipe_id']
            if callback_data['action'] == 'favourite':
                bd.bot_add_favourite(msg_for_search.from_user.id, recipe_id)
                suffix = '\n(Your favourite)'
                await query.message.edit_text('Added to favourite')
            else:
                bd.bot_delete_favourite(msg_for_search.from_user.id, recipe_id)
                suffix = ''
                await query.message.edit_text('Deleted from favourites')
            recipe = bd.make_recipe_object(recipe_id)
            text, markup,photo = format_recipe(recipe_id, callback_data['start_indx'], recipe,
                                         msg_for_search.from_user.id)
            await query.message.edit_text(text + suffix, reply_markup=markup)

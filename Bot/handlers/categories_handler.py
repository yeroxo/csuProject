from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from Bot.misc import bd, dp, bot
from model.recipe import Recipe

recipe_cb = CallbackData('recipe', 'recipe_id', 'start_indx', 'action')


class ShowCategoriesList(StatesGroup):
    start_listing = State()


def get_reply_fmt(recipe_list, start_indx=0):
    if isinstance(start_indx, str):
        start_indx = int(start_indx)
    if start_indx < 0:
        start_indx = 0
    markup = types.InlineKeyboardMarkup()
    reply_msg = ''
    for recipe in (recipe_list[start_indx:start_indx + 10]):
        reply_msg += f'{recipe[1]}\n'

    if start_indx > 0:
        markup.add(types.InlineKeyboardButton(
            f'Previous page',
            callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx - 10, action='list')))
    if start_indx + 10 < len(recipe_list):
        markup.add(types.InlineKeyboardButton(
            f'Next page',
            callback_data=recipe_cb.new(recipe_id='-', start_indx=start_indx + 10, action='list')))
    return {'markup': markup, 'msg': reply_msg.replace("\'", "")}


@dp.message_handler(Text(equals='Показать все категории'), state="*")
async def search_categories(msg_search_type: types.Message):
    all_categories = bd.bot_get_categories()
    reply_fmt = get_reply_fmt(all_categories)
    if len(all_categories) <= 0:
        await bot.send_message(msg_search_type.chat.id, 'Не могу найти ничего по вашему запросу')
    else:
        await msg_search_type.answer(reply_fmt['msg'], reply_markup=reply_fmt['markup'])
    await ShowCategoriesList.start_listing.set()

    @dp.callback_query_handler(recipe_cb.filter(action='list'), state=ShowCategoriesList.start_listing)
    async def query_show_list_by_categories(query: types.CallbackQuery, callback_data: dict):
        last_recipes = all_categories
        reply_fmt = get_reply_fmt(last_recipes, callback_data['start_indx'])
        await query.message.edit_text(reply_fmt['msg'], reply_markup=reply_fmt['markup'])

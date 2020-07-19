from aiogram import types
from aiogram.utils.callback_data import CallbackData

from Bot.misc import bd, dp
from model.recipe import Recipe

recipe_cb = CallbackData('recipe', 'recipe_id', 'start_indx', 'action')


# Изменяем и переписываем кнопки

def get_reply_fmt(recipe_list, start_indx=0):
    if isinstance(start_indx, str):
        start_indx = int(start_indx)
    if start_indx < 0:
        start_indx = 0
    markup = types.InlineKeyboardMarkup()
    reply_msg = ''
    for i, recipe in enumerate(recipe_list[start_indx:start_indx + 10]):
        reply_msg += f'{i + 1}. {recipe.name}\n'
        markup.add(
            types.InlineKeyboardButton(
                f'{i + 1}',
                callback_data=recipe_cb.new(recipe_id=recipe.id, start_indx=start_indx, action='view')),
        )
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
    description = recipe.description.replace("\'", "").replace("\\n", "\n").replace("\\r", " ")
    text = f"Название: {recipe.name}\nКаллорийность: {recipe.calories} ккал.\nВремя приготовления: {recipe.time_cooking}\n{description}".replace(
        "\'", "")
    #TODO 4096 символов в 1 сообщении
    favourites = bd.bot_get_favourites(user_id)
    is_favourite = False
    if favourites:
        for favourite in favourites:
            if int(recipe.id) == int(favourite.id):
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


def query_handler_view(msg_for_search, callback_data):
    recipe_id = callback_data['recipe_id']
    recipe = bd.make_recipe_object(recipe_id)
    text, markup = format_recipe(recipe_id, callback_data['start_indx'], recipe,
                                 msg_for_search.from_user.id)
    return text, markup

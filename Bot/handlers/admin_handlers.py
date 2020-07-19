import random
import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from Bot.handlers.inline_methods import get_reply_fmt, recipe_cb, format_recipe
from Bot.misc import bd, dp, bot
from model.recipe import Recipe
import matplotlib.pyplot as plt
from Bot.handlers.matpolib_graph_maker import make_graph_by_args


class AdminTypesAction(StatesGroup):
    choose_action = State()


class AdminManager(StatesGroup):
    admin_redactor = State()
    admin_redactor_action = State()


admin_type_action = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Статистика за неделю'),
            types.KeyboardButton(text='Статистика за месяц')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)

admin_manage = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text='Добавить админа'),
            types.KeyboardButton(text='Удалить админа')
        ],
        [
            types.KeyboardButton(text='Вернуться')
        ]
    ],
    resize_keyboard=True
)


@dp.message_handler(Text(equals=['Статистика по новым пользователям', 'Статистика по активным']), state="*")
async def set_action(msg_search_type: types.Message, state: FSMContext):
    if bd.bot_check_is_admin(msg_search_type.from_user.id):
        await state.update_data(type_statistic=msg_search_type.text)
        await AdminTypesAction.choose_action.set()
        await msg_search_type.answer('Выберите тип поиска', reply_markup=admin_type_action)

    @dp.message_handler(Text(equals=['Статистика за неделю', 'Статистика за месяц']),
                        state=AdminTypesAction.choose_action)
    async def do_action(msg: types.Message):

        statistic = []
        filename = f'../tmp/{random.randint(12, 10000) * 33}.png'
        ox = ''
        oy = ''
        title = ""
        type = await state.get_data()

        if type['type_statistic'] == 'Статистика по новым пользователям':
            ox = 'дни'
            oy = 'кол-во новых пользователей'
            if msg.text == 'Статистика за неделю':
                title = 'Статистика новых пользователей за неделю'
                statistic = bd.bot_get_new_users_week()
            elif msg.text == 'Статистика за месяц':
                title = 'Статистика новых пользователей за месяц'
                statistic = bd.bot_get_new_users_month()
        elif type['type_statistic'] == 'Статистика по активным':
            ox = 'дни'
            oy = 'кол-во активных пользователей'
            if msg.text == 'Статистика за неделю':
                title = 'Статистика активных пользователей за неделю'
                statistic = bd.bot_get_active_users_week()
            elif msg.text == 'Статистика за месяц':
                title = 'Статистика активных пользователей за месяц'
                statistic = bd.bot_get_active_users_month()
        make_graph_by_args(statistic, filename, title, ox, oy)
        await bot.send_photo(msg.chat.id, open(filename, 'rb'))
        os.remove(filename)


@dp.message_handler(Text(equals='Управление админами'), state="*")
async def manage_admin(msg_search_type: types.Message):
    if bd.bot_check_is_admin(msg_search_type.from_user.id):
        await msg_search_type.answer('Выберите действие', reply_markup=admin_manage)
        await AdminManager.admin_redactor.set()
    else:
        return

    @dp.message_handler(Text(equals=['Добавить админа', 'Удалить админа']), state=AdminManager.admin_redactor)
    async def redactor_admin(msg: types.Message, state: FSMContext):
        await msg.answer('Введите логин : ')
        await AdminManager.next()
        await state.update_data(action=msg.text)

    @dp.message_handler(state=AdminManager.admin_redactor_action)
    async def name_input(msg_admin:types.Message,state:FSMContext):
        action = await state.get_data()
        if action['action'] == 'Добавить админа':
            bd.bot_make_user_admin(msg_admin.text)
            await msg_admin.answer('Успешно добавлен')
        elif action['action'] == 'Удалить админа':
            if bd.bot_check_is_root_admin(msg_admin.text):
                await msg_admin.answer('Нельзя удалить рут админа.')
            else:
                bd.bot_delete_user_admin(msg_admin.text)
                await msg_admin.answer('Удаление успешно закончено')
        else:
            await msg_admin.answer('чо то не так')
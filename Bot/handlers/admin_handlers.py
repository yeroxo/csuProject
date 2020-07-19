
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils.callback_data import CallbackData

from Bot.handlers.inline_methods import get_reply_fmt, recipe_cb, format_recipe
from Bot.misc import bd, dp, bot
from model.recipe import Recipe
import matplotlib.pyplot as plt


class AdminTypesAction(StatesGroup):
    choose_action = State()


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


@dp.message_handler(Text(equals=['Статистика по новым пользователям', 'Статистика по активным']), state="*")
async def set_action(msg_search_type: types.Message, state: FSMContext):
    if bd.bot_check_is_admin(msg_search_type.from_user.id):
        await state.update_data(type_statistic=msg_search_type.text)
        await AdminTypesAction.choose_action.set()
        await msg_search_type.answer('Выберите тип поиска', reply_markup=admin_type_action)

    @dp.message_handler(Text(equals=['Статистика за неделю', 'Статистика за месяц']), state=AdminTypesAction.choose_action)
    async def do_action(msg: types.Message):

        statistic = bd.bot_get_new_users_week()
        x = [i+1 for i in range(len(statistic))]
        y = statistic
        filename = 'tmp.png'
        fig = plt.figure()
        plt.plot(x, y)
        fig.suptitle('Новые пользователи на неделю')
        plt.xlabel('дни')
        plt.ylabel('кол-во новых пользователей')
        plt.savefig(filename)
        await bot.send_photo(msg.chat.id, open(filename, 'rb'))
        type = await state.get_data()

        if type['type_statistic'] == 'Статистика по новым пользователям':
            msg.answer('ss')
        elif type['type_statistic'] == 'Статистика по активным':
            await msg.answer('b')

from aiogram import executor
from Bot.misc import dp
import Bot.handlers

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
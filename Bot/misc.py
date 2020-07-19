import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from Db.LogicalPart import LogicalPart as DataBase

from Bot import config

# инициализируем все что нам нужно

bot = Bot(token=config.API_TOKEN)
memory_storage = MemoryStorage()
bd = DataBase()
dp = Dispatcher(bot, storage=memory_storage)
logging.basicConfig(level=logging.INFO)

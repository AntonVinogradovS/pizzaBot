from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other
from database import sqlite_db


    


async def on_startup(_):
    print("Бот вышел на связь")
    sqlite_db.sql_start()

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
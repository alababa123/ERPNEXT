from aiogram import executor
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from database.connect_db import conn, cur
async def on_startup(dispatcher):
    cur.execute("SET SESSION wait_timeout=88000;")
    conn.commit()
    await on_startup_notify(dispatcher)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

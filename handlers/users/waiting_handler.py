from aiogram import dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from keyboards.default.start import start_keyboard
from loader import dp
from states.foreman import foreman
from states.wait_state import wait, wait_foremane
from database.connect_db import cur, conn
from states.login_at_user import user_status
from states.worker import worker
from handlers.users.registration_handler import mes
from keyboards.default.start import start_keyboard
from states.worker import worker
from keyboards.default.foreman_job import foreman_start_job
from keyboards.default.worker_job import worker_start_job
@dp.message_handler(text="Проверить наличие обновлений", state=worker.no_job)
async def no_job(message: Message, state=FSMContext):
    conn.commit()
    cur.execute("select foreman, telegramidforeman from tabWorker where telegramid=%s" %message.from_user.id)
    a = cur.fetchall()
    if(not a):
        await message.answer("Вас еще не взяли на работу")
        await worker.no_job.set()
    else:
        await message.answer("Вы присоединились к %s" %a[0][0], reply_markup=worker_start_job)
        await message.answer('Нажмите "Начать рабочий день", чтобы выйти на смену')
        await state.finish()
@dp.message_handler(state=wait.ver)
async def waiting(message: Message, state=FSMContext):
    while(1):
        conn.commit()
        cur.execute("select * from tabEmployer where name=%d" %message.from_user.id)
        a = cur.fetchall()
        if (a[0][4]):
            break
    cur.execute("select role from `tabRole of Employer` where name=%s" %a[0][4])
    role = cur.fetchall()
    mas = []
    mas.append(a[0][0])
    mas.append(a[0][1])
    mas.append(a[0][2])
    mas.append("1")
    mas.append(a[0][3])
    mas.append(a[0][4])
    mas.append(a[0][5])
    mas.append(" ")
    mas.append(" ")
    mas.append(a[0][7])
    mas.append(a[0][8])
    if (role[0][0] == "Прораб"):
        cur.execute("insert into tabProrab (name ,creation ,owner , enable, fio, phone_number, telegramid, ,dateobj, object, photo_worker, ,photo_passport)")
    elif(role[0][0] == "Рабочий"):
        cur.execute("insert into `tabWorker Free` (name ,creation ,owner , enable, fio, phone_number, telegramid, ,dateobj, object, photo_worker, ,photo_passport)")
    await message.answer("Добрый день, вам выдали роль: %s. Вы можете начать свой рабочий день." %role[0][0], reply_markup=worker_start_job)
    await state.finish()
@dp.message_handler(state=wait_foremane.ver)
async def waiting(message: Message, state=FSMContext):
    conn.commit()
    cur.execute("select * from tabProrab where name=%d and enable=0" %message.from_user.id)
    a = cur.fetchall()
    if(a):
        await message.answer("Вас еще не подтвердили!")
        await wait.ver.set()
    else:
        await message.answer("Вы верифицированы, нажмите копку внизу чтобы начать работать!", reply_markup=worker_start_job)
        await state.finish()
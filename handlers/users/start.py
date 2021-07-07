from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.default.registation import reg
from loader import dp
from database.connect_db import conn, cur, cur1
from keyboards.default.worker_no_job import worker_no_job
from keyboards.default.worker_job import worker_start_job
from keyboards.inline.foreman_menu import foreman_menu
from states.worker import worker
from states.foreman import foreman
from keyboards.default.foreman_job import foreman_start_job
from datetime import datetime
from keyboards.inline.worker import worker_menu_company
name_worker = ""
name_foreman = ""
st = ""
st_name_task = ""
@dp.message_handler(CommandStart())
async def show_menu(message: Message):
    conn.commit()
    mes = message.from_user.id
    cur.execute("select fio from tabProrab where telegramid=%s and enable=1" % mes)
    a = cur.fetchall()
    cur.execute("select fio from `tabWorker Free` where telegramid=%d and enable=1" % mes)
    b = cur.fetchall()
    cur.execute("select fio from tabWorker where telegramid=%d and enable=1" % mes)
    c = cur.fetchall()
    cur.execute("select fio, rank from tabEmployer where telegramid=%d" %mes)
    d = cur.fetchall()
    if (a):
        name_foreman = a[0]
        cur.execute("select object from tabProrab where telegramid=%s" % message.from_user.id)
        obj = cur.fetchall()
        if (obj[0][0]):
            await message.answer('Добрый день, %s!' % a[0], reply_markup=ReplyKeyboardRemove())
            await message.answer(text="Главное меню", reply_markup=foreman_menu)
            await foreman.job.set()
        else:
            await message.answer('Добрый день, %s, вы не прикреплены к объекту.' % a[0], reply_markup=foreman_start_job)
    elif (b):
        await message.answer(f"Добрый день, %s!" % b[0], reply_markup=worker_no_job)
        await worker.no_job.set()
    elif (c):
        mas = []
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("select telegramidforeman from tabWorker where telegramid=%s" %message.from_user.id)
        tg = cur.fetchall()
        st = str(now) + " " +  str(message.from_user.id)
        st_name_task = st
        mas.append(st)
        mas.append(now)
        print(datetime.now())
        mas.append("Administrator")
        mas.append(c[0][0])
        now = datetime.now().strftime('%Y-%m-%d')
        mas.append(now)
        mas.append(None)
        mas.append(message.from_user.id)
        mas.append(tg[0][0])
        cur.execute("insert into `tabWorker activity temp` (name ,creation ,owner, fio, date_join, date_end, telegramid, telegramidforeman)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", mas)
        conn.commit()
        await message.answer('Добрый день, %s!' % c[0], reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Главное меню", reply_markup=worker_menu_company)
        await worker.job.set()
    elif(d):
        await message.answer("Ваша заявка на регистрацию находится на рассмотрении, подождите немного")
        conn.commit()
        cur.execute("select name, creation, owner, fio, phone_number, telegramid, rank, photo, photo_pass from tabEmployer where name=%s" % mes)
        a = cur.fetchall()
        if(a[0][6]):
            mas1 =[]
            mas1.append(a[0][6])
            cur.execute("select role from `tabRole of Employer` where name=?", mas1 )
            role = cur.fetchall()
            print(role)
            mas = []
            mas.append(a[0][0])
            mas.append(a[0][1])
            mas.append(a[0][2])
            mas.append("1")
            mas.append(a[0][3])
            mas.append(a[0][4])
            mas.append(a[0][5])
            mas.append("")
            mas.append("")
            mas.append(a[0][7])
            mas.append(a[0][8])
            if (role[0][0] == "Прораб"):
                cur.execute("INSERT INTO tabProrab"
                            " (name ,creation ,owner , enable, fio, phone_number, telegramid, dateobj, object, photo_worker, photo_passport)"
                            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
                await message.answer(
                    "Добрый день, вам выдали роль: %s. Вы можете начать свой рабочий день." % role[0][0],
                    reply_markup=foreman_start_job)
            elif (role[0][0] == "Рабочий"):
                cur.execute(
                    "insert into `tabWorker Free` (name ,creation ,owner , enable, fio, phone_number, telegramid, dateobj, object, photo_worker, photo_passport)"
                    " values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
                await message.answer("Добрый день, вам выдали роль: %s. Вы можете начать свой рабочий день." % role[0][0], reply_markup=worker_start_job)
            conn.commit()
    else:
        await message.answer('Вас приветствует бот УП_ERP! \nНажмите кнопку "Зарегистрироваться", чтобы пройти регистрацию. \n\nПосле подтверждения личности, вы можете начать работу!', reply_markup=reg)

@dp.message_handler(text="Начать рабочий день", state=None)
async def join_job(message: Message, state=FSMContext):
    conn.commit()
    mes = message.from_user.id
    mes = message.from_user.id
    cur.execute("select fio from tabProrab where telegramid=%s and enable=1" %mes)
    a = cur.fetchall()
    cur.execute("select fio from `tabWorker Free` where telegramid=%d and enable=1" %mes)
    b = cur.fetchall()
    cur.execute("select fio from tabWorker where telegramid=%d and enable=1" % mes)
    c = cur.fetchall()
    cur.execute("select fio from tabEmployer where telegramid=%d" % mes)
    d = cur.fetchall()
    if (a):
        name_foreman = a[0]
        cur.execute("select object from tabProrab where telegramid=%s" % message.from_user.id)
        obj = cur.fetchall()
        if(obj[0][0]):
            print(obj)
            await message.answer('Добрый день, %s!' %a[0], reply_markup=ReplyKeyboardRemove())
            await message.answer(text="Главное меню", reply_markup=foreman_menu)
            await foreman.job.set()
        else:
            await message.answer('Добрый день, %s, вы не прикреплены к объекту.' % a[0], reply_markup=foreman_start_job)
    elif (b):
        await message.answer(f"Добрый день, %s!"  %b[0], reply_markup=worker_no_job)
        await worker.no_job.set()
    elif (c):
        mas = []
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("select telegramidforeman from tabWorker where telegramid=%s" % message.from_user.id)
        tg = cur.fetchall()
        st = str(now) + " " + str(message.from_user.id)
        mas.append(st)
        mas.append(now)
        mas.append("Administrator")
        mas.append(c[0][0])
        mas.append(datetime.now().strftime('%Y-%m-%d'))
        mas.append(None)
        mas.append(message.from_user.id)
        mas.append(tg[0][0])
        cur.execute(
            "insert into `tabWorker activity temp` (name ,creation ,owner, fio, date_join, date_end, telegramid, telegramidforeman)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", mas)
        conn.commit()
        await message.answer('Добрый день, %s!' % c[0])
        await message.answer(text="Главное меню", reply_markup=worker_menu_company)
        await worker.job.set()
    elif (d):
        await message.answer("Ваша заявка на регистрацию находится на рассмотрении, подождите немного")
        conn.commit()
        cur.execute(
            "select name, creation, owner, fio, phone_number, telegramid, rank, photo, photo_pass from tabEmployer where name=%s" % mes)
        a = cur.fetchall()
        print(a)
        if (a[0][6]):
            mas1 = []
            mas1.append(a[0][6])
            cur.execute("select role from `tabRole of Employer` where name=?", mas1)
            role = cur.fetchall()
            print(role)
            mas = []
            mas.append(a[0][0])
            mas.append(a[0][1])
            mas.append(a[0][2])
            mas.append("1")
            mas.append(a[0][3])
            mas.append(a[0][4])
            mas.append(a[0][5])
            mas.append("")
            mas.append("")
            mas.append(a[0][7])
            mas.append(a[0][8])
            if (role[0][0] == "Прораб"):
                cur.execute("INSERT INTO tabProrab"
                            " (name ,creation ,owner , enable, fio, phone_number, telegramid, dateobj, object, photo_worker, photo_passport)"
                            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
                await message.answer(
                    "Добрый день, вам выдали роль: %s. Вы можете начать свой рабочий день." % role[0][0],
                    reply_markup=foreman_start_job)
            elif (role[0][0] == "Рабочий"):
                cur.execute(
                    "insert into `tabWorker Free` (name ,creation ,owner , enable, fio, phone_number, telegramid, dateobj, object, photo_worker, photo_passport)"
                    " values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
                await message.answer("Добрый день, вам выдали роль: %s. Вы можете начать свой рабочий день." % role[0][0],
                                     reply_markup=worker_start_job)
            conn.commit()

@dp.message_handler(text="/back", state="*")
async def back_from_reg(message: Message, state=FSMContext):
    await message.answer("Вы вернулись в главное меню", reply_markup=ReplyKeyboardRemove())
    await state.finish()

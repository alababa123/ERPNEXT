import asyncio

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.reg_buttons import end_reg
from keyboards.default.registation import reg
from loader import dp
from states.registration import registration as reg
from states.registration import registration_foreman as reg_foreman
from aiogram.dispatcher import FSMContext
from keyboards.default.cancel import cancel
from keyboards.default.foreman_job import foreman_start_job
from data.config import loc_photo_worker, loc_photo_foreman, loc_pass_worker, loc_pass_foreman
from database.connect_db import conn, cur, cur1
import datetime
from loader import bot
import re
from utils.format import format_phone
from states.wait_state import wait, wait_foremane
from states.foreman import foreman
from keyboards.inline.foreman_menu import foreman_menu

@dp.message_handler(text="Начать рабочий день", state=foreman.start_job)
async def join_session(message: Message):
    now = datetime.datetime.now()
    await message.answer("Добрый день, сегодня %s число." %now.strftime("%d-%m-%Y"), reply_markup=foreman_menu)
    await foreman.job.set()

@dp.callback_query_handler(text_contains="serv:Список свободных рабочих", state=foreman.job)
async def free_work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    print(1)
    cur.execute("select fio, telegramid from `tabWorker Free` where enable='1'")
    a = cur.fetchall()
    free_work = []
    print(a)
    for i in a:
        free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
    free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
    foreman_btn = InlineKeyboardMarkup(
        inline_keyboard=free_work,
    )
    await call.message.edit_text(text="Список свободных рабочих", reply_markup=foreman_btn)
    await foreman.free_worker.set()

@dp.callback_query_handler(state=foreman.free_worker)
async def free_work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    if (str == "Назад"):
        await call.message.edit_text(text="Главное меню", reply_markup=foreman_menu)
        await foreman.job.set()
    else:
        cur.execute("select fio, phone_number, telegramid, comments_foreman, photo_worker, photo_passport from `tabWorker Free` where enable='1' and telegramid=%s" % str)
        a = cur.fetchall()
        free_work = []
        free_work.append([InlineKeyboardButton("Взять в подчинение", callback_data="Взять в подчинение")])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_choise_free_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text("Профиль рабочего %s\nНомер телефона: %s\nТелеграм ID: %s\nКомментарий предыдущего прораба: %s\n" %(a[0][0], a[0][1], a[0][2], a[0][3]),
                                     reply_markup=foreman_choise_free_btn)
        await state.update_data(fio=a[0][0], phone_number=a[0][1], telegramid=a[0][2], comment=a[0][3], photo=a[0][4], passport=a[0][5])
        await foreman.free_worker_profile.set()

@dp.callback_query_handler(state=foreman.free_worker_profile)
async def invite_team(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    telegram = call.from_user.id
    if (str == "Назад"):
        cur.execute("select fio, telegramid from `tabWorker Free` where enable='1'")
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список свободных рабочих", reply_markup=foreman_btn)
        await foreman.free_worker.set()
    else:
        mas_foreman = []
        now = datetime.datetime.now()
        data = await state.get_data()
        print(telegram)
        cur.execute("select fio, telegramid, object from tabProrab where telegramid=%s" %telegram)
        mas_foreman = cur.fetchall()
        print(mas_foreman)
        mas = []
        mas.append(data.get("telegramid"))
        mas.append(now)
        mas.append("Administrator")
        mas.append("1")
        mas.append(data.get("fio"))
        mas.append(data.get("phone_number"))
        mas.append(data.get("telegramid"))
        mas.append(mas_foreman[0][0])
        mas.append(now)
        mas.append(data.get("comment"))
        mas.append(mas_foreman[0][2])
        mas.append(data.get("photo"))
        mas.append(data.get("passport"))
        mas.append(mas_foreman[0][1])
        #cur.execute("select * into tabemployer_worker from `tabWorker Free` where telegramid=%s" %data.get("telegramid"))
        cur.execute("INSERT INTO tabWorker (name ,creation ,owner ,enable , fio, phone_number, telegramid, foreman, dateobj, comments_foreman, object, photo_worker, photo_passport, telegramidforeman) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
        cur.execute("delete from `tabWorker Free` where telegramid=%s" %data.get("telegramid"))
        conn.commit()
        await call.message.delete()
        await call.message.answer("Рабочий %s был перведён к вам!" %data.get("fio"))
        cur.execute("select fio, telegramid from `tabWorker Free` where enable='1'")
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список свободных рабочих", reply_markup=foreman_btn)
        await foreman.free_worker.set()

@dp.callback_query_handler(text_contains="serv:Журнал учёта рабочих", state=foreman.job)
async def check_time(call: CallbackQuery, state=FSMContext):
    cur.execute("select fio, telegramid from `tabWorker activity temp` where telegramidforeman=%s" %call.from_user.id)
    a = cur.fetchall()
    free_work = []
    print(a)
    for i in a:
        free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
    free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
    foreman_btn = InlineKeyboardMarkup(
        inline_keyboard=free_work,
    )
    await call.message.edit_text(text="Список отметившихся", reply_markup=foreman_btn)
    await foreman.activity_worker.set()

@dp.callback_query_handler(state=foreman.activity_worker)
async def free_work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    if (str == "Назад"):
        await call.message.edit_text(text="Главное меню", reply_markup=foreman_menu)
        await foreman.job.set()
    else:
        cur.execute("select fio, date_join, telegramidforeman, name from `tabWorker activity temp` where telegramid=%s" % str)
        a = cur.fetchall()
        cur.execute("select phone_number from tabWorker where telegramid=%s" % str)
        tg = cur.fetchall()
        free_work = []
        time_work = ""
        time_work = a[0][1]
        free_work.append([InlineKeyboardButton(text="Принять", callback_data="Принять")])
        free_work.append([InlineKeyboardButton(text="Отклонить", callback_data="Отклонить")])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_choise_free_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        print(a[0][1])
        await call.message.edit_text("Имя рабочего %s\nНомер телефона: %s\nВремя прихода на работу: %s"
                                     %(a[0][0], tg[0][0], time_work),reply_markup=foreman_choise_free_btn)
        await state.update_data(telegramid=str, fio=a[0][0], date_join=a[0][1], telegramidforeman=a[0][2], nameTaskActivity=a[0][3])
        await foreman.activity_worker_profile.set()

@dp.callback_query_handler(state=foreman.activity_worker_profile)
async def invite_team(call: CallbackQuery, state=FSMContext):
    conn.commit()
    stri = call.data
    telegram = call.from_user.id
    if (stri == "Назад"):
        cur.execute(
            "select fio, telegramid from `tabWorker activity temp` where telegramidforeman=%s" % call.from_user.id)
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список отметившихся", reply_markup=foreman_btn)
        await foreman.activity_worker.set()
    elif(stri == "Принять"):
        mas_foreman = []
        now = datetime.datetime.now()
        data = await state.get_data()
        print(telegram)
        mas = []
        st = ""
        mas.append(data.get("nameTaskActivity"))
        mas.append(datetime.datetime.now())
        mas.append("Administrator")
        mas.append(data.get("fio"))
        mas.append(data.get("date_join"))
        mas.append(None)
        mas.append(data.get("telegramid"))
        mas.append(data.get("telegramidforeman"))
        cur.execute(
            "insert into `tabWorker activity` (name ,creation ,owner, fio, date_join, date_end, telegramid, telegramidforeman)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", mas)
        mas = []
        mas.append(data.get("telegramid"))
        mas.append(data.get("date_join"))
        cur.execute("delete from `tabWorker activity temp` where telegramid=? and date_join=?", mas)
        conn.commit()
        cur.execute(
            "select fio, telegramid from `tabWorker activity temp` where telegramidforeman=%s" % call.from_user.id)
        a = cur.fetchall()
        free_work = []
        await call.message.delete()
        await call.message.answer("Принято!")
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список отметившихся", reply_markup=foreman_btn)
        await foreman.activity_worker.set()
    elif(stri == "Отклонить"):
        data = await state.get_data()
        temp = []
        print(data.get("telegramid"))
        j = data.get("telegramid")
        j = int(j)
        await bot.send_message(j, "Сообщение от прораба: "
                                  "Ваш данные начала работы отклонены!")
        mes = []
        mes.append(data.get("date_join"))
        mes.append(data.get("telegramid"))
        cur.execute("delete from `tabWorker activity temp` where date_join=? and telegramid=?", mes)
        conn.commit()
        await call.message.delete()
        await call.message.answer("Отклонено!")
        cur.execute(
            "select fio, telegramid from `tabWorker activity temp` where telegramidforeman=%s" % call.from_user.id)
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список отметившихся", reply_markup=foreman_btn)
        await foreman.activity_worker.set()


@dp.callback_query_handler(text_contains="serv:Список подчиненных", state=foreman.job)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    print(1)
    cur.execute("select fio, telegramid from tabWorker where enable='1' and telegramidforeman=%s" %call.from_user.id)
    a = cur.fetchall()
    free_work = []
    print(a)
    for i in a:
        free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
    free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
    foreman_btn = InlineKeyboardMarkup(
        inline_keyboard=free_work,
    )
    await call.message.edit_text(text="Список подчиненных", reply_markup=foreman_btn)
    await foreman.worker.set()

@dp.callback_query_handler(state=foreman.worker)
async def free_work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    if (str == "Назад"):
        await call.message.edit_text(text="Главное меню", reply_markup=foreman_menu)
        await foreman.job.set()
    else:
        cur.execute("select fio, phone_number, telegramid, comments_foreman, photo_worker, photo_passport from tabWorker where enable='1' and telegramid=%s" % str)
        a = cur.fetchall()
        free_work = []
        free_work.append([InlineKeyboardButton(text="Удалить", callback_data="Удалить")])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_choise_free_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text("Профиль рабочего %s\nНомер телефона: %s\nТелеграм ID: %s\nКомментарий предыдущего прораба: %s\n" %(a[0][0], a[0][1], a[0][2], a[0][3]),
                                     reply_markup=foreman_choise_free_btn)
        await state.update_data(fio=a[0][0], phone_number=a[0][1], telegramid=a[0][2], comment=a[0][3], photo=a[0][4], passport=a[0][5])
        await foreman.worker_profile.set()

@dp.callback_query_handler(state=foreman.worker_profile)
async def invite_team(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    telegram = call.from_user.id
    if (str == "Назад"):
        cur.execute(
            "select fio, telegramid from tabWorker where enable='1' and telegramidforeman=%s" %call.from_user.id)
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список подчиненных", reply_markup=foreman_btn)
        await foreman.worker.set()
    else:
        mas_foreman = []
        now = datetime.datetime.now()
        data = await state.get_data()
        print(telegram)
        cur.execute("select fio, telegramid, object from tabProrab where telegramid=%s" %telegram)
        mas_foreman = cur.fetchall()
        print(mas_foreman)
        mas = []
        mas.append(data.get("telegramid"))
        mas.append(now)
        mas.append("Administrator")
        mas.append("1")
        mas.append(data.get("fio"))
        mas.append(data.get("phone_number"))
        mas.append(data.get("telegramid"))
        mas.append(" ")
        mas.append(None)
        mas.append(data.get("comment"))
        mas.append(" ")
        mas.append(data.get("photo"))
        mas.append(data.get("passport"))
        mas.append(" ")
        #cur.execute("select * into tabemployer_worker from `tabWorker Free` where telegramid=%s" %data.get("telegramid"))
        cur.execute("INSERT INTO `tabWorker Free` (name ,creation ,owner ,enable , fio, phone_number, telegramid, foreman, dateobj, comments_foreman, object, photo_worker, photo_passport, telegramidforeman) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
        cur.execute("delete from tabWorker where telegramid=%s" %data.get("telegramid"))
        conn.commit()
        await call.message.delete()
        await call.message.answer("Рабочий %s был перенесён в архив!" %data.get("fio"))
        cur.execute(
            "select fio, telegramid from tabWorker where enable='1' and telegramidforeman=%s" % call.from_user.id)
        a = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список подчиненных", reply_markup=foreman_btn)
        await foreman.worker.set()


@dp.callback_query_handler(text_contains="serv:Список отчетов", state=foreman.job)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    print(1)
    cur.execute("select distinct worker_name, telegramid"
                " from `tabTemp worker report` where telegramidforeman=%s" %call.from_user.id)
    a = cur.fetchall()
    free_work = []
    print(a)
    b = []
    for i in a:
        free_work.append([InlineKeyboardButton(text=i[0] , callback_data=i[1])])
        b.clear()
    free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
    foreman_btn = InlineKeyboardMarkup(
        inline_keyboard=free_work,
    )
    await call.message.edit_text(text="Список отчетов", reply_markup=foreman_btn)
    await foreman.report_temp.set()

@dp.callback_query_handler(state=foreman.report_temp)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    print(1)
    stri = call.data
    if(stri == "Назад"):
        await call.message.edit_text(text="Главное меню", reply_markup=foreman_menu)
        await foreman.job.set()
    else:
        mas_data = [call.from_user.id, stri]
        cur.execute("select job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, phone_number_foreman, date"
                " from `tabTemp worker report` where telegramidforeman=? and telegramid=?", mas_data)
        a = cur.fetchall()
        mis = [stri]
        cur.execute("select fio from tabWorker where telegramid=?", mis)
        c = cur.fetchall()
        free_work = []
        print(a)
        for i in a:
            st = str(i[9])
            free_work.append([InlineKeyboardButton(text=i[0] , callback_data=i[5] + "+" + st)])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список отчетов рабочего %s" %c[0][0], reply_markup=foreman_btn)
        await foreman.report_temp_down.set()

@dp.callback_query_handler(state=foreman.report_temp_down)
async def free_work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    str = call.data
    if (str == "Назад"):
        print(1)
        cur.execute(
            "select distinct worker_name, telegramid"
            " from `tabTemp worker report` where telegramidforeman=%s" % call.from_user.id)
        a = cur.fetchall()
        free_work = []
        print(a)
        b = []
        for i in a:
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[1])])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список отчетов", reply_markup=foreman_btn)
        await foreman.report_temp.set()
    else:
        mas = str.split("+")
        print(mas)
        cur.execute("select job, job_section, photo, job_value, worker_name, telegramid, phone_number, "
                    "foreman_name, telegramidforeman, phone_number_foreman, date, task_name, name "
                    "from `tabTemp worker report` where telegramid=? and date=?", mas)
        a = cur.fetchall()
        free_work = []
        free_work.append([InlineKeyboardButton(text="Принять", callback_data="Принять")])
        free_work.append([InlineKeyboardButton(text="Отклонить", callback_data="Отклонить")])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_choise_free_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        mis = [a[0][11]]
        cur.execute("select amount, progress_amount from tabTask where name=?", mis )
        b = cur.fetchall()
        print(a)
        await call.message.edit_text("Название работы: %s\nРаздел работы: %s\nОбъем работ: %s\nВыполнено на текущих момент: %s\nОбщий объем работ: %s\nНомер телефона рабочего: %s\nИмя рабочего: %s" %(a[0][0], a[0][1], a[0][3], b[0][1], b[0][0], a[0][6], a[0][4]), reply_markup=foreman_choise_free_btn)
        await state.update_data(job=a[0][0], job_section=a[0][1], telegramid_report=a[0][5],
                                photo_work=a[0][2], job_value=a[0][3],
                                worker_name=a[0][4], phone_number_worker_report=a[0][6],
                                foreman_report_name=a[0][7], telegramid_report_forename=a[0][8],
                                foreman_report_phone_number=a[0][9], date=a[0][10], task_name=a[0][11])
        await foreman.report_temp_profile.set()

@dp.callback_query_handler(state=foreman.report_temp_profile)
async def invite_team(call: CallbackQuery, state=FSMContext):
    conn.commit()
    stri = call.data
    telegram = call.from_user.id
    if (stri == "Назад"):
        data = await state.get_data()
        await state.update_data(telegramid_report=data.get("telegramid_report"))
        temp = [data.get("telegramid_report"), call.from_user.id]
        cur.execute("select job, job_section, photo, job_value, worker_name, telegramid, phone_number, "
                    "foreman_name, phone_number_foreman, date, task_name "
                    "from `tabTemp worker report` where telegramid=? and telegramidforeman=?", temp)
        a = cur.fetchall()
        cur.execute("select fio from tabWorker where telegramid=%s" % temp[0])
        c = cur.fetchall()
        free_work = []
        for i in a:
            st = i[9]
            st = str(st)
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[5] + "+" + st)])
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.edit_text(text="Список отчетов рабочего %s" %c[0][0], reply_markup=foreman_btn)
        await foreman.report_temp_down.set()
    elif(stri == "Принять"):
        a = []
        now = datetime.datetime.now()
        print(telegram)
        data = await state.get_data()
        await state.update_data(telegramid_report=data.get("telegramid_report"))
        temp=[]
        temp.append(data.get("telegramid_report"))
        temp.append(data.get("job"))
        cur.execute("select job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, telegramidforeman,"
                    "phone_number_foreman, date, task_name, name from `tabTemp worker report` where telegramid=? and job=?", temp)
        a = cur.fetchall()
        mas = []
        name = a[0][12]
        mas.append(name)
        mas.append(now)
        mas.append("Administrator")
        mas.append(a[0][0])
        mas.append(a[0][1])
        mas.append(a[0][2])
        mas.append(a[0][3])
        mas.append(a[0][4])
        mas.append(a[0][5])
        mas.append(a[0][6])
        mas.append(a[0][7])
        mas.append(a[0][8])
        mas.append(a[0][9])
        mas.append(a[0][10])
        mas.append(a[0][11])
        print(mas)
        #cur.execute("select * into tabWorker from `tabWorker Free` where telegramid=%s" %data.get("telegramid"))
        cur.execute("INSERT INTO `tabWorker report` (name ,creation ,owner , job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, telegramidforeman, phone_number_foreman, date, task_name) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
        cur.execute("delete from `tabTemp worker report` where telegramid=? and job=?", temp)
        mos = []
        mos.append(a[0][11])
        cur.execute("select amount, progress_amount from tabTask where name=?", mos)
        b = cur.fetchall()
        job_value = a[0][3]
        print(type(float(job_value)))
        job_max = b[0][0]
        job_current_value = b[0][1]
        if(type(job_current_value) == None):
            job_current_value = 0.
            print(12)
            print(type(job_current_value))
        progress = (float(job_value) / float(job_max)) * 100
        print(job_current_value)
        progress_amount = float(job_current_value) + float(job_value)
        mes = []
        mes.append(progress_amount)
        mes.append(float(progress))
        mes.append(a[0][11])
        cur.execute("update tabTask set progress_amount=?, progress=? where name=?", mes)
        await call.message.delete()
        await call.message.answer("Прогресс по задаче обновлён")
        await call.message.answer("Отчет занесён в базу!")
        conn.commit()
        print(1)
        tempa = [temp[0], call.from_user.id]
        cur.execute(
            "select job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, phone_number_foreman, date from `tabTemp worker report` where telegramid=? and telegramidforeman=?",
            tempa)
        a = cur.fetchall()
        cur.execute("select fio from tabWorker where telegramid=%s" % temp[0])
        c = cur.fetchall()
        free_work = []
        print(a)
        b = []
        for i in a:
            st = str(a[0][9])
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[5] + "+" + st)])
            b.clear()
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список отчетов рабочего %s" % c[0][0], reply_markup=foreman_btn)
        await foreman.report_temp_down.set()
    elif (stri == "Отклонить"):
        data = await state.get_data()
        temp = []
        temp.append(data.get("telegramid_report"))
        await state.update_data(telegramid_report=data.get("telegramid_report"))
        temp.append(data.get("job"))
        await bot.send_message(data.get("telegramid_report"), "Ваш отчет отклонили!")
        cur.execute("delete from `tabTemp worker report` where telegramid=? and job=?", temp)
        conn.commit()
        await call.message.delete()
        await call.message.answer("Отчет отклонён!")
        conn.commit()
        print(1)
        tempa = [temp[0], call.from_user.id]
        cur.execute(
            "select job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, phone_number_foreman, date from `tabTemp worker report` where telegramid=? and telegramidforeman=?", tempa )
        a = cur.fetchall()
        cur.execute("select fio from tabWorker where telegramid=%s" % temp[0])
        c = cur.fetchall()
        free_work = []
        print(a)
        b = []
        for i in a:
            st = str(a[0][9])
            free_work.append([InlineKeyboardButton(text=i[0], callback_data=i[5]+ "+" + st)])
            b.clear()
        free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        foreman_btn = InlineKeyboardMarkup(
            inline_keyboard=free_work,
        )
        await call.message.answer(text="Список отчетов рабочего %s" %c[0][0], reply_markup=foreman_btn)
        await foreman.report_temp_down.set()

@dp.callback_query_handler(text_contains="serv:Закончить рабочий день", state=foreman.job)
async def end_session(call: CallbackQuery, state=FSMContext):
    now = datetime.datetime.now()
    await call.message.delete()
    await call.message.answer(text="Вы закончили рабочий день", reply_markup=foreman_start_job)
    await state.finish()

import datetime

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loader import dp
from aiogram.dispatcher import FSMContext
from database.connect_db import conn, cur, cur1
from loader import bot
from states.manager import manage
from keyboards.inline.manage_menu import manage_menu, manage_menu_delete
@dp.message_handler(text="Начать рабочий день", state=manage.start_job)
async def join_session(message: Message):
    now = datetime.datetime.now()
    await message.answer("Добрый день, сегодня %s число." %now.strftime("%d-%m-%Y"), reply_markup=manage_menu)
    await manage.job.set()

@dp.callback_query_handler(text_contains="serv:Удаление сотрудников", state=manage.job)
async def deleting_worker(call: CallbackQuery, state=FSMContext):
    conn.commit()
    btn = []
    cur.execute("select fio, telegramid from tabemployer_worker")
    tabemployer_worker = cur.fetchall()
    for i in tabemployer_worker:
        btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker")])
    cur.execute("select fio, telegramid from tabemployer_foreman")
    tabemployer_foreman = cur.fetchall()
    for i in tabemployer_foreman:
        btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_foreman")])
    cur.execute("select fio, telegramid from tabemployer_worker_free")
    tabemployer_worker_free = cur.fetchall()
    for i in tabemployer_worker_free:
        btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker_free")])
    btn.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
    btn = InlineKeyboardMarkup(
        inline_keyboard=btn,
    )
    await call.message.edit_text(text="Списки рабочих", reply_markup=btn)
    await manage.delete.set()

@dp.callback_query_handler(state=manage.delete)
async def deleting_profile(call: CallbackQuery, state=FSMContext):
    st = call.data
    if(st == "Назад"):
        await call.message.edit_text(text="Меню", reply_markup=manage_menu)
        await manage.start_job
    else:
        await call.message.delete()
        mas = st.split("+")
        cur.execute("select fio from %s where telegramid=%s" %(mas[1], mas[0]))
        await state.update_data(telegram=mas[0])
        fio = cur.fetchall()
        await call.message.answer("Сотрудник %s был перемещен в архив, желаете его заменить?" %fio[0][0], reply_markup=manage_menu_delete)
        await manage.choise.set()
@dp.callback_query_handler(state=manage.choise)
async def deleting_choise(call: CallbackQuery, state=FSMContext):
    st = call.data
    data = await state.get_data()
    if(st == "Да"):
        btn = []
        cur.execute("select fio, telegramid from tabemployer_worker where telegramid != %s" %data.get("telegram"))
        tabemployer_worker = cur.fetchall()
        for i in tabemployer_worker:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker")])
        cur.execute("select fio, telegramid from tabemployer_foreman where telegramid != %s" %data.get("telegram"))
        tabemployer_foreman = cur.fetchall()
        for i in tabemployer_foreman:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_foreman")])
        cur.execute("select fio, telegramid from tabemployer_worker_free where telegramid != %s" %data.get("telegram"))
        tabemployer_worker_free = cur.fetchall()
        for i in tabemployer_worker_free:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker_free")])
        btn.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        btn = InlineKeyboardMarkup(
            inline_keyboard=btn,
        )
        await call.message.edit_text(text="Заменить на", reply_markup=btn)
        await manage.input_name.set()
    else:
        cur.execute("select fio, telegramid from tabemployer_worker_free where telegramid=%s" %data.get("telegram"))
        a = cur.fetchall()
        cur.execute("select fio, telegramid from tabemployer_foreman where telegramid=%s" %data.get("telegram"))
        b = cur.fetchall()
        cur.execute("select fio, telegramid from tabemployer_worker where telegramid=%s" %data.get("telegram"))
        c = cur.fetchall()
        mas = [data.get("telegram"), datetime.datetime.now(), "Administrator"]
        if a:
            mas.append(a[0][0])
            mas.append(a[0][1])
            cur.execute("insert into tabArchive_employer (name, creation, owner, fio, phone_number) values (%s, %s, %s, %s, %s)", mas)
            cur.execute("delete from tabemployer_worker where telegramid=%s" %data.get("telegram"))
        elif(b):
            mas.append(b[0][0])
            mas.append(b[0][1])
            cur.execute("insert into tabArchive_employer (name, creation, owner, fio, phone_number) values (%s, %s, %s, %s, %s)", mas)
            cur.execute("delete from tabemployer_foreman where telegramid=%s" %data.get("telegram"))
        elif (c):
            mas.append(c[0][0])
            mas.append(c[0][1])
            cur.execute("insert into tabArchive_employer (name, creation, owner, fio, phone_number) values (%s, %s, %s, %s, %s)", mas)
            cur.execute("delete from tabemployer_worker where telegramid=%s" %data.get("telegram"))
        conn.commit()
        btn = []
        cur.execute("select fio, telegramid from tabemployer_worker")
        tabemployer_worker = cur.fetchall()
        for i in tabemployer_worker:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker")])
        cur.execute("select fio, telegramid from tabemployer_foreman")
        tabemployer_foreman = cur.fetchall()
        for i in tabemployer_foreman:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_foreman")])
        cur.execute("select fio, telegramid from tabemployer_worker_free")
        tabemployer_worker_free = cur.fetchall()
        for i in tabemployer_worker_free:
            btn.append([InlineKeyboardButton(text=i[0], callback_data=i[1] + "+tabemployer_worker_free")])
        btn.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
        btn = InlineKeyboardMarkup(
            inline_keyboard=btn,
        )
        await call.message.edit_text(text="Списки рабочих", reply_markup=btn)
        await manage.delete.set()
    
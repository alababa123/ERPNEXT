from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.reg_buttons import end_reg
from keyboards.default.registation import reg
from loader import dp
from states.registration import registration as reg
from states.registration import registration_foreman as reg_foreman
from aiogram.dispatcher import FSMContext
from keyboards.default.cancel import cancel
from keyboards.default.start import start_keyboard
from data.config import loc_photo_worker, loc_photo_foreman, loc_pass_worker, loc_pass_foreman
from database.connect_db import conn, cur, cur1
import datetime
import re
from keyboards.default.worker_job import worker_start_job
from utils.format import format_phone
from states.wait_state import wait, wait_foremane
from states.foreman import foreman
from states.worker import worker
from keyboards.inline.foreman_menu import foreman_menu
from keyboards.inline.worker import worker_menu, worker_menu_company
from keyboards.default.worker_no_job import worker_no_job

subject_task = ""
parent_task = ""
@dp.message_handler(state=worker.start_job)
async def join_session(message: Message, state=FSMContext):
    tgid = message.from_user.id
    cur.execute("select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" %tgid)
    name = cur.fetchall()
    if(not name):
        await message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        await state.update_data(telegramid=tgid, name_worker=name[0][0], name_foreman=name[0][2], telegramidforeman=name[0][1], object=name[0][3], phone_number=name[0][4])
        cur.execute("select phone_number from tabProrab where telegramid=%s" %name[0][1])
        a = cur.fetchall()
        await state.update_data(phone_number_foreman=a[0][0])
        now = datetime.datetime.now()
        await message.answer("Добрый день, сегодня %s число." %now.strftime("%d-%m-%Y"), reply_markup=worker_menu)
        await worker.job.set()
@dp.callback_query_handler(text_contains="serv:Перевести в термины компании", state=worker.job)
async def translate(call: CallbackQuery, state=FSMContext):
    await state.update_data(translate="company")
    print(1)
    await call.message.edit_text("Меню", reply_markup=worker_menu_company)


@dp.callback_query_handler(text_contains="serv:Перевести в термины заказчика", state=worker.job)
async def translate(call: CallbackQuery, state=FSMContext):
    await state.update_data(translate="customer")
    print(2)
    await call.message.edit_text("Меню", reply_markup=worker_menu)


@dp.callback_query_handler(text_contains="serv:Сделать отчет", state=worker.job)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    tgid = call.from_user.id
    cur.execute("select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" % tgid)
    name = cur.fetchall()
    if (not name):
        await call.message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        data = await state.get_data()
        conn.commit()
        print(21)
        cur.execute("select telegramidforeman from tabWorker where telegramid=%s" %call.from_user.id)
        tgid_for = cur.fetchall()
        cur.execute("select object from tabProrab where telegramid=%s" %tgid_for[0][0])
        proj = cur.fetchall()
        print(proj)
        mas = []
        mas.append(proj[0][0])
        print(mas)
        cur.execute("select name from tabTask where is_group='1' and project=?", mas)
        await state.update_data(project=mas)
        section_task = cur.fetchall()
        print(data.get("translate"))
        if(data.get("translate") == "customer"):
            free_work = []
            for i in section_task:
                name_mas = []
                name_mas.append(i[0])
                cur.execute("select term_customer from `tabDictionary reference book` where name=?", name_mas)
                parent = cur.fetchall()
                free_work.append([InlineKeyboardButton(text=parent[0][0], callback_data=i[0])])
            free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
            foreman_btn = InlineKeyboardMarkup(
                inline_keyboard=free_work,
            )
        else:
            free_work = []
            for i in section_task:
                name_mas = []
                name_mas.append(i[0])
                cur.execute("select term_customer, term_worker from `tabDictionary reference book` where name=?", name_mas)
                parent = cur.fetchall()
                print(parent)
                if(parent[0] != "" ):
                    if (parent[0][1] != ""):
                        free_work.append([InlineKeyboardButton(text=parent[0][1], callback_data=i[0])])
                    else:
                        free_work.append([InlineKeyboardButton(text=parent[0][0], callback_data=i[0])])
            free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
            foreman_btn = InlineKeyboardMarkup(
                inline_keyboard=free_work,
            )
        await call.message.edit_text(text="Разделы работ", reply_markup=foreman_btn)
        await worker.section_task.set()

@dp.callback_query_handler(state=worker.section_task)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    tgid = call.from_user.id
    data = await state.get_data()
    cur.execute(
        "select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" % tgid)
    name = cur.fetchall()
    if (not name):
        await call.message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        conn.commit()
        str = call.data
        if (str == "Назад"):
            if(data.get("translate") == "customer"):
                await call.message.edit_text(text="Главное меню", reply_markup=worker_menu)
            else:
                await call.message.edit_text(text="Главное меню", reply_markup=worker_menu_company)
            await worker.job.set()
        else:
            data = await state.get_data()
            if(data.get("translate") == "customer"):
                mas = []
                free_work = []
                mas.append(str)
                cur.execute("select subject, name from tabTask where parent_task=?", mas)
                task = cur.fetchall()
                print(task)
                for i in task:
                    mas1 = []
                    mas1.append(i[1])
                    cur.execute("select term_customer from `tabDictionary reference book` where name=?", mas1)
                    term_customer = cur.fetchall()
                    free_work.append([InlineKeyboardButton(text=term_customer[0][0], callback_data=i[1])])
                free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
                foreman_btn = InlineKeyboardMarkup(
                    inline_keyboard=free_work,
                )
            else:
                mas = []
                free_work = []
                mas.append(str)
                cur.execute("select subject, name from tabTask where parent_task=?", mas)
                task = cur.fetchall()
                print(task)
                for i in task:
                    mas1 = []
                    mas1.append(i[1])
                    cur.execute("select term_customer, term_worker from `tabDictionary reference book` where name=?", mas1)
                    term_customer = cur.fetchall()
                    if(term_customer[0][1]):
                        free_work.append([InlineKeyboardButton(text=term_customer[0][1], callback_data=i[1])])
                    else:
                        free_work.append([InlineKeyboardButton(text=term_customer[0][0], callback_data=i[1])])
                free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
                foreman_btn = InlineKeyboardMarkup(
                    inline_keyboard=free_work,
                )
            cur.execute("select subject from tabTask where name='%s'" %str)
            subject = cur.fetchall()
            await state.update_data(parent_task_name=str, parent_task_subject=subject[0][0])
            await call.message.edit_text(text="Работы в разделе %s" %subject[0][0], reply_markup=foreman_btn)
            await worker.input_task.set()

@dp.callback_query_handler(state=worker.input_task)
async def work(call: CallbackQuery, state=FSMContext):
    conn.commit()
    tgid = call.from_user.id
    cur.execute(
        "select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" % tgid)
    name = cur.fetchall()
    if (not name):
        await call.message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        conn.commit()
        str = call.data
        data = await state.get_data()
        if (str == "Назад"):
            data = await state.get_data()
            conn.commit()
            print(21)
            cur.execute("select telegramidforeman from tabWorker where telegramid=%s" % call.from_user.id)
            tgid_for = cur.fetchall()
            cur.execute("select object from tabProrab where telegramid=%s" % tgid_for[0][0])
            proj = cur.fetchall()
            print(proj)
            mas = []
            mas.append(proj[0][0])
            print(mas)
            cur.execute("select name from tabTask where is_group='1' and project=?", mas)
            await state.update_data(project=mas)
            section_task = cur.fetchall()
            print(data.get("translate"))
            if (data.get("translate") == "customer"):
                free_work = []
                for i in section_task:
                    name_mas = []
                    name_mas.append(i[0])
                    cur.execute("select term_customer from `tabDictionary reference book` where name=?", name_mas)
                    parent = cur.fetchall()
                    free_work.append([InlineKeyboardButton(text=parent[0][0], callback_data=i[0])])
                free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
                foreman_btn = InlineKeyboardMarkup(
                    inline_keyboard=free_work,
                )
            else:
                free_work = []
                for i in section_task:
                    name_mas = []
                    name_mas.append(i[0])
                    cur.execute("select term_customer, term_worker from `tabDictionary reference book` where name=?",
                                name_mas)
                    parent = cur.fetchall()
                    print(parent)
                    if (parent[0] != ""):
                        if (parent[0][1] != ""):
                            free_work.append([InlineKeyboardButton(text=parent[0][1], callback_data=i[0])])
                        else:
                            free_work.append([InlineKeyboardButton(text=parent[0][0], callback_data=i[0])])
                free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
                foreman_btn = InlineKeyboardMarkup(
                    inline_keyboard=free_work,
                )
            await call.message.edit_text(text="Разделы работ", reply_markup=foreman_btn)
            await worker.section_task.set()
        else:
            cur.execute("select subject from tabTask where name='%s'" % str)
            task_name = cur.fetchall()
            await state.update_data(task_name=str, task_subject=task_name[0][0])
            free_work = []
            free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
            foreman_btn = InlineKeyboardMarkup(
                inline_keyboard=free_work,
            )
            await call.message.edit_text(text="Введите объем выполненной работы")
            await worker.reg_report.set()

@dp.message_handler(state=worker.reg_report)
async def free_work(message: Message, state=FSMContext):
    conn.commit()
    tgid = message.from_user.id
    cur.execute(
        "select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" % tgid)
    name = cur.fetchall()
    if (not name):
        await message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        conn.commit()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = await state.get_data()
        mes = message.text
        mas = []
        st = str(datetime.datetime.now()) + " " + str(data.get("task_name") + " " + str(tgid))
        cur.execute("select fio, phone_number, telegramid, foreman, dateobj, telegramidforeman from tabWorker where telegramid=%s" %tgid)
        a = cur.fetchall()
        cur.execute("select phone_number from tabProrab where telegramid=%s" %a[0][5])
        phone_foreman = cur.fetchall()
        mas.append(data.get("task_name"))
        mas.append(st)
        mas.append(datetime.datetime.now())
        mas.append("Administrator")
        mas.append(data.get("task_subject"))
        mas.append(data.get("parent_task_subject"))
        mas.append("")
        mas.append(mes)
        mas.append(a[0][0])
        mas.append(tgid)
        mas.append(a[0][1])
        mas.append(a[0][3])
        mas.append(a[0][5])
        mas.append(phone_foreman[0][0])
        mas.append(now)
        print(mas)
        cur.execute("insert into `tabTemp worker report` (task_name, name ,creation ,owner, "
                    "job, job_section, photo, job_value, worker_name, telegramid, phone_number, foreman_name, telegramidforeman, phone_number_foreman, date)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mas)
        conn.commit()
        await message.answer("Ваш отчёт направлен прорабу")
        free_work = []
        name_parent = [data.get("task_name")]
        cur.execute("select parent_task from tabTask where name=?", name_parent )
        name1 = cur.fetchall()
        print(name1)
        parent_task_mas = [name1[0][0]]
        cur.execute("select subject, name from tabTask where parent_task=?", parent_task_mas )
        if (data.get("translate") == "customer"):
            mas = []
            free_work = []
            mas.append(str)
            cur.execute("select subject, name from tabTask where parent_task=?", parent_task_mas)
            task = cur.fetchall()
            print(task)
            for i in task:
                mas1 = []
                mas1.append(i[1])
                cur.execute("select term_customer from `tabDictionary reference book` where name=?", mas1)
                term_customer = cur.fetchall()
                free_work.append([InlineKeyboardButton(text=term_customer[0][0], callback_data=i[1])])
            free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
            foreman_btn = InlineKeyboardMarkup(
                inline_keyboard=free_work,
            )
        else:
            mas = []
            free_work = []
            mas.append(str)
            cur.execute("select subject, name from tabTask where parent_task=?", parent_task_mas)
            task = cur.fetchall()
            print(task)
            for i in task:
                mas1 = []
                mas1.append(i[1])
                cur.execute("select term_customer, term_worker from `tabDictionary reference book` where name=?", mas1)
                term_customer = cur.fetchall()
                if (term_customer[0][1]):
                    free_work.append([InlineKeyboardButton(text=term_customer[0][1], callback_data=i[1])])
                else:
                    free_work.append([InlineKeyboardButton(text=term_customer[0][0], callback_data=i[1])])
            free_work.append([InlineKeyboardButton(text="Назад", callback_data="Назад")])
            foreman_btn = InlineKeyboardMarkup(
                inline_keyboard=free_work,
            )
        cur.execute("select subject from tabTask where name=?", parent_task_mas)
        subject = cur.fetchall()
        await state.update_data(parent_task_name=str, parent_task_subject=subject[0][0])
        await message.answer(text="Работы в разделе %s" % subject[0][0], reply_markup=foreman_btn)
        await worker.input_task.set()

@dp.callback_query_handler(text_contains="serv:Закончить рабочий день", state=worker.job)
async def end_session(call: CallbackQuery, state=FSMContext):
    conn.commit()
    tgid = call.from_user.id
    cur.execute(
        "select fio, telegramidforeman, foreman, object, phone_number from tabWorker where telegramid=%s" % tgid)
    name = cur.fetchall()
    if (not name):
        await call.message.answer("Вас еще не взяли на работу", reply_markup=worker_no_job)
        await worker.no_job.set()
    else:
        print(220)
        mas = []
        mas.append(datetime.datetime.now().strftime('%Y-%m-%d'))
        mas.append(datetime.datetime.now().strftime('%Y-%m-%d'))
        mas.append(call.from_user.id)
        mes = []
        mes.append(datetime.datetime.now().strftime('%Y-%m-%d'))
        mes.append(tgid)
        cur.execute("select * from `tabWorker activity` where date_join=? and telegramid=?", mes)
        print(mas)
        a = cur.fetchall()
        print(a)
        if(a):
            print(2)
            cur.execute("update `tabWorker activity` set date_end=? where date_join=? and telegramid=?", mas)
            conn.commit()
            await call.message.delete()
            await call.message.answer(text="Вы закончили рабочий день", reply_markup=worker_start_job)
            await state.finish()
        else:
            print(1)
            cur.execute("delete from `tabWorker activity temp` where telegramid=%s" %tgid)
            conn.commit()
            await call.message.delete()
            await call.message.answer(text="Вы закончили рабочий день", reply_markup=worker_start_job)
            await state.finish()

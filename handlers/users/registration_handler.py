import asyncio

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
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
from datetime import datetime
import re
from utils.format import format_phone
from states.wait_state import wait, wait_foremane
from states.worker import worker
from states.foreman import foreman
from keyboards.default.worker_job import worker_start_job
from keyboards.default.foreman_job import foreman_start_job
from loader import bot
mes = ''
@dp.message_handler(text="Зарегистрироваться", state=None)
async def enter_reg(message: Message):
    conn.commit()
    mes = message.from_user.id
    cur.execute("select telegramid from `tabWorker Free` where telegramid=%d" %mes)
    a = cur.fetchall()
    cur.execute("select telegramid from tabWorker where telegramid=%d" % mes)
    b = cur.fetchall()
    if (a or b):
        await message.answer("Вы уже зарегистрированны, либо ваш аккаунт еще не подтвердили.", reply_markup=start_keyboard)
    else:
        await message.answer("При желании вы всегда можете выйти в главное меню, нажав кнопку отмена", reply_markup=cancel)
        await message.answer("Введите ФИО")
        await reg.fio.set()


@dp.message_handler(state=reg.fio)
async def reg_fio(message: Message, state: FSMContext):
    pattern = r'[а-яА-ЯёЁ]+'
    if re.match(pattern, message.text):
        fio = message.text
        await message.answer("Введите номер телефона")
        await state.update_data(fio=fio)
        await reg.phone.set()
        await state.update_data(telegramid=message.from_user.id)
    else:
        await message.answer("Невеный формат\nПожалуйста, вводите ФИО без цифр и только русскими буквами")
        await reg.fio.set()


@dp.message_handler(state=reg.phone)
async def reg_phone(message: Message, state: FSMContext):
    r = message.text
    pattern = r'(\+7|8).*?(\d{3}).*?(\d{3}).*?(\d{2}).*?(\d{2})'
    if re.match(pattern, r):
        phone = message.text
        phone = format_phone(phone)
        await message.answer("Отправьте страницу паспорта с вашим фото и ФИО, как показано на примере ниже")
        await bot.send_photo(message.from_user.id, photo=open('/home/erpnext/UP_ERP_TG/image/example.png', 'rb'))
        await state.update_data(phone=phone)
        await reg.passport.set()
    else:
        await message.answer("Неверный формат номера телефона")
        await message.answer("Пожалуйста, введите номер правильно")
        await reg.phone.set()

@dp.message_handler(state=reg.passport, content_types=['photo'])
async def reg_passport(message, state: FSMContext):
    passport = message.photo[-1]
    await passport.download(destination=loc_pass_worker + "passport_worker" + str(message.from_user.id) + ".jpg")
    await state.update_data(path_pas="/files/pass_worker/passport_worker" + str(message.from_user.id) + ".jpg")
    await message.answer("Отправьте вашу фотографию")
    data = await state.get_data()
    await reg.photo.set()

@dp.message_handler(state=reg.photo, content_types=['photo'])
async def reg_passport(message, state: FSMContext):
    passport = message.photo[-1]
    await passport.download(destination=loc_photo_worker + "photo_worker" + str(message.from_user.id) + ".jpg")
    await state.update_data(path_photo="/files/photo_worker/photo_worker" + str(message.from_user.id) + ".jpg")
    data = await state.get_data()
    await message.answer("Пожалуйста, проверте верна ли введеная информация\n" \
                         "ФИО: " + data.get("fio") + "\n"
                                                     "Номер телефона: " + data.get("phone") + "\n", reply_markup=end_reg)
    await reg.check.set()

@dp.callback_query_handler(text_contains="reg", state=reg.check)
async def reg_check(call: CallbackQuery, state: FSMContext):
    now = datetime.now()
    callback_data = call.data
    mas = []
    data = await state.get_data()
    if callback_data == "reg:True":
        await call.message.answer("Ваша заявка отправленна на рассмотрение оператором, отправьте боту сообщение для проверки статуса вашего аккаунту.", reply_markup=ReplyKeyboardRemove())
        mas.append(data.get("telegramid"))
        mas.append(now)
        mas.append("Administrator")
        mas.append(data.get("fio"))
        mas.append(data.get("phone"))
        mas.append(data.get("telegramid"))
        mas.append(data.get("path_pas"))
        mas.append(data.get("path_photo"))
        cur.execute("INSERT INTO tabEmployer (name ,creation ,owner ,fio ,phone_number ,telegramid ,photo_pass ,photo ) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", mas)
        conn.commit()
        await state.finish()
    else:
        await call.message.answer("Начнём сначала! Введите ФИО.\n")
        await reg.fio.set()


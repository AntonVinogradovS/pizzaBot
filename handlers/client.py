from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client
from database import sqlite_db
from keyboards import client_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import smtplib
from email.mime.text import MIMEText


def send_email(client_email, order):
    sender = "rusantonvin@yandex.ru"
    password = "password"
    server = smtplib.SMTP('smtp.yandex.com', 587)
    server.starttls()
    receipt = f'Ваш заказ:\n{order}\nоформлен. Ожидайте.\nЭто письмо было автоматически сгенерировано, пожалуйста, не отвечайте на него.\
                \nКонтакты для связи: +79100073082, @itmmpmi'
    try:
        server.login(sender, password)
        msg = MIMEText(receipt)
        msg["Subject"] = "Заказ из пиццерии"
        server.sendmail(sender, client_email, msg.as_string())
        return "Письмо отправлено"
    except Exception as _ex:
        return f'{_ex}'



#@dp.message_handler(commands=['start'])
async def cmd_handler(message: types.Message):
    await message.answer("Бот для заказа пиццы", reply_markup=kb_client)


#@dp.message_handler(content_types= types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    await message.answer("Номер получен")


#@dp.message_handler(text="Отправить username")
async def usname(message: types.Message):
    tmp = "@" + message.from_user.username
    await message.answer(tmp)

#@dp.message_handler(text="Контакты")
async def contactInfo(message: types.Message):
    tmp = "Номер телефона: +791011111111"
    #await message.answer(tmp)
    await message.answer(message.from_user.id)

# async def menu(text = "Каталог"):
#     await sqlite_db.sql_read(text)
user_keyboards = {}
async def add_to_cart(message: types.Message):
    read = await sqlite_db.sql_read2()
    for ret in read:
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}\n{ret[-1]}')
        send_message =await bot.send_message(message.from_user.id,text='Выберите действие:', reply_markup= client_kb.inlineAction(ret[1]))
        print(send_message.message_id)
        if message.from_user.id not in user_keyboards:
            user_keyboards[message.from_user.id] = [send_message.message_id]
        else:
            user_keyboards[message.from_user.id].append(send_message.message_id)
        
async def add_button(callback_query: types.CallbackQuery):
    count = callback_query.message.reply_markup.inline_keyboard[0][1].text
    await sqlite_db.sql_add_product(callback_query.from_user.id, callback_query.data.replace('addProduct ', ''), count)
    await callback_query.answer(text=f'{callback_query.data.replace("addProduct ", "")} добавлен в корзину.', show_alert=True)

orderTmp = {}
async def plus_button(callback_query: types.CallbackQuery):
    user = callback_query.from_user.id
    order = callback_query.data.replace('plus ', '')
    s = str(user) + order
    if s not in orderTmp:
        orderTmp[s] = 1
    else:
        orderTmp[s] += 1

    # Получаем текущий текст кнопки счетчика
    #current_text = callback_query.message.reply_markup.inline_keyboard[0][1].text

    # Обновляем текст кнопки счетчика с новым значением
    callback_query.message.reply_markup.inline_keyboard[0][1].text = str(orderTmp[s])

    # Обновляем клавиатуру с измененным текстом кнопки счетчика
    await callback_query.message.edit_reply_markup(reply_markup=callback_query.message.reply_markup)

async def minus_button(callback_query: types.CallbackQuery):
    user = callback_query.from_user.id
    order = callback_query.data.replace('minus ', '')
    s = str(user) + order
    if s not in orderTmp:
        await callback_query.answer(text=f'{callback_query.data.replace("minus ", "")} еще не добавлен в корзину.', show_alert=True)
    else:
        t = orderTmp[s]
        
        if t >= 2:
            orderTmp[s] -= 1
        else:
            del orderTmp[s]

        # Получаем текущий текст кнопки счетчика
        current_text = callback_query.message.reply_markup.inline_keyboard[0][1].text

        # Обновляем текст кнопки счетчика с новым значением
        callback_query.message.reply_markup.inline_keyboard[0][1].text = str(orderTmp[s]) if s in orderTmp else '0'

        # Обновляем клавиатуру с измененным текстом кнопки счетчика
        await callback_query.message.edit_reply_markup(reply_markup=callback_query.message.reply_markup)



async def del_button(callback_query: types.CallbackQuery):
    s = await sqlite_db.sql_del_product(callback_query.from_user.id, callback_query.data.replace('removeProduct ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("removeProduct ", "")} {s}.', show_alert=True)

async def basket_button(callback_query: types.CallbackQuery):
    read = await sqlite_db.sql_basket_product(callback_query.from_user.id)
    if len(read) == 0:
        s = 'Ваша корзина пуста.'
        await bot.send_message(callback_query.from_user.id, s)
    else:  
        s = "Ваша корзина:"
        finalPrice = 0.
        for ret in read:
            s += f'\n{ret[0]} в количестве {ret[1]} шт. Цена: {ret[2]} руб.'
            finalPrice += ret[2]
        s += f'\nИтоговая стоимость: {finalPrice} руб.'
        await bot.send_message(callback_query.from_user.id, s, reply_markup=client_kb.inline_basket_kb)
    print(user_keyboards)
    user_id = callback_query.from_user.id
    message_ids = user_keyboards.get(user_id, [])

    # Удаление клавиатур из всех сообщений для текущего пользователя
    for message_id in message_ids:
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=message_id, reply_markup=None)
    # Очищаем список идентификаторов сообщений для текущего пользователя
    user_keyboards[user_id] = []

async def pay_basket(callback_query: types.CallbackQuery):
    read = await sqlite_db.sql_basket_product(callback_query.from_user.id)
    if len(read) == 0:
        s = 'Ваша корзина пуста.'
    else:
        finalPrice = 0.
        for ret in read:
            finalPrice += ret[2]
        s = f'К оплате: {finalPrice} руб.\nОжидаем перевод по номеру +79100073082 (Сбербанк, Тинькофф)'
    await bot.send_message(callback_query.from_user.id, s)
    
async def order(message: types.Message):
    user = message.from_user.id
    read = await sqlite_db.sql_basket_product(user)
    finalPrice = 0.
    for ret in read:
        # tmp = str(user) + ret[0]
        # del orderTmp[tmp]
        finalPrice += ret[2]
    finalPrice *= 100

    await bot.send_invoice(
        chat_id=message.from_user.id,
        title='Оплата заказа',
        description='Заказ из пиццерии',
        payload='payload Sber',
        provider_token='401643678:TEST:b0438e6a-9877-4935-b6c1-e88732b15c62',
        currency='rub',
        prices = [types.LabeledPrice(label="Product", amount=int(finalPrice))],
        need_phone_number=True,
        need_email=True
    )
    

    
    

#@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    # Обработка предварительного запроса на платеж (например, проверка наличия товара)
    
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)  # ok=True, если все в порядке, иначе False
    #print(pre_checkout_query.order_info)

#@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print(message)
    # Обработка успешного платежа (например, предоставление доступа к контенту)
    await message.answer("Оплата прошла успешно!")
    phone_number = "+" + message.successful_payment.order_info["phone_number"]
    email_adress = message.successful_payment.order_info["email"]
    print(phone_number, email_adress)
    
    ord = await sqlite_db.order_in_processing(message.from_user.id, phone_number, email_adress)
    t = ord.split("\n")
    for i in t:
        #tmp = i.split()
        arr = i.split()
        print(arr)
        tmp = arr[0]
        print(tmp)
        s = str(message.from_user.id) + tmp
        del orderTmp[s]
        print(orderTmp)
    send_email(email_adress, ord)





def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_handler, commands=['start'])
    dp.register_message_handler(contact_handler, content_types= types.ContentType.CONTACT)
    dp.register_message_handler(usname, text="Отправить username")
    dp.register_message_handler(contactInfo, text="Контакты")
    dp.register_message_handler(add_to_cart, text="Каталог")
    dp.register_callback_query_handler(add_button, lambda x: x.data and x.data.startswith('addProduct '), state="*")
    #dp.register_callback_query_handler(del_button, lambda x: x.data and x.data.startswith('removeProduct '), state="*")
    dp.register_callback_query_handler(basket_button, lambda x: x.data and x.data.startswith('basket '), state="*")
    dp.register_callback_query_handler(plus_button, lambda x: x.data and x.data.startswith('plus '), state="*")
    dp.register_callback_query_handler(minus_button, lambda x: x.data and x.data.startswith('minus '), state="*")
    dp.register_callback_query_handler(order, text = 'to_pay')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_successful_payment, content_types=types.ContentType.SUCCESSFUL_PAYMENT)
    dp.register_callback_query_handler(add_to_cart, text = 'go_shopping')
    #dp.register_message_handler(menu, text="Каталог")
    #dp.register_message_handler(echo)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from database import sqlite_db
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
IDAdmin = 1313463136


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()

#@dp.message_handler(commands='moderator', is_chat_admin = True)
async def make_changes_command(message: types.Message):
    ID = message.from_user.id
    print("sefsefsef")
    if ID == IDAdmin:
        print("sefsefsef")
        #await message.reply("Ты мой хозяин")
        await bot.send_message(message.from_user.id,"Ты мой хозяин", reply_markup= admin_kb.button_case_admin)
        await message.delete()

    

#@dp.message_handler(commands = "Загрузить", state=None)
async def cm_start(message: types.Message):
    print("qswswsw")
    if message.from_user.id == IDAdmin:
        await FSMAdmin.photo.set()
        await message.reply("Загрузи фото")
#первый ответ
#@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state = FSMContext):
    if message.from_user.id == IDAdmin:    
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply("Отлично. Теперь введи название")

#второй ответ
#@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state = FSMContext):
    if message.from_user.id == IDAdmin:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply("Замечательно. Укажи описание товара")

#третий ответ
#@dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state = FSMContext):
    if message.from_user.id == IDAdmin:
        async with state.proxy() as data:
            data['description'] = message.text
        await FSMAdmin.next()
        await message.reply("И на последок определись с ценой")


#@dp.message_handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state = FSMContext):
    if message.from_user.id == IDAdmin:
        async with state.proxy() as data:
            data['price'] = float(message.text)
        # async with state.proxy() as data:
        #     await message.reply(str(data))
        await sqlite_db.sql_add_command(state)
        await state.finish()

#Выход из состояний
#@dp.message_handler(state="*", commands='отмена')
#@dp.message_handler(Text(equals = 'отмена', ignore_case = True), state = "*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == IDAdmin:    
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')

async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)

async def delete_item(message: types.Message):
    if message.from_user.id == IDAdmin:
        read = await  sqlite_db.sql_read2()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\n{ret[2]}\n{ret[-1]}')
            await bot.send_message(message.from_user.id, text = '^^^^^', reply_markup = InlineKeyboardMarkup().\
                                   add(InlineKeyboardButton(f'Удалить {ret[1]}', callback_data = f'del {ret[1]}')))
            
async def orders_progress(message: types.Message):
    print('1111')
    if message.from_user.id == IDAdmin:
        read = await sqlite_db.sql_read3()
        for ret in read:
            print(ret)
            await bot.send_message(message.from_user.id, text = f'id заказа: {ret[0]}, id клиента: {ret[1]}, номер телефона: {ret[2]}, почта: {ret[3]},\
                                   состав заказа: {ret[4]}')
            


def register_handlers_admin(dp: Dispatcher):
    
    dp.register_message_handler(cm_start, commands = ['Загрузить'], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    #dp.register_message_handler(cancel_handler, state="*", commands=['отмена'])
    #dp.register_message_handler(cancel_handler,Text(equals = ['отмена'], ignore_case = True), state = "*")
    dp.register_message_handler(make_changes_command, commands=['moderator'], state = None)
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '), state="*")
    dp.register_message_handler(delete_item, state = "*", commands=['Удалить'])
    dp.register_message_handler(orders_progress, commands =['Ожидание'], state="*")
    
    #dp.register_message_handler(make_changes_command, commands='moderator', is_chat_admin = True)
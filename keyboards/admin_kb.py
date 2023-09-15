from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

button_load = KeyboardButton(text="/Загрузить")
button_delete = KeyboardButton(text = "/Удалить")
button_progress = KeyboardButton(text = "/Ожидание")

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load).add(button_delete).add(button_progress)

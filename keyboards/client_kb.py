from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton


kb_client = ReplyKeyboardMarkup(resize_keyboard= True)
b1 = KeyboardButton(text = "Отправить username")
b2 = KeyboardButton(text = "Отправить номер телефона", request_contact= True)
b3 = KeyboardButton(text = "Каталог")
b4 = KeyboardButton(text = "Контакты")
buttonList = [b1,b2,b3,b4]
kb_client.add(*buttonList)


def inlineAction(ret, count = 0):    
    inline_kb_client = InlineKeyboardMarkup(row_width=3)
    inline_kb_client.add(InlineKeyboardButton(text='+', callback_data =f'plus {ret}'))
    inline_kb_client.insert(InlineKeyboardButton(text=count, callback_data =f'count {ret}'))
    inline_kb_client.insert(InlineKeyboardButton(text='-', callback_data =f'minus {ret}'))
    inline_kb_client.add(InlineKeyboardButton(text='Добавить', callback_data =f'addProduct {ret}'))
    inline_kb_client.add(InlineKeyboardButton(text='Корзина', callback_data =f'basket {ret}'))
    return inline_kb_client


inline_basket_kb = InlineKeyboardMarkup(row_width=2)
inline_basket_kb.add(InlineKeyboardButton(text = 'Оплатить', callback_data='to_pay'))
inline_basket_kb.insert(InlineKeyboardButton(text = 'Продолжить выбор товаров', callback_data='go_shopping'))
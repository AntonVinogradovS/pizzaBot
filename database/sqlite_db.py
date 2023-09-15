import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('pizza_cool.db')
    cur = base.cursor()
    if base:
        print("Data base connected OK!")
    base.execute('CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS basketProduct(user TEXT, nameProduct TEXT, count INTEGER DEFAULT 0, price REAL DEFAULT 0.0)')
    base.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user TEXT, phone TEXT, email TEXT, newOrder TEXT)')
    base.commit()
 
async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_read(message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        #await bot.send_photo(message.from_user.id, ret[0], ret[1] + "\n" + ret[2] + "\n" + ret[3] + " рублей")#, reply_markup= admin_kb.button_case_admin)
        await bot.send_photo(message.from_user.id, f'{ret[0]}, {ret[1]}\n{ret[2]}\n{ret[-1]} рублей')

async def sql_read2():
    return cur.execute('SELECT * FROM menu').fetchall()

async def sql_read3():
    return cur.execute('SELECT * FROM orders').fetchall()

async def sql_delete_command(data):
    print(data)
    cur.execute('DELETE FROM menu WHERE name == ?', (data,))
    base.commit()

async def sql_add_product(usName, prodName, count):
    print(prodName)
    cur.execute('SELECT price FROM menu WHERE name == ?', (prodName,))
    priceProd = float(cur.fetchone()[0])
    cur.execute('SELECT count FROM basketProduct WHERE user == ? AND nameProduct == ?', (usName, prodName))
    countTmp = cur.fetchone()
    if countTmp is not None:
        countTmp = int(countTmp[0])
        priceProd *= (countTmp+int(count))
        cur.execute('UPDATE basketProduct SET count = ?, price = ? WHERE user = ? AND nameProduct = ?', (countTmp + int(count), priceProd, usName, prodName))
    else:

        countTmp = int(count)
        tmp = (usName, prodName, countTmp, priceProd*countTmp)
        cur.execute('INSERT INTO basketProduct VALUES (?, ?, ?, ?)', tmp)
    base.commit()

async def sql_del_product(usName, prodName):
    cur.execute('SELECT price FROM menu WHERE name == ?', (prodName,))
    priceProd = float(cur.fetchone()[0])
    cur.execute('SELECT count FROM basketProduct WHERE user == ? AND nameProduct == ?', (usName, prodName))
    countTmp = cur.fetchone()
    print(countTmp)
    if countTmp is not None and countTmp[0] != 0:
        countTmp = int(countTmp[0])
        countTmp -= 1
        priceProd *= countTmp
        if countTmp != 0:
            cur.execute('UPDATE basketProduct SET count = ?, price = ? WHERE user = ? AND nameProduct = ?', (countTmp, priceProd, usName, prodName))
        else:
            cur.execute('DELETE FROM basketProduct WHERE user = ? AND nameProduct = ?', (usName, prodName))
        base.commit()
        return "Удален из корзины"
    else:
        return "Отсутствует в корзине"

async def sql_basket_product(usName):
    cur.execute('SELECT nameProduct, count, price FROM basketProduct WHERE user == ?', (usName,))
    ret = cur.fetchall()
    return ret

async def order_in_processing(usName, phone_number, email):
    cur.execute('SELECT nameProduct, count FROM basketProduct WHERE user == ?', (usName,))
    read = cur.fetchall()
    order = ""
    for ret in read:
        if ret != read[-1]:
            order += f'{ret[0]} - {ret[1]} шт.;\n'
        else:
            order += f'{ret[0]} - {ret[1]} шт.'
    print(order)
    cur.execute('INSERT INTO orders  (user, phone, email, newOrder) VALUES (?,?,?,?)', (usName, phone_number,email, order))
    cur.execute('DELETE FROM basketProduct WHERE user = ?', (usName,))
    base.commit()
    return order




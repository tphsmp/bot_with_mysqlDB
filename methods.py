from aiogram import Bot

import mysql.connector
from classes import Database
import db_settings
from errno import errorcode

# рассчет суммы чисел айдшника пользователя
def get_magic_number(user_id):
    string = list(str(user_id))
    magic_number = 0
    for i in range(len(string)):
        magic_number = magic_number + int(string[i])
    if magic_number > 9:
        magic_number = get_magic_number(magic_number)
    return magic_number


# получение ID пользователя Telegram
def get_uid(message):
    user_id = message.from_user.id
    return user_id


# получение имени пользователя
def get_username(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    name = str(first_name) + ' ' + str(last_name)
    return name


# отправка сообщения администратору при запуске бота
async def on_startup(bot):
    user_id = 673882353
    await bot.send_message(user_id, "Hey master! I'm here again!")

# обработка соединения с БД
def trying_db_connection(db):
    try:
        if db:
            print('DB is connected')
            connection_available = True
            return connection_available
    except mysql.connector.Error as err:
        connection_available = False
        print('Wrong user data') if err.errno == errorcode.ER_ACCESS_DENIED_ERROR else print(
            'DB not found') if err.errno == errorcode.ER_BAD_DB_ERROR else print(err)
        return connection_available

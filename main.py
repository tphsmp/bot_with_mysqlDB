from aiogram import Bot, Dispatcher, executor, types
import mysql.connector

from datetime import datetime

from settings import TOKEN
from methods import *

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


# обработка команды /start
@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    # получение данных для БД
    date = datetime.date(datetime.today())
    time = datetime.strftime(datetime.today(), '%H:%M:%S')

    magic_number = get_magic_number(get_uid(message))

    # создание подключения к базе данных
    db = Database.connect_to_database()

    # проверка соединения с бд
    if (trying_db_connection(db) is True):
        # обработка записи в базу логов
        Database.record_in_log_db(db, message, magic_number, date, time, get_uid(message), get_username(message))

        # запись в базу уникальных пользователей
        Database.record_in_unique_names_db(db, message, date, time, get_uid(message), get_username(message))

        # отправка сообщения пользователю
        if (Database.check_username(db, message, get_uid(message))) == 'USER':
            await bot.send_message(message.from_user.id,
                                   f'Hello, {get_username(message)}! Your user ID is: {get_uid(message)} '
                                   f'and your magic number is: {magic_number}')
        else:
            await bot.send_message(message.from_user.id,
                                   f'Hello, {Database.check_username(db, message, get_uid(message))}! Your user ID is: {get_uid(message)} '
                                   f'and your magic number is: {magic_number}')

    else:
        print('Connection discarded')


# обработка команды /changename
@dp.message_handler(commands=['changename'])
async def command_changename(message: types.Message):
    mess = message.text
    await message.reply('Type in the new name') if mess == '/changename' \
        else await message.reply("Please type in only '/changename'")


    @dp.message_handler()
    async def new_name(message: types.Message):
        new_n = message.text

        db = Database.connect_to_database()

        if "'" in new_n or '"' in new_n:
            await bot.send_message(message.from_user.id, "Пиши нормально без непонятных символов типа \' или \" ")
        else:
            if (trying_db_connection(db) is True):

                try:
                    cursor = db.cursor()
                    request = f"UPDATE users_ SET assigned_name = '{new_n}' WHERE user_id = {get_uid(message)}"
                    cursor.execute(request)
                    db.commit()

                    with open(r'log.txt', 'a') as file:
                        file.write(
                            '>>>> Username was changed: ' + str(get_username(message)) + ' to ' + Database.check_username(db, message, get_uid(message))
                            + '>>>> record done\n')

                except mysql.connector.Error as err:
                    # print('Unable to make a record in db for some reasons, check errors below: ', err)
                    with open(r'log.txt', 'a') as file:
                        file.write(
                            '>>>> An error occured while adding assigned_name: ' + ' ' + str(err) + '\n')

                finally:
                    if db:
                        db.close()

            else:
                print('Connection discarded')


            # отправка ссобщения с новым именем
            await message.reply(
                f"So, from now on you're: {new_n} with id {get_uid(message)} unless you change your name again")


if __name__ == '__main__':
    executor.start(dp, on_startup(bot))
    executor.start_polling(dp, skip_updates=True)

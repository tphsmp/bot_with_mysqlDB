from aiogram import Bot, Dispatcher, executor, types
import mysql.connector
from errno import errorcode
from datetime import datetime

from settings import TOKEN
import db_settings

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


# рассчет суммы чисел айдшника пользователя
def get_magic_number(user_id):
    string = list(str(user_id))
    magic_number = 0
    for i in range(len(string)):
        magic_number = magic_number + int(string[i])

    if magic_number > 9:
        magic_number = get_magic_number(magic_number)
    return magic_number


def connect_to_database():
    connection = mysql.connector.connect(
        host=db_settings.host,
        port=db_settings.port,
        user=db_settings.user,
        passwd=db_settings.passwd,
        database=db_settings.database
    )
    return connection


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    date = datetime.date(datetime.today())
    time = datetime.strftime(datetime.today(), '%H:%M:%S')

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    magic_number = get_magic_number(user_id)
    print(magic_number)

    database = connect_to_database()

    try:
        if database:
            print('DB is connected')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Wrong user data!')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('DB not found!')
        else:
            print(err)

    try:
        cursor = database.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS visitors '
                       '(user_id INTEGER(12), '
                       'first_name VARCHAR(255), '
                       'last_name VARCHAR(255), '
                       'magic_number INTEGER(1), '
                       'visit_date DATE NOT NULL, '
                       'visit_time TIME NOT NULL)')
        db_record = 'INSERT INTO visitors (user_id, ' \
                    'first_name, ' \
                    'last_name, ' \
                    'magic_number, ' \
                    'visit_date, ' \
                    'visit_time) VALUES (%s, %s, %s, %s, %s, %s)'
        values_for_db = (user_id, first_name, last_name, magic_number, date, time)
        cursor.execute(db_record, values_for_db)
        database.commit()
        with open(r'log.txt', 'a') as file:
            file.write('>>>> ' + str(first_name) + ' ' + str(last_name) + ' record done\n')
    except mysql.connector.Error as err:
        print('Unable to make a record in db for some reasons, check errors below: ', err)
        with open(r'log.txt', 'a') as file:
            file.write('>>>> ' + str(first_name) + ' ' + str(last_name) + ' record error: ' + str(err) + '\n')
    finally:
        if database:
            database.close()

    await bot.send_message(message.from_user.id,
                           f'Hello {first_name} {last_name}! Your user ID is: {user_id} '
                           f'and your magic number is: {magic_number}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

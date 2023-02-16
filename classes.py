import mysql.connector

import db_settings
from methods import *

class Database:

# подключение к базе данных
    @classmethod
    def connect_to_database(cls):
        connection = mysql.connector.connect(
            host=db_settings.host,
            port=db_settings.port,
            user=db_settings.user,
            passwd=db_settings.passwd,
            database=db_settings.database,
            consume_results=True
        )
        return connection


    # проверка назначенного имени пользователя из БД
    @classmethod
    def check_username(cls, database, message, user_id):
        result = ''
        try:
            cursor = database.cursor()
            request = f"SELECT assigned_name FROM users_ WHERE user_id = {user_id}"
            cursor.execute(request)
            result = cursor.fetchone()[0]
            cursor.close()
            return result
        except mysql.connector.Error as err:
            print('There was an error during username cheking: ', err)

        return result


    # запись в таблицу логов времени обращения к боту
    @classmethod
    def record_in_log_db(cls, db, message, magic_number, date, time, user_id, username):
        try:
            cursor = db.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS visitors '
                           '(user_id INTEGER(12), '
                           'first_name VARCHAR(255), '
                           'last_name VARCHAR(255), '
                           'magic_number INTEGER(1), '
                           'visit_date DATE NOT NULL, '
                           'visit_time TIME NOT NULL)')

            visitors_db_record = 'INSERT INTO visitors (user_id, ' \
                                 'first_name, ' \
                                 'last_name, ' \
                                 'magic_number, ' \
                                 'visit_date, ' \
                                 'visit_time) VALUES (%s, %s, %s, %s, %s, %s)'

            values_for_visitors_db = (
                user_id, message.from_user.first_name, message.from_user.last_name, magic_number, date, time)

            cursor.execute(visitors_db_record, values_for_visitors_db)

            db.commit()

            with open(r'log.txt', 'a') as file:
                file.write('>>>> Recording userdata in database: ' + str(date) + ' ' + str(time) + ' ' + username + '>>>> record done\n')

        except mysql.connector.Error as err:
            # print('Unable to make a record in db for some reasons, check errors below: ', err)
            with open(r'log.txt', 'a') as file:
                file.write(
                    '>>>> Recording error' + str(date) + ' ' + str(time) + ' ' + username + ' >>>> ' + str(
                        err) + '\n')


    # запись ID и назначенного имени пользователя в таблицу уникальных значений
    @classmethod
    def record_in_unique_names_db(cls, db, message, date, time, user_id, user_name):

        try:
            cursor = db.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS users_ (user_id INTEGER(12), "
                f"first_name VARCHAR(255), "
                f"assigned_name VARCHAR(255) DEFAULT 'USER', CONSTRAINT unique_id UNIQUE (user_id))")

            users_db_record = 'INSERT INTO users_ (user_id, first_name) VALUES (%s, %s)'
            values_for_users_db = (user_id, user_name)
            cursor.execute(users_db_record, values_for_users_db)
            db.commit()
            with open(r'log.txt', 'a') as file:
                file.write(
                    '>>>> Recording unique userdata in database: ' + str(date) + ' ' + str(time) + ' ' + user_name + '>>>> record done\n')

        except mysql.connector.Error as err:
            with open(r'log.txt', 'a') as file:
                file.write('>>>> Unique userdata recording error' + str(date) + ' ' + str(time) + ' ' + user_name + ' >>>> '
                           + str(err) + '\n')




TOKEN = ''

import mysql.connector
database = mysql.connector.connect(
    host='localhost',
    port='3305',
    user='root',
    passwd='123456',
    database='prattler_bot_db')
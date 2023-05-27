import sqlite3
from sqlite3 import Error


def main(db_file):

    create_weather_forecast_table = """ CREATE TABLE IF NOT EXISTS graphs(
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        graph BLOB,
                                        city_name text
                                        ); """

    conn = create_connection(db_file)

    if conn is not None:
        create_table(conn, create_weather_forecast_table)
        return conn
    else:
        print("Error when connecting to db")
    
    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


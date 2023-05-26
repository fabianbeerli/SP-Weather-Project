import sqlite3
from sqlite3 import Error


def main():
    database = r"weather_db.db"
    create_weather_snapshot_table = """ CREATE TABLE IF NOT EXISTS weather_snapshots (
                                            id integer PRIMARY KEY,
                                            city_name text NOT NULL,
                                            curr_temp real NOT NULL,
                                            max_temp real NOT NULL,
                                            min_temp real NOT NULL,
                                            sea_level integer NOT NULL,
                                            humidity text NOT NULL,
                                            sunrise text NOT NULL,
                                            sunset text NOT NULL
                                        ); """

    create_weather_forecast_table = """ CREATE TABLE IF NOT EXISTS weather_forecasts (
                                            id integer PRIMARY KEY,
                                            forecast_city_name text NOT NULL,
                                            forecast_curr_temp real NOT NULL,
                                            forecast_max_temp real NOT NULL,
                                            forecast_min_temp real NOT NULL,
                                            forecast_sea_level integer NOT NULL,
                                            forecast_humidity text NOT NULL,
                                            forecast_sunrise text NOT NULL,
                                            forecast_sunset text NOT NULL,
                                            forecast_date text NOT NULL
                                        ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, create_weather_snapshot_table)
        create_table(conn, create_weather_forecast_table)
    else:
        print("Error when connecting to db")


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

if __name__ == '__main__':  
    main()

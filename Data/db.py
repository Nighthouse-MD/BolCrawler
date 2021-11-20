import sqlite3
from sqlite3 import Error
from Constants import Constants
from .productToTrack import create_productToTrack
from datetime import datetime


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_db(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def alter_table(conn, alter_table_sql):
    """ alter a table from the alter_table_sql statement
    :param conn: Connection object
    :param alter_table_sql: a ALTER TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(alter_table_sql)
    except Error as e:
        print(e)


def migrate():
    sql_create_productToTrack_table = """ CREATE TABLE IF NOT EXISTS productToTrack (
                                        id integer PRIMARY KEY,
                                        productId text NOT NULL,
                                        name text NOT NULL,
                                        fetchedOn DATETIME,
                                        fetchedByCategoryId text
                                    ); """

    sql_alter_productToTrack_table = """ ALTER TABLE productToTrack
                                        ADD COLUMN inactive bool
                                    """

    sql_create_productSnapshot_table = """ CREATE TABLE IF NOT EXISTS productSnapshot (
                                        id integer PRIMARY KEY,
                                        productToTrackId text NOT NULL,
                                        trackedOn DATETIME NOT NULL,
                                        sellerId text NOT NULL,
                                        price DOUBLE NOT NULL,
                                        stockAmount integer NOT NULL,
                                        FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
                                    ); """

    sql_create_dailyParse_table = """ CREATE TABLE IF NOT EXISTS dailyParse (
                                        id integer PRIMARY KEY,
                                        productToTrackId text NOT NULL,
                                        sellerId text NOT NULL,
                                        dayStart DATETIME NOT NULL,
                                        dayEnd DATETIME NOT NULL,
                                        revenue DOUBLE NOT NULL,
                                        avgPrice DOUBLE NOT NULL,
                                        unitsSold integer NOT NULL,
                                        stockIncreaseSize integer NOT NULL,
                                        FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
                                    ); """

    sql_create_dailyParseCompleted_table = """ CREATE TABLE IF NOT EXISTS dailyParseCompleted (
                                        id integer PRIMARY KEY,
                                        dayStart DATETIME NOT NULL,
                                        completedOn DATETIME NOT NULL,
                                        error text
                                    ); """

    sql_alter_dailyParse_table = """ ALTER TABLE dailyParse
                                     ADD COLUMN currentStock integer
                                    """

    sql_alter_productToTrack_table_add_inactivatedOn = """ ALTER TABLE productToTrack
                                        ADD COLUMN inactivatedOn DATETIME
                                    """

    # create a database connection
    create_db(Constants.DB_PATH)
    conn = create_connection(Constants.DB_PATH)

    # create tables
    if conn is not None:
        try:
            create_table(conn, sql_create_productToTrack_table)
            create_table(conn, sql_create_productSnapshot_table)
            create_table(conn, sql_create_dailyParse_table)
            alter_table(conn, sql_alter_productToTrack_table)
            # create_table(conn, sql_create_dailyParseCompleted_table)
            alter_table(conn, sql_alter_dailyParse_table)
            alter_table(conn, sql_alter_productToTrack_table_add_inactivatedOn)
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")

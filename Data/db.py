import sqlite3
from sqlite3 import Error
from Constants import Constants
from datetime import datetime
from Data.trackerDB.productToTrack import list_all, updateEan_productToTrack
import requests


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


def isEanMissing(product):
    return product[7] == None


def checkForMissingEans():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    trackedProducts = list_all(conn)
    productsWithMissingEan = list(filter(isEanMissing, trackedProducts))

    for i in range(len(productsWithMissingEan)):
        try:
            productId = productsWithMissingEan[i][1]
            resp = requests.get(
                'https://api.bol.com/catalog/v4/products/{}?apikey={}&offers=cheapest&includeAttributes=false&format=json'.format(productId, Constants.BOL_API_KEY))

            if resp.status_code != 200:
                # This means something went wrong.
                raise ApiError('GET /lists/ {}'.format(categoryId))

            productEan = resp.json()['products'][0]['ean']
            updateEan_productToTrack(conn, productId, productEan)
        except Error as e:
            print(e)


def migrateTrackerDB():
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

    sql_alter_productToTrack_table_add_ean = """ ALTER TABLE productToTrack
                                        ADD COLUMN ean text
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

    sql_create_scraperLog_table = """ CREATE TABLE IF NOT EXISTS scraperLog (
                                        id integer PRIMARY KEY,
                                        loggedOn DATETIME NOT NULL,
                                        level text NOT NULL,
                                        message text NOT NULL,
                                        exceptionType text NULL,
                                        exception text NULL,
                                        stackTrace text NOT NULL
                                    ); """

    sql_alter_dailyParse_table_add_parsedOn = """ ALTER TABLE dailyParse
                                        ADD COLUMN parsedOn DATETIME
                                    """

    sql_alter_dailyParse_table_add_parsedOn = """ ALTER TABLE dailyParse
                                        ADD COLUMN parsedOn DATETIME
                                    """

    sql_alter_dailyParse_table_add_sellerName = """ ALTER TABLE dailyParse
                                        ADD COLUMN sellerName text
                                    """

    sql_alter_productSnapshot_table_add_sellerName = """ ALTER TABLE productSnapshot
                                        ADD COLUMN sellerName text
                                    """

    sql_alter_dailyParse_table_add_ean = """ ALTER TABLE dailyParse
                                        ADD COLUMN ean text
                                    """

    sql_alter_dailyParse_table_add_type = """ ALTER TABLE dailyParse
                                        ADD COLUMN type text
                                    """

    # create a database connection
    create_db(Constants.BOLDER_TRACKER_DB_PATH)
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)

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
            create_table(conn, sql_create_scraperLog_table)
            alter_table(conn, sql_alter_dailyParse_table_add_parsedOn)
            alter_table(conn, sql_alter_dailyParse_table_add_sellerName)
            alter_table(conn, sql_alter_productSnapshot_table_add_sellerName)
            alter_table(conn, sql_alter_productToTrack_table_add_ean)
            alter_table(conn, sql_alter_dailyParse_table_add_ean)
            alter_table(conn, sql_alter_dailyParse_table_add_type)
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")


def migrateApiDB():
    sql_create_apiUser_table = """ CREATE TABLE IF NOT EXISTS apiUser (
                                        id text PRIMARY KEY,
                                        name text NOT NULL,
                                        createdOn DATETIME,
                                        clientApplication text NOT NULL,
                                        inactive bool
                                    ); """

    sql_create_request_table = """ CREATE TABLE IF NOT EXISTS request (
                                        id integer PRIMARY KEY,
                                        apiUserId text NOT NULL,
                                        url text NOT NULL,
                                        body text NOT NULL,
                                        requestedOn DATETIME
                                    ); """

    # create a database connection
    create_db(Constants.BOLDER_API_DB_PATH)
    conn = create_connection(Constants.BOLDER_API_DB_PATH)

    # create tables
    if conn is not None:
        try:
            create_table(conn, sql_create_apiUser_table)
            create_table(conn, sql_create_request_table)
        except Error as e:
            print(e)
    else:
        print("Error! cannot create the database connection.")

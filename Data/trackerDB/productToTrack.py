from datetime import datetime
from datetime import date, timedelta


def list_all_active(conn):
    """
    Query all rows in the productToTrack table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(""" SELECT * FROM productToTrack
                    WHERE inactive <> 1
                    OR inactive is null""")
    rows = cur.fetchall()
    return rows


def list_all_untracked_productIds_today(conn):
    cur = conn.cursor()
    conn.row_factory = lambda cursor, row: row[0]
    cur.execute("""SELECT id
                FROM productToTrack
                where inactive is null
                and id not in (SELECT distinct producttotrackid
                FROM productSnapshot
                where trackedOn > '""" + str(datetime.now() - timedelta(hours=12)) + """')""")
    rows = cur.fetchall()
    rows = list(map(lambda x: x[0], rows))
    return rows


def inactivate_productToTrack(conn, productId, reason="manually inactivated"):
    cur = conn.cursor()
    cur.execute(
        '''UPDATE productToTrack SET inactive = 1, inactivatedOn = ?, reasonForInactivating = ? WHERE id = ?''', (datetime.now(), reason, productId))
    conn.commit()


def inactivate_productToTrack_byEan(conn, ean, reason="manually inactivated"):
    cur = conn.cursor()
    cur.execute(
        '''UPDATE productToTrack SET inactive = 1, inactivatedOn = ?, reasonForInactivating = ? WHERE ean = ? AND inactive is not 1''', (datetime.now(), reason, ean))
    conn.commit()


def updateEan_productToTrack(conn, productId, ean):
    cur = conn.cursor()
    cur.execute(
        '''UPDATE productToTrack SET ean = ? WHERE productId = ?''', (ean, productId))
    conn.commit()


def create_productToTrack(conn, product):
    """
    Create a new productToTrack into the productToTrack table: param conn:: param productToTrack: : return: productToTrack id
    """
    sql = ''' INSERT INTO productToTrack(productId,ean,name,fetchedOn,fetchedByCategoryId)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, product)
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS productToTrack(
    id integer PRIMARY KEY,
    productId text NOT NULL,
    name text NOT NULL,
    fetchedOn DATETIME,
    fetchedByCategoryId text
); """

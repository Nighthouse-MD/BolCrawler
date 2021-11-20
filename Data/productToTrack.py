from datetime import datetime


def list_all(conn):
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


def inactivate_productToTrack(conn, productId):
    cur = conn.cursor()
    cur.execute(
        '''UPDATE productToTrack SET inactive = 1, inactivatedOn = ? WHERE id = ?''', (datetime.now(), productId))
    conn.commit()


def create_productToTrack(conn, product):
    """
    Create a new productToTrack into the productToTrack table: param conn:: param productToTrack: : return: productToTrack id
    """
    sql = ''' INSERT INTO productToTrack(productId,name,fetchedOn,fetchedByCategoryId)
              VALUES(?,?,?,?) '''
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

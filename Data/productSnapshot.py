def list_all_by_productId(conn, productId):
    """
    Query all rows in the productSnapshot table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM productSnapshot WHERE productToTrackId = " + str(productId))
    rows = cur.fetchall()
    return rows


def list_all_by_productId_from_date(conn, productId, fromDay):
    """
    Query all rows in the productSnapshot table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM productSnapshot WHERE productToTrackId = ? AND trackedOn > '" + fromDay + "%'",
                (str(productId),))
    rows = cur.fetchall()
    return rows


def create_productSnapshot(conn, productSnapshot):
    """
    Create a new productSnapshot into the productSnapshot table
    :param conn:
    :param productSnapshot:
    :return: productSnapshot id
    """
    sql = ''' INSERT INTO productSnapshot(productToTrackId,trackedOn,sellerId,sellerName,price,stockAmount)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, productSnapshot)
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS productSnapshot (
    id integer PRIMARY KEY,
    productToTrackId text NOT NULL,
    trackedOn DATETIME NOT NULL,
    sellerId text NOT NULL,
    sellerName text NOT NULL,
    price DOUBLE NOT NULL,
    stockAmount integer NOT NULL,
    FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
); """

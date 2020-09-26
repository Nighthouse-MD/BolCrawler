def create_productSnapshot(conn, productSnapshot):
    """
    Create a new productSnapshot into the productSnapshot table
    :param conn:
    :param productSnapshot:
    :return: productSnapshot id
    """
    sql = ''' INSERT INTO productSnapshot(productToTrackId,trackedOn,sellerId,price,stockAmount)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, productSnapshot)
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS productSnapshot (
    id integer PRIMARY KEY,
    productToTrackId text NOT NULL,
    trackedOn DATETIME NOT NULL,
    sellerId text NOT NULL,
    price DOUBLE NOT NULL,
    stockAmount integer NOT NULL,
    FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
); """

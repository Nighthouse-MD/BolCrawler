def list_all(conn):
    """
    Query all rows in the productToTrack table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM productToTrack")
    rows = cur.fetchall()
    return rows


def create_productToTrack(conn, product):
    """
    Create a new productToTrack into the productToTrack table
    :param conn:
    :param productToTrack:
    :return: productToTrack id
    """
    sql = ''' INSERT INTO productToTrack(productId,name,fetchedOn,fetchedByCategoryId)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, product)
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS productToTrack (
    id integer PRIMARY KEY,
    productId text NOT NULL,
    name text NOT NULL,
    fetchedOn DATETIME,
    fetchedByCategoryId text
); """

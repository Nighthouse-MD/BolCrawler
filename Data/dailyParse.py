from datetime import datetime


class DailyParse:
    def __init__(self, productToTrackId, sellerId):
        self.productToTrackId = productToTrackId
        self.sellerId = sellerId
        self.dayStart = None
        self.dayEnd = None
        self.revenue = 0
        self.avgPrice = 0
        self.unitsSold = 0
        self.stockIncreaseSize = 0
        self.currentStock = 0
        self.parsedOn = datetime.now()

    def toTuple(self):
        return (self.avgPrice, self.dayStart, self.dayEnd, self.productToTrackId, self.revenue, self.sellerId, self.stockIncreaseSize, self.unitsSold, self.parsedOn)


def create_dailyParse(conn, dailyParse: DailyParse):
    """
    Create a new dailyParse into the dailyParse table
    :param conn:
    :param dailyParse:
    :return: dailyParse id
    """
    sql = ''' INSERT INTO dailyParse(avgPrice,dayStart,dayEnd,productToTrackId,revenue,sellerId,stockIncreaseSize,unitsSold,parsedOn)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, dailyParse.toTuple())
    conn.commit()
    return cur.lastrowid


def delete_dailyParse_byProductToTrackId(conn, productToTrackId):
    sql = ''' DELETE FROM dailyParse
      WHERE productToTrackId=? '''
    cur = conn.cursor()
    cur.execute(sql, (str(productToTrackId),))
    conn.commit()
    return cur.lastrowid


def delete_dailyParse_byProductToTrackId_fromDate(conn, productToTrackId, fromDay):
    sql = " DELETE FROM dailyParse WHERE productToTrackId = ? AND dayStart > '" + \
        fromDay + "%' "
    cur = conn.cursor()
    cur.execute(sql, (str(productToTrackId),))
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS dailyParse (
    id integer PRIMARY KEY,
    productToTrackId text NOT NULL,
    sellerId text NOT NULL,
    dayStart DATETIME NOT NULL,
    dayEnd DATETIME NOT NULL,
    revenue DOUBLE NOT NULL,
    avgPrice DOUBLE NOT NULL,
    unitsSold integer NOT NULL,
    stockIncreaseSize integer NOT NULL,
    parsedOn DATETIME NOT NULL,
    FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
); """

from datetime import datetime


class DailyParse:
    def __init__(self, productToTrackId, sellerId, sellerName, ean, type):
        self.productToTrackId = productToTrackId
        self.sellerId = sellerId
        self.sellerName = sellerName
        self.dayStart = None
        self.dayEnd = None
        self.revenue = 0
        self.avgPrice = 0
        self.unitsSold = 0
        self.stockIncreaseSize = 0
        self.currentStock = 0
        self.parsedOn = datetime.now()
        self.ean = ean
        self.type = type

    def toTuple(self):
        return (self.avgPrice, self.dayStart, self.dayEnd, self.productToTrackId, self.ean, self.revenue, self.sellerId, self.sellerName, self.stockIncreaseSize, self.unitsSold, self.currentStock, self.parsedOn, self.type)


def create_dailyParse(conn, dailyParse: DailyParse):
    """
    Create a new dailyParse into the dailyParse table
    :param conn:
    :param dailyParse:
    :return: dailyParse id
    """
    sql = ''' INSERT INTO dailyParse(avgPrice,dayStart,dayEnd,productToTrackId,ean,revenue,sellerId,sellerName,stockIncreaseSize,unitsSold,currentStock,parsedOn,type)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, dailyParse.toTuple())
    conn.commit()
    return cur.lastrowid


def create_dailyParseList(conn, dailyParses):
    sql = ''' INSERT INTO dailyParse(avgPrice,dayStart,dayEnd,productToTrackId,ean,revenue,sellerId,sellerName,stockIncreaseSize,unitsSold,currentStock,parsedOn,type)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.executemany(
        sql, list(map(lambda x: x.toTuple(), dailyParses)))
    conn.commit()
    return


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


def delete_dailyParse_byProductToTrackIds(conn, productToTrackIds):

    cur = conn.cursor()
    productIds = str(productToTrackIds)[1:][:-1]
    sql = ''' DELETE FROM dailyParse
        WHERE productToTrackId in (''' + productIds + ''') '''
    cur.execute(sql, ())
    conn.commit()
    return cur.lastrowid


def delete_dailyParse_byProductToTrackIds_fromDate(conn, productToTrackIds, fromDay):
    sql = " DELETE FROM dailyParse WHERE productToTrackId in (?) AND dayStart > '" + \
        fromDay + "%' "
    cur = conn.cursor()
    productIds = str(productToTrackIds)[1:][:-1]
    cur.execute(sql, (productIds,))
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS dailyParse (
    id integer PRIMARY KEY,
    productToTrackId text NOT NULL,
    sellerId text NOT NULL,
    sellerName text,
    dayStart DATETIME NOT NULL,
    dayEnd DATETIME NOT NULL,
    revenue DOUBLE NOT NULL,
    avgPrice DOUBLE NOT NULL,
    unitsSold integer NOT NULL,
    stockIncreaseSize integer NOT NULL,
    parsedOn DATETIME NOT NULL,
    FOREIGN KEY(productToTrackId) REFERENCES productToTrack(id)
); """

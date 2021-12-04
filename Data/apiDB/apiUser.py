from datetime import datetime


class ApiUser:
    def __init__(self, productToTrackId, sellerId, sellerName, ean, type):
        self.name = productToTrackId
        self.createdOn = sellerId
        self.clientApplication = sellerName
        self.inactive = False

    def toTuple(self):
        return (self.name, self.createdOn, self.clientApplication, self.inactive)


def getActiveUser(conn, userId):
    cur = conn.cursor()
    cur.execute("SELECT * FROM apiUser WHERE inactive <> 1 AND id = ?",
                (str(userId),))
    rows = cur.fetchall()
    return rows


""" CREATE TABLE IF NOT EXISTS apiUser (
                                        id text PRIMARY KEY,
                                        name text NOT NULL,
                                        createdOn DATETIME,
                                        clientApplication text NOT NULL
                                    ); """

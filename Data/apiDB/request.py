from datetime import datetime, date, timedelta


class Request:
    def __init__(self, apiUserId, url, body, requestedOn):
        self.apiUserId = apiUserId
        self.url = url
        self.body = body
        self.requestedOn = requestedOn

    def toTuple(self):
        return (self.apiUserId, self.url, self.body, self.requestedOn)


def getAllFromLast2Weeks(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM request WHERE requestedOn > " +
                (date.today() - timedelta(days=14)).strftime('%Y-%m-%d'))
    rows = cur.fetchall()
    return rows


""" CREATE TABLE IF NOT EXISTS request (
                                        id integer PRIMARY KEY,
                                        apiUserId text NOT NULL,
                                        url text NOT NULL,
                                        body text NOT NULL,
                                        requestedOn DATETIME
                                    ); """

from datetime import date, datetime


class ScraperLog:
    def __init__(self, message, level, exceptionType, exception, stackTrace):
        self.message = message
        self.level = level
        self.exceptionType = exceptionType
        self.exception = str(exception)
        self.stackTrace = str(stackTrace)
        self.loggedOn = datetime.now()


def toTuple(self):
    return (self.loggedOn, self.level, self.message, self.exceptionType, self.exception, self.stackTrace)


def create_log(conn, log: ScraperLog):
    sql = ''' INSERT INTO scraperLog(loggedOn,level,message,exceptionType,exception,stackTrace)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, toTuple(log))
    conn.commit()
    return cur.lastrowid


""" CREATE TABLE IF NOT EXISTS scraperLog (
    id integer PRIMARY KEY,
    loggedOn DATETIME NOT NULL,
    level text NOT NULL,
    message text NOT NULL,
    exception text NULL,
    stackTrace text NOT NULL
); """

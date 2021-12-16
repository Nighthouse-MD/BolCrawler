
# from Data import db

from Grinder.DailySnapshotGrinder import parseSnapshotsForDaily
from Data.trackerDB.productToTrack import list_all_active
from Data.db import create_connection
from Constants import Constants
from Data.trackerDB.scraperLog import ScraperLog, create_log
from Data.trackerDB.dailyParse import DailyParse, create_dailyParseList, delete_dailyParse_byProductToTrackIds, delete_dailyParse_byProductToTrackIds_fromDate
from datetime import date, timedelta


def batchList(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def run():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    create_log(conn, ScraperLog(
        f'GRINDER START', 'Info', None, None, None))
    trackedProducts = list_all_active(conn)

    statsToSave = []

    for i in range(len(trackedProducts)):
        statsToSave = statsToSave + parseSnapshotsForDaily(
            trackedProducts[i][0], trackedProducts[i][7], Constants.DAILY_PARSE_ALL)

    batchedStats = list(batchList(statsToSave, 500))

    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)

    productIds = list(map(lambda x: x[0], trackedProducts))
    if(Constants.DAILY_PARSE_ALL):
        delete_dailyParse_byProductToTrackIds(conn, productIds)
    else:
        fromDate = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        delete_dailyParse_byProductToTrackIds_fromDate(
            conn, productIds, fromDate)

    for batch in batchedStats:
        create_dailyParseList(conn, batch)

    create_log(conn, ScraperLog(
        f'GRINDER DONE', 'Info', None, None, None))

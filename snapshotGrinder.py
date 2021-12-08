
# from Data import db

from Grinder.DailySnapshotGrinder import parseSnapshotsForDaily
from Data.trackerDB.productToTrack import list_all
from Data.db import create_connection
from Constants import Constants
from Data.trackerDB.scraperLog import ScraperLog, create_log


def run():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    create_log(conn, ScraperLog(
        f'GRINDER START', 'Info', None, None, None))
    trackedProducts = list_all(conn)

    for i in range(len(trackedProducts)):
        parseSnapshotsForDaily(
            trackedProducts[i][0], trackedProducts[i][7], Constants.DAILY_PARSE_ALL)

    create_log(conn, ScraperLog(
        f'GRINDER DONE', 'Info', None, None, None))


# from Data import db

from Grinder.DailySnapshotGrinder import parseSnapshotsForDaily
from Data.trackerDB.productToTrack import list_all
from Data.db import create_connection
from Constants import Constants
import pandas


def run():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    trackedProducts = list_all(conn)

    for i in range(len(trackedProducts)):
        parseSnapshotsForDaily(
            trackedProducts[i][0], trackedProducts[i][7], Constants.DAILY_PARSE_ALL)

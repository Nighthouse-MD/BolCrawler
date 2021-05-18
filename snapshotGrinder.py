
# from Data import db

from Grinder.DailySnapshotGrinder import parseSnapshotsForDaily
from Data.productToTrack import list_all
from Data.db import create_connection
from Constants import Constants
import pandas


def run():
    conn = create_connection(Constants.DB_PATH)
    trackedProducts = list_all(conn)

    # testvar = pandas.DataFrame(trackedProducts)
    # print(testvar)

    for i in range(len(trackedProducts)):
        parseSnapshotsForDaily(trackedProducts[i][0])
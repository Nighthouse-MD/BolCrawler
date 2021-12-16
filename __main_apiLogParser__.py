import stockCrawler
import snapshotGrinder
from Data.db import create_db
from Constants import Constants
from Data.apiDB.request import getAllFromLast2Weeks
from Data.db import create_connection
from Data.trackerDB.productToTrack import inactivate_productToTrack_byEan, list_all_active
import json

if __name__ == '__main__':
    apiDbConn = create_connection(Constants.BOLDER_API_DB_PATH)
    logs = getAllFromLast2Weeks(apiDbConn)

    statLogs = list(filter(lambda x: x[2].find(
        'productStatistics') > -1, logs))

    logBodysAsJson = list(map(lambda x: json.loads(x[3]), statLogs))

    trackedEans = []

    for body in logBodysAsJson:
        if 'eans' in body:
            eans = body['eans']
            for ean in eans:
                trackedEans.append(ean)
        else:
            print('hey')

    requestedEans = list(set(trackedEans))

    trackerDbConn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    allActiveEans = list(
        map(lambda x: x[7], list_all_active(trackerDbConn)))   # deactivate these

    eansToDeactivate = list(
        filter(lambda x: x not in requestedEans, allActiveEans))

    for ean in eansToDeactivate:
        inactivate_productToTrack_byEan(trackerDbConn, ean, "")

    print('done')

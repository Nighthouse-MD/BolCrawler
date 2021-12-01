from datetime import date, timedelta
from Data.dailyParse import DailyParse, create_dailyParse, delete_dailyParse_byProductToTrackId, delete_dailyParse_byProductToTrackId_fromDate
from Data.productSnapshot import list_all_by_productId, list_all_by_productId_from_date
from Data.productToTrack import inactivate_productToTrack
from Data.db import create_connection
from Constants import Constants
import itertools
from dateutil.parser import parse
from operator import itemgetter


def parseSnapshotsForDaily(productId, parseAllDays):
    conn = create_connection(Constants.DB_PATH)

    if(parseAllDays):
        snapshots = list_all_by_productId(conn, productId)
        delete_dailyParse_byProductToTrackId(conn, productId)
    else:
        fromDate = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        snapshots = list_all_by_productId_from_date(conn, productId, fromDate)
        delete_dailyParse_byProductToTrackId_fromDate(
            conn, productId, fromDate)

    listsByDay = []
    for timestamp, dailyGrp in itertools.groupby(snapshots, key=lambda x: parse(x[2]).date()):
        listOfOneDay = list(dailyGrp)
        # print('on day {} a total of {} rows'.format(
        #     timestamp, len(listOfOneDay)))

        listOfOneDay = sorted(listOfOneDay, key=itemgetter(3))

        listsOfSellersForOneDay = []
        for seller, dailyListForSeller in itertools.groupby(listOfOneDay, key=lambda x: x[3]):
            listOfOneSellerForOneDay = list(dailyListForSeller)
            listOfOneSellerForOneDay = sorted(
                listOfOneSellerForOneDay, key=itemgetter(2))
            listsOfSellersForOneDay.append(listOfOneSellerForOneDay)
            # print('on day {} seller {} has total of {} rows'.format(
            #     timestamp, seller, len(listOfOneSellerForOneDay)))

        listsByDay.append(listsOfSellersForOneDay)

    # parse and save daily by seller to db
    dailyParses = []
    for sellerListsOfOneDay in listsByDay:
        for sellerSnapshotsOnOneDay in sellerListsOfOneDay:
            if(sellerSnapshotsOnOneDay[0][3] == 'NO SELLER'):
                continue

            dailyParse = DailyParse(
                sellerSnapshotsOnOneDay[0][1], sellerSnapshotsOnOneDay[0][3], sellerSnapshotsOnOneDay[0][6])
            dailyParse.dayStart = parse(sellerSnapshotsOnOneDay[0][2]).date()
            dailyParse.dayEnd = dailyParse.dayStart + timedelta(days=1)

            totalAmountOfSnapshots = len(sellerSnapshotsOnOneDay)
            for i in range(totalAmountOfSnapshots):
                if(i + 1 < totalAmountOfSnapshots):
                    currentSnapshot = sellerSnapshotsOnOneDay[i]
                    nextSnapshot = sellerSnapshotsOnOneDay[i+1]

                    try:
                        float(currentSnapshot[4])
                    except ValueError:
                        print("Not a float")
                        continue

                    unitsSold = currentSnapshot[5] - nextSnapshot[5]
                    if(unitsSold > 0):
                        dailyParse.unitsSold += unitsSold
                        dailyParse.revenue += (unitsSold * currentSnapshot[4])
                    elif (unitsSold < 0):
                        dailyParse.stockIncreaseSize += unitsSold * -1

            if(dailyParse.unitsSold > 0):
                dailyParse.avgPrice = dailyParse.revenue / dailyParse.unitsSold

            dailyParse.currentStock = sellerSnapshotsOnOneDay[totalAmountOfSnapshots - 1][5]
            dailyParses.append(dailyParse)

    conn = create_connection(Constants.DB_PATH)

    for dailyParse in dailyParses:
        create_dailyParse(conn, dailyParse)

    # parse and save daily all sellers to db
    dailyParsesAllSellers = []
    for day, dailyGrp in itertools.groupby(dailyParses, key=lambda x: x.dayStart):
        listOfOneDay = list(dailyGrp)
        dailyParseAllSellers = DailyParse(
            listOfOneDay[0].productToTrackId, 'ALL', 'ALL')
        dailyParseAllSellers.dayStart = listOfOneDay[0].dayStart
        dailyParseAllSellers.dayEnd = listOfOneDay[0].dayEnd

        for dailyParse in listOfOneDay:
            dailyParseAllSellers.revenue += dailyParse.revenue
            dailyParseAllSellers.unitsSold += dailyParse.unitsSold
            dailyParseAllSellers.stockIncreaseSize += dailyParse.stockIncreaseSize
            dailyParseAllSellers.currentStock += dailyParse.currentStock

        if(dailyParseAllSellers.unitsSold > 0):
            dailyParseAllSellers.avgPrice = dailyParseAllSellers.revenue / \
                dailyParseAllSellers.unitsSold

        dailyParsesAllSellers.append(dailyParseAllSellers)

    conn = create_connection(Constants.DB_PATH)
    for dailyParseAllSellers in dailyParsesAllSellers:
        create_dailyParse(conn, dailyParseAllSellers)

    if len(snapshots) != 0 and all(x[3] == 'NO SELLER' for x in snapshots):
        inactivate_productToTrack(conn, productId)

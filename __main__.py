import stockCrawler
import snapshotGrinder
from Data.db import create_db
from Constants import Constants
from Data.db import migrateTrackerDB, migrateApiDB

import stockCrawlerV2

if __name__ == '__main__':
    migrateTrackerDB()
    migrateApiDB()
    # stockCrawler.run()
    stockCrawlerV2.run()
    snapshotGrinder.run()

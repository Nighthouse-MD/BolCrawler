import stockCrawler
import snapshotGrinder
from Data.db import create_db
from Constants import Constants
from Data.db import migrateTrackerDB, migrateApiDB

if __name__ == '__main__':
    migrateTrackerDB()
    migrateApiDB()
    stockCrawler.run()
    snapshotGrinder.run()

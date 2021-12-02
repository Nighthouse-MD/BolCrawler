import stockCrawler
import snapshotGrinder
from Data.db import create_db
from Constants import Constants
from Data.db import migrate

if __name__ == '__main__':
    migrate()
    stockCrawler.run()
    snapshotGrinder.run()

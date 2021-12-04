from Data.db import migrateTrackerDB, checkForMissingEans
from Constants import Constants

if __name__ == '__main__':
    migrateTrackerDB()
    # checkForMissingEans()

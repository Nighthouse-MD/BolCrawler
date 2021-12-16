
# from Data import db

from Crawler.BolCrawler import handlerCrawlForOneProductAllSellers
from Data.trackerDB.productToTrack import list_all_active
from Data.db import create_connection
from Constants import Constants
import random
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-GB')
    profile.set_preference("browser.privatebrowsing.autostart", True)
    return profile


def run():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    productsToTrack = list_all_active(conn)
    random.shuffle(productsToTrack)

    GECKODRIVER_PATH = Constants.GECKODRIVER_PATH

    driver = webdriver.Firefox(firefox_profile=getProfile(),
                               executable_path=GECKODRIVER_PATH)

    # testProduct = list(filter(lambda x: (x[0] == 332), productsToTrack))[0]
    for i in range(len(productsToTrack)):
        handlerCrawlForOneProductAllSellers(driver, productsToTrack[i])

    # testProduct = list(filter(lambda x: (x[0] == 332), productsToTrack))[0]
    # handlerCrawlForOneProductAllSellers(driver, testProduct)

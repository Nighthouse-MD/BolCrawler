
# from Data import db

from Crawler.BolCrawlerV2 import handlerCrawlForOneProductAllSellers, getDriverBE
from Data.trackerDB.productToTrack import list_all
from Data.db import create_connection
from Constants import Constants
import random
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import os

import sys
import traceback
from Data.trackerDB.scraperLog import ScraperLog, create_log


def batchList(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-GB')
    profile.set_preference("browser.privatebrowsing.autostart", True)
    return profile


def run():
    conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
    create_log(conn, ScraperLog(
        f'TRACKER START', 'Info', None, None, None))
    productsToTrack = list_all(conn)
    random.shuffle(productsToTrack)

    batchedProducts = list(batchList(productsToTrack, 10))
    driver = None

    for batch in batchedProducts:
        if(driver is not None):
            driver.close()
            os.system("taskkill /f /im geckodriver.exe /T")

        driver = getDriverBE()

        for product in batch:
            try:
                handlerCrawlForOneProductAllSellers(driver, product)
            except Exception as e:
                ex_type, ex_value, ex_traceback = sys.exc_info()

                # Extract unformatter stack traces as tuples
                trace_back = traceback.extract_tb(ex_traceback)

                # Format stacktrace
                stack_trace = list()

                for trace in trace_back:
                    stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (
                        trace[0], trace[1], trace[2], trace[3]))

                print("Exception type : %s " % ex_type.__name__)
                print("Exception message : %s" % ex_value)
                print("Stack trace : %s" % stack_trace)

                conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
                create_log(conn, ScraperLog(
                    f'FATAL ERROR', 'Error', ex_type.__name__, ex_value, stack_trace))
                driver.quit()

    create_log(conn, ScraperLog(
        f'TRACKER DONE', 'Info', None, None, None))

    # testProduct = list(filter(lambda x: (x[0] == 332), productsToTrack))[0]
    # handlerCrawlForOneProductAllSellers(driver, testProduct)

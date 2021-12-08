import sys
import traceback
import csv
import time
import os.path
from os import path
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from Data.trackerDB.productSnapshot import create_productSnapshot, create_productSnapshots
from Data.trackerDB.productToTrack import inactivate_productToTrack
from Data.db import create_connection
from Data.trackerDB.scraperLog import ScraperLog, create_log
from Constants import Constants
from Crawler.FindElementHelpers import findElementByClassNameUntilFound, findElementsByClassNameUntilFound, findElementsByLinkTextUntilFound, findElementByIdUntilFound, findElementByTagNameUntilFound, findElementByXPathUntilFound, findElementsByIdUntilFound, findElementsByTagNameUntilFound, findElementsByXPathUntilFound

import time


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-GB')
    profile.set_preference("browser.privatebrowsing.autostart", True)
    return profile


def getStockAmountWith999Trick(driver, elementIndex, elementToScrape, lastOption):
    SLEEP_INVERVAL = Constants.SLEEP_INVERVAL

    lastOption.click()

    amountInput = findElementByClassNameUntilFound(
        elementToScrape, 'js_quantity_overlay_input')

    amountInput.send_keys('999')
    amountInfputConfirmButton = findElementByClassNameUntilFound(
        elementToScrape, 'js_quantity_overlay_ok')

    amountInfputConfirmButton.click()
    # !! causes a refresh

    refreshedShoppingCartElements = findElementsByClassNameUntilFound(
        driver, 'shopping-cart__row')
    elementToScrapeAfterRefresh = refreshedShoppingCartElements[elementIndex]

    quantityDropDown = findElementByIdUntilFound(
        elementToScrapeAfterRefresh, 'tst_quantity_dropdown')
    options = findElementsByTagNameUntilFound(quantityDropDown, 'option')

    theStockAmount = options[-2].get_attribute('value')
    return (theStockAmount, refreshedShoppingCartElements)


def getDriverBE():
    success = False

    while not success:
        try:
            GECKODRIVER_PATH = Constants.GECKODRIVER_PATH
            options = Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(firefox_profile=getProfile(),
                                       executable_path=GECKODRIVER_PATH,
                                       firefox_options=options)

            driver.get('https://bol.com')

            # handle modals
            firstModalAcceptButtonElements = findElementsByXPathUntilFound(driver,
                                                                           '/html/body/wsp-modal-window[1]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]')
            if(len(firstModalAcceptButtonElements) > 0):
                firstModalAcceptButtonElements[0].click()

            secondModalCloseButtonElements = findElementsByXPathUntilFound(driver,
                                                                           '/html/body/wsp-modal-window/div[2]/div[2]/wsp-country-language-modal/button', 2)

            if(len(secondModalCloseButtonElements) > 0):
                secondModalCloseButtonElements[0].click()

            catchOverlayError(driver, findElementByXPathUntilFound(
                driver, '/html/body/div/header/wsp-main-nav-offcanvas/div[2]/div/div/nav[1]/ul[2]/li[5]/wsp-country-language-selector/a').click)

            catchOverlayError(driver, findElementByXPathUntilFound(
                driver, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-country-language-modal/div[1]/p[1]/label/span').click)

            catchOverlayError(driver, findElementByXPathUntilFound(
                driver, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-country-language-modal/div[3]/p[2]/label/span').click)

            catchOverlayError(driver, findElementByXPathUntilFound(
                driver, '//*[@id="modalWindow"]/div[2]/div[2]/wsp-country-language-modal/button').click)

            success = True

        except Exception as e:
            driver.close()

    return driver


def catchOverlayError(driver, fnToExecute):
    success = False
    while not success:
        try:
            fnToExecute()
            success = True
        except ElementClickInterceptedException as e:
            findElementByClassNameUntilFound(driver, 'modal__overlay').click()


def handlerCrawlForOneProductAllSellers(driver, product):
    # start = time.time()
    # print("Started Timed Scrape V2")
    sellerId = ''
    sellerName = ''

    if driver is None:
        driver = getDriverBE()

    goToProductSellerOverview(driver, product[1])

    try:
        elementsFound = putAllInWinkelWagen(driver)

        if not elementsFound:
            conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
            inactivate_productToTrack(conn, product[0], "No sellers found")
            return

        goToCart(driver)

        shoppingCartElements = getShoppingCartElements(driver)

        productSnapshots = collectSnapshots(
            driver, shoppingCartElements, product)

        clearShoppingCart(driver)

        # add the row to the db
        conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
        create_productSnapshots(conn, productSnapshots)

    except Exception as e:
        handleException(driver, product, sellerId, sellerName)

    # end = time.time()
    # print("Ended Timed Scrape V2 with time: " + str(end - start))


def handleException(driver, product, sellerId='NO SELLER', sellerName='NO SELLER'):
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
    create_productSnapshot(
        conn, (product[0], datetime.now(), sellerId, sellerName, - 1, 0))
    create_log(conn, ScraperLog(
        f'An error occured when tracking product with db id {product[0]}', 'Error', ex_type.__name__, ex_value, stack_trace))
    try:
        driver.close()
    except Exception as e:
        return


def putAllInWinkelWagen(driver):
    inWinkelwagenLinks = findElementsByLinkTextUntilFound(
        driver, 'In winkelwagen')

    amountOfInWinkelwagenLinks = len(inWinkelwagenLinks)

    if(amountOfInWinkelwagenLinks < 1):
        return False

    for j in range(amountOfInWinkelwagenLinks):
        successBuyClick = False
        count = 0
        while successBuyClick is False and count < 4:
            # connect
            try:
                inWinkelwagenLinks[j].click()
                successBuyClick = True
            except Exception as e:
                count = count + 1
                time.sleep(0.1)
        time.sleep(0.3)

        successModalClick = False
        count = 0
        while successModalClick is False and count < 4:
            # connect
            try:
                findElementByXPathUntilFound(
                    driver, '/html/body/div[2]/div[2]/div[1]').click()
                successModalClick = True
            except Exception as e:
                count = count + 1
                time.sleep(0.1)
        time.sleep(0.3)

    return True


def scrapeOneShoppingCartItem(driver, elementToScrape, product, index, shoppingCartElements):
    try:
        priceOfOne = findElementByIdUntilFound(elementToScrape, 'tst_product_price').text.replace(
            '.', '').replace(',', '.').strip('€ ')
    except:
        handleException(driver, product, 'PRICE ERROR', 'PRICE ERROR')

    # check for non bol seller element location
    try:
        sellerNameElement = findElementByClassNameUntilFound(
            elementToScrape, 'product-seller__name')

    except NoSuchElementException:
        sellerNameElement = None

    sellerIsBol = False

    if(sellerNameElement == None):
        sellerIsBol = True

    sellerId = 'NO SELLER'
    sellerName = 'NO SELLER'

    if(not sellerIsBol):
        sellerLink = findElementByXPathUntilFound(
            sellerNameElement, '..')
        sellerPath = sellerLink.get_attribute('href')
        sellerId = sellerPath.split("/")[-2]
        sellerName = sellerLink.text
    else:
        sellerName = 'BOL'
        sellerId = 'BOL'

    stockAmount = -1

    quantityDropDown = findElementByIdUntilFound(
        elementToScrape, 'tst_quantity_dropdown')
    options = findElementsByTagNameUntilFound(
        quantityDropDown, 'option')

    if any(option.get_attribute('value') == 'meer' for option in options):
        result = getStockAmountWith999Trick(
            driver, index, elementToScrape, options[-1])
        stockAmount = result[0]
        shoppingCartElements = result[1]
    else:
        stockAmount = options[-1].get_attribute('value')

    trackedOn = datetime.now()

    return (shoppingCartElements, (product[0], trackedOn, sellerId, sellerName, priceOfOne, stockAmount))


def clearShoppingCart(driver):
    removeButtons = findElementsByIdUntilFound(
        driver, 'tst_remove_from_basket')
    removeButtonsLength = len(removeButtons)

    while removeButtonsLength > 0:
        removeButtons[0].click()
        removeButtons = findElementsByIdUntilFound(
            driver, 'tst_remove_from_basket')
        removeButtonsLength = len(removeButtons)


def getShoppingCartElements(driver):
    shoppingCartElements = findElementsByClassNameUntilFound(
        driver, 'shopping-cart__row')
    return list(filter(lambda x: ('Neem Select erbij voor' not in x.text), shoppingCartElements))


def goToCart(driver):
    driver.get('https://www.bol.com/nl/order/basket.html')


def collectSnapshots(driver, shoppingCartElements, product):
    shoppingCartElementsLength = len(shoppingCartElements)
    productSnapshots = []

    for i in range(shoppingCartElementsLength):
        elementToScrape = shoppingCartElements[i]
        # get price and sellerId
        result = scrapeOneShoppingCartItem(
            driver, elementToScrape, product, i, shoppingCartElements)

        shoppingCartElements = result[0]
        productSnapshots.append(result[1])

    return productSnapshots


def goToProductSellerOverview(driver, productId):
    productSellersOverviewUrl = 'https://www.bol.com/be/nl/prijsoverzicht/productname/' + \
        productId + '/?filter=new&sortOrder=asc&sort=price'
    driver.get(productSellersOverviewUrl)

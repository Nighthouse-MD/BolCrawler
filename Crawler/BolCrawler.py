import sys
import traceback
import csv
import time
import os.path
from os import path
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from Data.trackerDB.productSnapshot import create_productSnapshot
from Data.db import create_connection
from Data.trackerDB.scraperLog import ScraperLog, create_log
from Constants import Constants


def getStockAmountWith999Trick(driver, lastOption):
    SLEEP_INVERVAL = Constants.SLEEP_INVERVAL

    lastOption.click()
    amountInput = driver.find_element_by_class_name(
        'js_quantity_overlay_input')

    amountInput.send_keys('999')
    amountInfputConfirmButton = driver.find_element_by_class_name(
        'js_quantity_overlay_ok')
    amountInfputConfirmButton.click()

    quantityDropDown = driver.find_element_by_id('tst_quantity_dropdown')
    options = quantityDropDown.find_elements_by_tag_name('option')

    theStockAmount = options[-2].get_attribute('value')
    return theStockAmount


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-GB')
    profile.set_preference("browser.privatebrowsing.autostart", True)
    profile.set_preference("network.http.pipelining", True)
    profile.set_preference("network.http.proxy.pipelining", True)
    profile.set_preference("network.http.pipelining.maxrequests", 8)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    # Increase the cache capacity.
    profile.set_preference("browser.cache.memory.capacity", 65536)
    profile.set_preference("browser.startup.homepage", "about:blank")
    # Disable reader, we won't need that.
    profile.set_preference("reader.parse-on-load.enabled", False)
    profile.set_preference("browser.pocket.enabled", False)  # Duck pocket too!
    profile.set_preference("loop.enabled", False)
    # Text on Toolbar instead of icons
    profile.set_preference("browser.chrome.toolbar_style", 1)
    # Don't show thumbnails on not loaded images.
    profile.set_preference("browser.display.show_image_placeholders", False)
    # Don't show document colors.
    profile.set_preference("browser.display.use_document_colors", False)
    # Don't load document fonts.
    profile.set_preference("browser.display.use_document_fonts", 0)
    # Use system colors.
    profile.set_preference("browser.display.use_system_colors", True)
    # Autofill on forms disabled.
    profile.set_preference("browser.formfill.enable", False)
    # Delete temprorary files.
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True)
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0)  # blank
    # Disable tabs, We won't need that.
    profile.set_preference("browser.tabs.forceHide", True)
    # Disable autofill on URL bar.
    profile.set_preference("browser.urlbar.autoFill", False)
    # Disable autocomplete on URL bar.
    profile.set_preference("browser.urlbar.autocomplete.enabled", False)
    # Disable list of URLs when typing on URL bar.
    profile.set_preference("browser.urlbar.showPopup", False)
    # Disable search bar.
    profile.set_preference("browser.urlbar.showSearch", False)
    profile.set_preference("extensions.checkCompatibility",
                           False)  # Addon update disabled
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("permissions.default.image",
                           2)  # Image load disabled again
    return profile


def findElementByXPathUntilFound(driver, xpath):
    result = None
    count = 0
    while result is None and count < 10:
        try:
            # connect
            result = driver.find_element_by_xpath(xpath)
        except:
            count = count + 1
            time.sleep(0.1)
    return result


def findElementsByXPathUntilFound(driver, xpath, amountOfTries=5):
    result = None
    count = 0
    while (result is None or len(result) < 1) and count < amountOfTries:
        # connect
        result = driver.find_elements_by_xpath(xpath)
        count = count + 1
        time.sleep(0.1)
    return result


def handlerCrawlForOneProductAllSellers(driver, product):
    try:
        if(driver is None):
            GECKODRIVER_PATH = Constants.GECKODRIVER_PATH
            driver = webdriver.Firefox(firefox_profile=getProfile(),
                                       executable_path=GECKODRIVER_PATH)
        else:
            driver.delete_all_cookies

        productSellersOverviewUrl = 'https://www.bol.com/nl/nl/prijsoverzicht/productname/' + \
            product[1] + '/?filter=new&sortOrder=asc&sort=price'

        driver.get(productSellersOverviewUrl)

        # handle modals
        firstModalAcceptButtonElements = findElementsByXPathUntilFound(driver,
                                                                       '/html/body/wsp-modal-window[1]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]')

        if(len(firstModalAcceptButtonElements) > 0):
            firstModalAcceptButtonElements[0].click()

        secondModalCloseButtonElements = findElementsByXPathUntilFound(driver,
                                                                       '/html/body/wsp-modal-window/div[2]/div[2]/wsp-country-language-modal/button', 2)

        if(len(secondModalCloseButtonElements) > 0):
            secondModalCloseButtonElements[0].click()

        findElementByXPathUntilFound(driver,
                                     '/html/body/div/header/wsp-main-nav-offcanvas/div[2]/div/div/nav[1]/ul[2]/li[5]/wsp-country-language-selector/a').click()

        findElementByXPathUntilFound(
            driver, '//*[@id="dutch-language-input"]').click()

        findElementByXPathUntilFound(driver,
                                     '//*[@id="country-belgium-input"]').click()

        findElementByXPathUntilFound(driver,
                                     '/html/body/wsp-modal-window/div[2]/div[2]/wsp-country-language-modal/button').click()

    except:
        return handleException(driver, product, 'MODAL ERROR', 'MODAL ERROR')
    try:
        amountOfInWinkelwagenLinks = len(driver.find_elements_by_link_text(
            'In winkelwagen'))

        for i in range(amountOfInWinkelwagenLinks):
            inWinkelwagenLinks = driver.find_elements_by_link_text(
                'In winkelwagen')

            # add to cart
            inWinkelwagenLinks[i].click()

            time.sleep(2.5)

            # go to cart
            driver.get('https://www.bol.com/nl/order/basket.html')

            # get price and sellerId
            try:
                priceOfOne = driver.find_element_by_id(
                    'tst_product_price').text.replace('.', '').replace(',', '.').strip('€ ')
            except:
                return handleException(driver, product, 'PRICE ERROR', 'PRICE ERROR')

            # check for non bol seller element location
            sellerElements = driver.find_elements_by_xpath(
                '/html/body/div/main/div[3]/div/div/div[2]/div/div[2]/div')

            sellerIsBol = False

            if(sellerElements == None or len(sellerElements) == 0):
                sellerIsBol = True

            sellerId = 'NO SELLER'
            sellerName = 'NO SELLER'

            if(not sellerIsBol):
                sellerLink = driver.find_element_by_xpath(
                    '/html/body/div/main/div[3]/div/div/div[2]/div/div[2]/div/wsp-popup-fragment/a')
                sellerPath = sellerLink.get_attribute('href')
                sellerId = sellerPath.split("/")[-2]
                sellerName = sellerLink.text
            else:
                sellerName = 'BOL'
                sellerId = 'BOL'

            # check if there is a 'meer' option
            hasMoreThanTenOptions = False
            stockAmount = -1

            quantityDropDown = driver.find_element_by_id(
                'tst_quantity_dropdown')
            options = quantityDropDown.find_elements_by_tag_name('option')

            if any(option.get_attribute('value') == 'meer' for option in options):
                stockAmount = getStockAmountWith999Trick(driver, options[-1])
            else:
                stockAmount = options[-1].get_attribute('value')

            trackedOn = datetime.now()

            # add the row to the db
            conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
            create_productSnapshot(
                conn, (product[0], trackedOn, sellerId, sellerName, priceOfOne, stockAmount))

            verwijderButton = driver.find_element_by_link_text(
                'Verwijder').click()

            productSellersOverviewUrl = 'https://www.bol.com/nl/prijsoverzicht/productname/' + \
                product[1] + '/?filter=new&sortOrder=asc&sort=price'

            driver.get(productSellersOverviewUrl)
        # driver.close()
    except:
        return handleException(driver, product, sellerId, sellerName)

    # foreach element in winkelwagen links
    # click it, and go to basket
    # get price, sellerId
    # do the track magic
    # save it
    # click verwijder in basket
    # go back to prijsoverzicht page and click the next item in this list


# def handlerCrawlForOneProduct(product):
#     try:
#         SLEEP_INVERVAL = Constants.SLEEP_INVERVAL
#         RESULTS_FOLDER = Constants.RESULTS_FOLDER
#         GECKODRIVER_PATH = Constants.GECKODRIVER_PATH

#         driver = webdriver.Firefox(firefox_profile=getProfile(),
#                                    executable_path=GECKODRIVER_PATH)
#         driver.get('https://www.bol.com/nl/p/productName/' + product[1])

#         time.sleep(0.3)

#         # handle modals
#         firstModalAcceptButton = driver.find_element_by_xpath(
#             '/html/body/wsp-modal-window[1]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]')

#         firstModalAcceptButton.click()

#         time.sleep(SLEEP_INVERVAL)

#         secondModalCloseButton = driver.find_element_by_xpath(
#             '/html/body/wsp-modal-window/div[2]/div[2]/div/wsp-toggle-visibility[1]/div/div[1]/wsp-switch-country/a')
#         secondModalCloseButton.click()

#         time.sleep(SLEEP_INVERVAL)

#         # get price and sellerId
#         try:
#             priceOfOne = driver.find_element_by_class_name(
#                 'promo-price').text.replace('\n', '.').strip('-').strip('.')
#         except:
#             return handleException(driver, product, 'PROMO ERROR', 'PROMO ERROR')

#         # check for non bol seller element location
#         sellerElement = driver.find_element_by_xpath(
#             '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div/wsp-visibility-switch/div[3]')

#         if(sellerElement == None):
#             sellerElement = driver.find_element_by_xpath(
#                 '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div[2]/wsp-visibility-switch/div[3]')

#         sellerIsBol = sellerElement.text == 'Verkoop door bol.com'

#         sellerId = 'NO SELLER'
#         sellerName = 'NO SELLER'

#         if(not sellerIsBol):
#             sellerLink = driver.find_element_by_xpath(
#                 '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div/wsp-visibility-switch/div[3]/wsp-popup-fragment/a')
#             sellerPath = sellerLink.get_attribute('href')
#             sellerId = sellerPath.split("/")[-2]
#             sellerName = sellerLink.text
#         else:
#             sellerId = 'BOL'
#             sellerName = 'BOL'

#         # add product to cart
#         addToCartButton = driver.find_element_by_xpath(
#             '//*[@id="' + product[1] + '"]')
#         addToCartButton.click()

#         time.sleep(SLEEP_INVERVAL)

#         # go to cart
#         driver.get('https://www.bol.com/nl/order/basket.html')

#         time.sleep(0.3)

#         # check if there is a 'meer' option
#         hasMoreThanTenOptions = False
#         stockAmount = -1

#         quantityDropDown = driver.find_element_by_id('tst_quantity_dropdown')
#         options = quantityDropDown.find_elements_by_tag_name('option')

#         if any(option.get_attribute('value') == 'meer' for option in options):
#             stockAmount = getStockAmountWith999Trick(driver, options[-1])
#         else:
#             stockAmount = options[-1].get_attribute('value')

#         driver.close()

#         # add the row to a new csv file with name '{PRODUCT_ID}_tracking.csv'
#         fileName = RESULTS_FOLDER + product[1] + '_result.csv'
#         trackedOn = datetime.now()

#         if(not path.exists(fileName)):
#             with open(fileName, 'w') as f:
#                 f.write('Date, Time, Seller Id, Price, Stock Amount \n')

#         with open(fileName, 'a') as f:
#             f.write(trackedOn.strftime("%d/%m/%Y, %H:%M:%S") +
#                     ', ' + sellerId + ', ' + priceOfOne + ', ' + stockAmount + '\n')

#         # add the row to the db
#         conn = create_connection(Constants.BOLDER_TRACKER_DB_PATH)
#         create_productSnapshot(
#             conn, (product[0], trackedOn, sellerId, sellerName, priceOfOne, stockAmount))
#     except:
#         return handleException(driver, product, sellerId, sellerName)


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
    # try:
    #     driver.quit()
    # except WebDriverException:
    #     pass
    return


# all offers of a seller page https://www.bol.com/nl/c/{anything}/{SELLER_ID}/
# example for 'Benson' https://www.bol.com/nl/c/lol/494032/

# one offer https://www.bol.com/nl/p/{anything}/{PRODUCT_ID}/
# example for 'kruiwagen wiel...' https://www.bol.com/nl/p/dinges/9200000055242553/

# investigate this, same product but different offerId AND different productId
# offerId=1001032522155253&productId=9200000055242553
# offerId=1001032980778060&productId=9200000087796759

# in winkelwagen button example
# <a href="https://www.bol.com/nl/order/basket/addItems.html?productId=9200000087796759&amp;offerId=1001032980778060&amp;quantity=1&amp;bltgh=jDXpzJrnMntqugT7q9BEzA.1_6.7.AddToCart" class="[ btn btn--cta btn--buy btn--lg ] js_floating_basket_btn js_btn_buy js_preventable_buy_action" id="9200000087796759" data-offer-id="1001032980778060" data-product-id="9200000087796759" data-show-additional-page="true" data-relatedproductimage_id="9200000087796759" data-button-type="buy" data-buy-block-type="BuyBlock" data-size-pick-prevent="add_to_basket" data-test="add-to-basket" data-bltgh="jDXpzJrnMntqugT7q9BEzA.1_6.7.AddToCart">
#     <span class="[ sb sb-plus ] active__hide"></span>
#     <span class="[ sb sb-check ] active__show"></span>
#     In winkelwagen
# </a>

# use sendKeys to simulate user input
# https://selenium-python.readthedocs.io/getting-started.html

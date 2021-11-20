import sys
import csv
import time
import os.path
from os import path
from selenium import webdriver
from datetime import datetime
from Data.productSnapshot import create_productSnapshot
from Data.db import create_connection
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
    time.sleep(SLEEP_INVERVAL)

    quantityDropDown = driver.find_element_by_id('tst_quantity_dropdown')
    options = quantityDropDown.find_elements_by_tag_name('option')

    theStockAmount = options[-2].get_attribute('value')
    return theStockAmount


def getProfile():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.privatebrowsing.autostart", True)
    return profile


def handlerCrawlForOneProductAllSellers(product):
    try:
        SLEEP_INVERVAL = Constants.SLEEP_INVERVAL
        RESULTS_FOLDER = Constants.RESULTS_FOLDER
        GECKODRIVER_PATH = Constants.GECKODRIVER_PATH

        driver = webdriver.Firefox(firefox_profile=getProfile(),
                                   executable_path=GECKODRIVER_PATH)

        productSellersOverviewUrl = 'https://www.bol.com/nl/prijsoverzicht/productname/' + \
            product[1] + '/?filter=new&sortOrder=asc&sort=price'

        driver.get(productSellersOverviewUrl)

        time.sleep(1)

        # handle modals
        firstModalAcceptButtonElements = driver.find_elements_by_xpath(
            '/html/body/wsp-modal-window[1]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]')

        if(len(firstModalAcceptButtonElements) > 0):
            firstModalAcceptButtonElements[0].click()

        time.sleep(SLEEP_INVERVAL)

        secondModalCloseButtonElements = driver.find_elements_by_xpath(
            '/html/body/wsp-modal-window/div[2]/div[2]/wsp-country-language-modal/button')

        if(len(secondModalCloseButtonElements) > 0):
            secondModalCloseButtonElements[0].click()

        time.sleep(SLEEP_INVERVAL)

        amountOfInWinkelwagenLinks = len(driver.find_elements_by_link_text(
            'In winkelwagen'))

        for i in range(amountOfInWinkelwagenLinks):
            inWinkelwagenLinks = driver.find_elements_by_link_text(
                'In winkelwagen')

            # add to cart
            inWinkelwagenLinks[i].click()

            time.sleep(SLEEP_INVERVAL)

            # go to cart
            driver.get('https://www.bol.com/nl/order/basket.html')

            time.sleep(1)

            # get price and sellerId
            try:
                priceOfOne = driver.find_element_by_id(
                    'tst_product_price').text.replace(',', '.').strip('€ ')
            except:
                print(sys.exc_info()[0])
                priceOfOne = -1
                conn = create_connection(Constants.DB_PATH)
                create_productSnapshot(
                    conn, (product[0], datetime.now(), 'NIET LEVERBAAR', -1, 0))
                driver.close()
                return

            # check for non bol seller element location
            sellerElements = driver.find_elements_by_xpath(
                '/html/body/div/main/div[3]/div/div/div[2]/div/div[2]/div')

            sellerIsBol = False

            if(sellerElements == None or len(sellerElements) == 0):
                sellerIsBol = True

            sellerId = 'BOL'

            if(not sellerIsBol):
                sellerLink = driver.find_element_by_xpath(
                    '/html/body/div/main/div[3]/div/div/div[2]/div/div[2]/div/wsp-popup-fragment/a')
                sellerPath = sellerLink.get_attribute('href')
                sellerId = sellerPath.split("/")[-2]

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

            # add the row to a new csv file with name '{PRODUCT_ID}_tracking.csv'
            # fileName = RESULTS_FOLDER + product[1] + '_result.csv'

            # if(not path.exists(fileName)):
            #     with open(fileName, 'w') as f:
            #         f.write('Date, Time, Seller Id, Price, Stock Amount \n')

            # with open(fileName, 'a') as f:
            #     f.write(trackedOn.strftime("%d/%m/%Y, %H:%M:%S") +
            #             ', ' + sellerId + ', ' + priceOfOne + ', ' + stockAmount + '\n')

            # add the row to the db
            conn = create_connection(Constants.DB_PATH)
            create_productSnapshot(
                conn, (product[0], trackedOn, sellerId, priceOfOne, stockAmount))

            verwijderButton = driver.find_element_by_link_text(
                'Verwijder').click()

            productSellersOverviewUrl = 'https://www.bol.com/nl/prijsoverzicht/productname/' + \
                product[1] + '/?filter=new&sortOrder=asc&sort=price'

            driver.get(productSellersOverviewUrl)
        driver.close()
    except:
        print(sys.exc_info()[0])
        priceOfOne = -1
        conn = create_connection(Constants.DB_PATH)
        create_productSnapshot(
            conn, (product[0], datetime.now(), 'NIET LEVERBAAR', -1, 0))
        driver.close()
        return

    # foreach element in winkelwagen links
    # click it, and go to basket
    # get price, sellerId
    # do the track magic
    # save it
    # click verwijder in basket
    # go back to prijsoverzicht page and click the next item in this list


def handlerCrawlForOneProduct(product):
    try:
        SLEEP_INVERVAL = Constants.SLEEP_INVERVAL
        RESULTS_FOLDER = Constants.RESULTS_FOLDER
        GECKODRIVER_PATH = Constants.GECKODRIVER_PATH

        driver = webdriver.Firefox(firefox_profile=getProfile(),
                                   executable_path=GECKODRIVER_PATH)
        driver.get('https://www.bol.com/nl/p/productName/' + product[1])

        time.sleep(1)

        # handle modals
        firstModalAcceptButton = driver.find_element_by_xpath(
            '/html/body/wsp-modal-window[1]/div[2]/div[2]/wsp-consent-modal/div[2]/button[1]')

        firstModalAcceptButton.click()

        time.sleep(SLEEP_INVERVAL)

        secondModalCloseButton = driver.find_element_by_xpath(
            '/html/body/wsp-modal-window/div[2]/div[2]/div/wsp-toggle-visibility[1]/div/div[1]/wsp-switch-country/a')
        secondModalCloseButton.click()

        time.sleep(SLEEP_INVERVAL)

        # get price and sellerId
        try:
            priceOfOne = driver.find_element_by_class_name(
                'promo-price').text.replace('\n', '.').strip('-').strip('.')
        except:
            print(sys.exc_info()[0])
            priceOfOne = -1
            conn = create_connection(Constants.DB_PATH)
            create_productSnapshot(
                conn, (product[0], datetime.now(), 'NIET LEVERBAAR', -1, 0))
            driver.close()
            return

        # check for non bol seller element location
        sellerElement = driver.find_element_by_xpath(
            '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div/wsp-visibility-switch/div[3]')

        if(sellerElement == None):
            sellerElement = driver.find_element_by_xpath(
                '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div[2]/wsp-visibility-switch/div[3]')

        sellerIsBol = sellerElement.text == 'Verkoop door bol.com'

        sellerId = 'BOL'
        if(not sellerIsBol):
            sellerLink = driver.find_element_by_xpath(
                '/html/body/div[1]/main/div/div[1]/div[5]/div[2]/div[1]/div/wsp-visibility-switch/div[3]/wsp-popup-fragment/a')
            sellerPath = sellerLink.get_attribute('href')
            sellerId = sellerPath.split("/")[-2]

        # add product to cart
        addToCartButton = driver.find_element_by_xpath(
            '//*[@id="' + product[1] + '"]')
        addToCartButton.click()

        time.sleep(SLEEP_INVERVAL)

        # go to cart
        driver.get('https://www.bol.com/nl/order/basket.html')

        time.sleep(1)

        # check if there is a 'meer' option
        hasMoreThanTenOptions = False
        stockAmount = -1

        quantityDropDown = driver.find_element_by_id('tst_quantity_dropdown')
        options = quantityDropDown.find_elements_by_tag_name('option')

        if any(option.get_attribute('value') == 'meer' for option in options):
            stockAmount = getStockAmountWith999Trick(driver, options[-1])
        else:
            stockAmount = options[-1].get_attribute('value')

        driver.close()

        # add the row to a new csv file with name '{PRODUCT_ID}_tracking.csv'
        fileName = RESULTS_FOLDER + product[1] + '_result.csv'
        trackedOn = datetime.now()

        if(not path.exists(fileName)):
            with open(fileName, 'w') as f:
                f.write('Date, Time, Seller Id, Price, Stock Amount \n')

        with open(fileName, 'a') as f:
            f.write(trackedOn.strftime("%d/%m/%Y, %H:%M:%S") +
                    ', ' + sellerId + ', ' + priceOfOne + ', ' + stockAmount + '\n')

        # add the row to the db
        conn = create_connection(Constants.DB_PATH)
        create_productSnapshot(
            conn, (product[0], trackedOn, sellerId, priceOfOne, stockAmount))
    except:
        print(sys.exc_info()[0])
        priceOfOne = -1
        conn = create_connection(Constants.DB_PATH)
        create_productSnapshot(
            conn, (product[0], datetime.now(), 'NIET LEVERBAAR', -1, 0))
        driver.close()
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

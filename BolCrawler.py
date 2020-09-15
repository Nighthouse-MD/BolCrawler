import csv
import time
import os.path
from os import path
from selenium import webdriver
from datetime import datetime

PRODUCT_ID = '9200000055242553'

SLEEP_INVERVAL = 3


def getStockAmountWith999Trick(lastOption):
    lastOption.click()
    amountInput = driver.find_element_by_class_name(
        'js_quantity_overlay_input')
    time.sleep(SLEEP_INVERVAL)

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


driver = webdriver.Firefox(firefox_profile=getProfile(),
                           executable_path=r'C:\Users\eclipse\AppData\Local\GeckoDriver\geckodriver.exe')
driver.get('https://www.bol.com/nl/p/productName/' + PRODUCT_ID)

time.sleep(SLEEP_INVERVAL)

# handle modals
firstModelAcceptButton = driver.find_element_by_xpath(
    '//*[@id="modalWindow"]/div[2]/div[2]/wsp-consent-modal/div[2]/div/div[1]/button')
firstModelAcceptButton.click()

time.sleep(SLEEP_INVERVAL)

secondModalCloseButton = driver.find_element_by_xpath(
    '//*[@id="modalWindow"]/div[2]/button')
secondModalCloseButton.click()

time.sleep(SLEEP_INVERVAL)

# get price and sellerId
priceOfOne = driver.find_element_by_class_name(
    'promo-price').text.replace('\n', '.')

sellerLink = driver.find_element_by_xpath(
    '/html/body/div[1]/main/div/div[1]/div[2]/div[2]/div[1]/div/wsp-visibility-switch/div[3]/wsp-popup-fragment/a')
sellerPath = sellerLink.get_attribute('href')
sellerId = sellerPath.split("/")[-2]

# add product to cart
addToCartButton = driver.find_element_by_xpath('//*[@id="' + PRODUCT_ID + '"]')
addToCartButton.click()

time.sleep(SLEEP_INVERVAL)

# go to cart
driver.get('https://www.bol.com/nl/order/basket.html')

time.sleep(SLEEP_INVERVAL)

# check if there is a 'meer' option
hasMoreThanTenOptions = False
stockAmount = -1

quantityDropDown = driver.find_element_by_id('tst_quantity_dropdown')
options = quantityDropDown.find_elements_by_tag_name('option')

if any(option.get_attribute('value') == 'meer' for option in options):
    stockAmount = getStockAmountWith999Trick(options[-1])
else:
    stockAmount = options[-1].get_attribute('value')

driver.close()

# add the row to a new csv file with name '{PRODUCT_ID}_tracking.csv'

fileName = PRODUCT_ID + '_result.csv'

if(not path.exists(fileName)):
    with open(fileName, 'w') as f:
        f.write('Date, Time, Seller Id, Price, Stock Amount \n')

with open(fileName, 'a') as f:
    f.write(datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +
            ', ' + sellerId + ', ' + priceOfOne + ', ' + stockAmount + '\n')


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

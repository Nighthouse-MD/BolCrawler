# import csv
# import time
# from selenium import webdriver

# MAX_PAGE_NUM = 5
# MAX_PAGE_DIG = 3

# with open('result.csv', 'w') as f:
#     f.write('Buyers, Price \n')


# def getProfile():
#     profile = webdriver.FirefoxProfile()
#     profile.set_preference("browser.privatebrowsing.autostart", True)
#     return profile


# def readCurrentPage(pageNumber):
#     print('reading page number ' + str(pageNumber))
#     buyers = driver.find_elements_by_xpath('//div[@title="buyer-name"]')
#     prices = driver.find_elements_by_xpath('//span[@class="item-price"]')

#     amountOfBuyers = len(buyers)
#     print('there are ' + str(amountOfBuyers) + ' buyers on this page')

#     with open('result.csv', 'a') as f:
#         for i in range(len(buyers)):
#             print(buyers[i].text + " : " + prices[i].text)
#             f.write(buyers[i].text + ',' + prices[i].text + '\n')
#         f.write('\n')


# def readLinksAfterLoad():
#     anchorZone = driver.find_element_by_css_selector('div[align=center]')
#     global LINKS
#     LINKS = anchorZone.find_elements_by_tag_name('a')


# LINKS = []
# driver = webdriver.Firefox(firefox_profile=getProfile(),
#                            executable_path=r'C:\Users\eclipse\AppData\Local\GeckoDriver\geckodriver.exe')
# driver.get('http://econpy.pythonanywhere.com/ex/001.html')

# time.sleep(5)
# readCurrentPage(1)
# readLinksAfterLoad()

# # assuming we start on page 1
# for i in range(len(LINKS)):
#     LINKS[i].click()
#     time.sleep(5)
#     readLinksAfterLoad()
#     readCurrentPage(i + 2)

# driver.close()

import time


def findElementsByLinkTextUntilFound(driver, linkText, amountOfTries=5):
    result = None
    count = 0
    while (result is None or len(result) < 1) and count < amountOfTries:
        # connect
        result = driver.find_elements_by_link_text(linkText)
        count = count + 1
        time.sleep(0.1)
    return result


def findElementByXPathUntilFound(driver, xpath):
    result = None
    count = 0
    while result is None and count < 5:
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


def findElementByClassNameUntilFound(driver, className):
    result = None
    count = 0
    while result is None and count < 5:
        try:
            # connect
            result = driver.find_element_by_class_name(className)
        except:
            count = count + 1
            time.sleep(0.1)
    return result


def findElementsByClassNameUntilFound(driver, className, amountOfTries=5):
    result = None
    count = 0
    while (result is None or len(result) < 1) and count < amountOfTries:
        # connect
        result = driver.find_elements_by_class_name(className)
        count = count + 1
        time.sleep(0.1)
    return result


def findElementByIdUntilFound(driver, id):
    result = None
    count = 0
    while result is None and count < 5:
        try:
            # connect
            result = driver.find_element_by_id(id)
        except:
            count = count + 1
            time.sleep(0.1)
    return result


def findElementsByIdUntilFound(driver, id, amountOfTries=5):
    result = None
    count = 0
    while (result is None or len(result) < 1) and count < amountOfTries:
        # connect
        result = driver.find_elements_by_id(id)
        count = count + 1
        time.sleep(0.1)
    return result


def findElementByTagNameUntilFound(driver, tagName):
    result = None
    count = 0
    while result is None and count < 5:
        try:
            # connect
            result = driver.find_element_by_tag_name(tagName)
        except:
            count = count + 1
            time.sleep(0.1)
    return result


def findElementsByTagNameUntilFound(driver, tagName, amountOfTries=5):
    result = None
    count = 0
    while (result is None or len(result) < 1) and count < amountOfTries:
        # connect
        result = driver.find_elements_by_tag_name(tagName)
        count = count + 1
        time.sleep(0.1)
    return result

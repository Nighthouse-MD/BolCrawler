
# from Data import db

from Crawler.BolCrawler import handlerCrawlForOneProduct
from Data.productToTrack import list_all
from Data.db import create_connection
from Constants import Constants


def run():
    conn = create_connection(Constants.DB_PATH)
    productsToTrack = list_all(conn)
    for i in range(len(productsToTrack)):
        handlerCrawlForOneProduct(productsToTrack[i])

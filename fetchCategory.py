from Data.db import create_connection
from Data.productToTrack import create_productToTrack
from Constants import Constants
from datetime import datetime
import requests


def fetchCategoryTopProducts(categoryId):
    resp = requests.get(
        'https://api.bol.com/catalog/v4/lists/?ids={}&limit=100&type=toplist_default&dataoutput=products&sort=rankasc&apikey={}&format=json'.format(categoryId, Constants.BOL_API_KEY))

    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /lists/ {}'.format(categoryId))

    products = resp.json()['products']
    fetchedOn = datetime.now()

    conn = create_connection(Constants.DB_PATH)

    for product in products:
        create_productToTrack(
            conn, (product['id'], product['title'], fetchedOn, categoryId))
        print('{} {}'.format(product['id'], product['title']))


if __name__ == '__main__':
    fetchCategoryTopProducts('22867')
    #7142, 11369, 11373

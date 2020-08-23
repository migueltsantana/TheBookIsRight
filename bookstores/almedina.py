import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from bs4 import BeautifulSoup
from models import Book


def get_info(url):
    html = utils.get_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    price = get_price(soup)
    return Book(int(get_isbn(soup)), price["promo_price"], price["regular_price"],
                price["currency"], "Almedina", url, get_photo_url(soup))


def get_price(soup):
    price = soup.select(".price-regular > span")[0].attrs.get("content")
    result = [price.replace("\xa0", "") for price in
              list(filter(None, list(map(lambda s: s.strip(), list(filter(None, price.strip().split(" ")))))))]
    return {
        "promo_price": float(result[0][:-1].replace(",", ".")),
        "regular_price": float(result[1][:-1].replace(",", ".")),
        "currency": price.strip().split(" ")[0][-1]
    }


def get_isbn(soup):
    soup.select(".prod-details-wrapper > ul > li > b")[3].decompose()
    return soup.select(".prod-details-wrapper > ul > li")[3].string[1:]


def get_photo_url(soup):
    return soup.select(".product-image-wrapper > .product-image-container > img")[0]["src"]

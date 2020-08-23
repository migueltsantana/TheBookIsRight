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
                price["currency"], "Book Depository", url, get_photo_url(soup))


def get_price(soup):
    price = {"promo_price": None, "regular_price": None}
    if soup.select(".list-price") != []:
        price["regular_price"] = float(soup.select(".list-price")[0].string[:-2].replace(",", "."))
        price["promo_price"] = float(soup.select(".sale-price")[0].string[:-2].replace(",", "."))
    else:
        price["regular_price"] = float(soup.select(".sale-price")[0].string[:-2].replace(",", "."))
    price["currency"] = soup.select(".sale-price")[0].string[-1]
    return price


def get_isbn(soup):
    return soup.find("span", itemprop="isbn").string


def get_photo_url(soup):
    return soup.select(".item-img > .item-img-content > .book-img")[0]["src"]

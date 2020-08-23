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
                price["currency"], "Wook", url, get_photo_url(soup))


def get_price(soup):
    price = {"promo_price": None, "regular_price": None}
    if soup.select("#productPageRightSectionTop-saleAction-price-old") != []:
        price["regular_price"] = float(
            soup.select("#productPageRightSectionTop-saleAction-price-old")[0].attrs.get("data-price")[:-1].replace(
                ",", "."))
        price["promo_price"] = float(
            soup.select("#productPageRightSectionTop-saleAction-price-current")[0].attrs.get("data-price")[:-1]
            .replace(",", "."))
    else:
        price["regular_price"] = float(
            soup.select("#productPageRightSectionTop-saleAction-price-current")[0].attrs.get("data-price")[:-1]
            .replace(",", "."))
    price["currency"] = \
        soup.select("#productPageRightSectionTop-saleAction-price-current")[0].attrs.get("data-price")[-1]
    return price


def get_isbn(soup):
    return soup.select("#productPageSectionDetails-collapseDetalhes-content-isbn > .info")[0].string


def get_photo_url(soup):
    return soup.select("#productPageLeftSectionTop-image img")[0]["src"]

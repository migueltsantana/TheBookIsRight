import os
import sys

import utils

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bs4 import BeautifulSoup
from models import Book


def get_info(url):
    soup = request_page(url)
    price = get_price(soup)
    return Book(int(get_isbn(soup)), price["promo_price"], price["regular_price"],
                price["currency"], "Amazon", url, get_photo_url(soup))


def get_price(soup):
    price = {"promo_price": None, "regular_price": None}
    try:
        if soup.select("#buyBoxInner > ul > li > span > .a-text-strike") != []:
            price["regular_price"] = float(soup.select("#buyBoxInner > ul > li > span > .a-text-strike")[0].string[:-2].replace(",", "."))
            price["promo_price"] = float(soup.select(".offer-price")[0].string[:-2].replace(",", "."))
        else:
            price["regular_price"] = float(soup.select(".offer-price")[0].string[:-2].replace(",", "."))
        price["currency"] = soup.select(".offer-price")[0].string[-1]
    except ValueError:
        if soup.select("#buyBoxInner > ul > li > span > .a-text-strike") != []:
            price["regular_price"] = float(soup.select("#buyBoxInner > ul > li > span > .a-text-strike")[0].string[1:].replace(",", "."))
            price["promo_price"] = float(soup.select(".offer-price")[0].string[1:].replace(",", "."))
        else:
            price["regular_price"] = float(soup.select(".offer-price")[0].string[1:].replace(",", "."))
        price["currency"] = soup.select(".offer-price")[0].string[0]
    return price


def get_isbn(soup):
    return soup.select_one('span.a-text-bold:contains("ISBN-13"), b:contains("ISBN-13")')\
        .find_parent().text.split(':')[-1].strip().replace("-", "")


def get_photo_url(soup):
    return soup.select("#imgBlkFront")[0]["src"]


def request_page(url):
    headers = {
        "Host": ("https://" + url.split("://")[1].split("/")[0] + "/").split("://")[1].split("/")[0],
        "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    utils.get_page("https://" + url.split("://")[1].split("/")[0] + "/", headers=headers)
    html = utils.get_page(url, headers=headers)
    return BeautifulSoup(html, features="lxml")

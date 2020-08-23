import os
import sys
from urllib.parse import urljoin

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from bs4 import BeautifulSoup
from models import Book


def get_info(url):
    html = utils.get_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    price = get_price(soup)
    return Book(int(get_isbn(soup)), price["promo_price"], price["regular_price"],
                price["currency"], "LeyaOnline", url, urljoin(url, get_photo_url(soup)))


def get_price(soup):
    price = {"promo_price": None, "regular_price": None}
    if soup.select(".pvp") != []:
        price["promo_price"] = float(soup.select(".price")[0].string.strip()[2:].replace(",", "."))
        price["regular_price"] = float(soup.select(".pvp > span")[1].string.strip()[2:].replace(",", "."))
    else:
        price["regular_price"] = float(soup.select(".price")[0].string.strip()[2:].replace(",", "."))
    price["currency"] = soup.select(".price")[0].string.strip()[0]
    return price


def get_isbn(soup):
    return soup.find("span", itemprop="identifier").string.strip()


def get_photo_url(soup):
    return soup.select(".img > a > img")[0]["src"]

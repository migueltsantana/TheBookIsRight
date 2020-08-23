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
                price["currency"], "PACTOR", url, urljoin(url, get_photo_url(soup)))


def get_price(soup):
    return {
        "promo_price": float(soup.select(".precoDetalhe > span")[0].nextSibling.strip()[2:].replace(",", ".")),
        "regular_price": float(soup.select(".precoDetalhe > span")[0].string[2:].replace(",", ".")),
        "currency": soup.select(".precoDetalhe > span")[0].string[0]
    }


def get_isbn(soup):
    return soup.select("#listSpecsDetalhe .impar > td")[1].string[6:].replace("-", "")


def get_photo_url(soup):
    return soup.select("#tabLivro > .bgDetalheLivro > .capaLivroDetalhe > a > img")[0]["src"]

import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from boto3.dynamodb.conditions import Attr, Key
from bs4 import BeautifulSoup
from jinja2 import Environment, select_autoescape, FileSystemLoader

from models import RowItem
from settings import FROM_EMAIL, TO_EMAIL, SMTP_USERNAME, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT


def distinct(books):
    """
    Remove unnecessary repeating book rows from the database query
    :param books: list of book dictionaries
    :return: list with distinct books based on the input list
    """
    analysed = {}
    distinct_books = []
    for book in books:
        if book["url"] not in analysed.get(book["isbn"], []):
            if book["isbn"] in analysed:
                analysed[book["isbn"]].append(book["url"])
            else:
                analysed[book["isbn"]] = [book["url"]]
            distinct_books.append(book)
    return distinct_books


def get_book_to_watch_qty(db, isbn):
    """
    Get the number of different bookstores with the same book to watch
    :param db: the instance of the database
    :param isbn: the ISBN-13 of the book
    :return: the number of bookstores
    """
    return len(db.Table("books_to_watch").scan(
        FilterExpression=Attr("watch_status").eq(True) & Attr("isbn").eq(isbn)
    )["Items"])


def order_promo_prices(array, offer):
    """
    Order a list of books based on the 'promo_price' attribute
    :param array: the list to sort
    :param offer: the best offer available
    :return: a sorted list without the best offer
    """
    offers = sorted(array, key=lambda i: i["promo_price"])
    offers.remove(offer)
    return offers


def get_cheapest_offer(array):
    """
    Order a list of books based on the 'promo_price' attribute
    :param array: the list to sort
    :return: the cheapest book available
    """
    return sorted(array, key=lambda i: i["promo_price"])[0]


def get_similar_offers(data, max_len_offers):
    """
    Order a list of books based on the 'timestamp' attribute to get the similar offers available
    :param data: the list to sort
    :param max_len_offers: the maximum number of elements
    :return: the similar offers for a book
    """
    return sorted(data, key=lambda i: i["timestamp"], reverse=True)[:max_len_offers]


def strptime_to_str(timestamp):
    """
    Return a string representation of the date only given a timestamp string
    :param timestamp: string representation of time in the format '%Y-%m-%d %H:%M:%S.%f'
    :return: the date string of the given timestamp
    """
    return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').date()


def get_lowest_values(ordered_list):
    """
    Create all the lowest values for the e-mail construction
    :param ordered_list: the ordered list based on the 'promo_price' attribute
    :return: lowest, lowest_date, lowest_price_discount, lowest_bookstore variables
    """
    lowest = f"{ordered_list[0]['promo_price']}{ordered_list[0]['currency']}"
    lowest_date = strptime_to_str(ordered_list[0]["timestamp"])
    lowest_price_discount = (1 - float(ordered_list[0]["promo_price"]) / float(
        ordered_list[0]["regular_price"])) * 100
    lowest_bookstore = ordered_list[0]["bookstore"]
    return lowest, lowest_date, lowest_price_discount, lowest_bookstore


def get_highest_values(ordered_list):
    """
    Create all the highest values for the e-mail construction
    :param ordered_list: the ordered list based on the 'promo_price' attribute
    :return: highest, highest_date, highest_price_discount, highest_bookstore variables
    """
    highest = f"{ordered_list[-1]['promo_price']}{ordered_list[-1]['currency']}"
    highest_date = strptime_to_str(ordered_list[-1]["timestamp"])
    highest_price_discount = (1 - float(ordered_list[-1]["promo_price"]) / float(
        ordered_list[-1]["regular_price"])) * 100
    highest_bookstore = ordered_list[-1]["bookstore"]
    return highest, highest_date, highest_price_discount, highest_bookstore


def preprocess(db):
    """
    The preprocessing of the data collected
    :param db: the instance of the database
    :return: instances of RowItem splitted into groups of 3
    """
    books = db.Table("books_to_watch").scan(
        FilterExpression=Attr("watch_status").eq(True)
    )["Items"]
    content = []
    seen = []
    for book in books:
        if book["isbn"] not in seen:
            data = db.Table("books_price_data").query(KeyConditionExpression=Key("isbn").eq(book["isbn"]))["Items"]
            ordered_list = sorted(data, key=lambda i: i["promo_price"])
            lowest, lowest_date, lowest_price_discount, lowest_bookstore = get_lowest_values(ordered_list)
            highest, highest_date, highest_price_discount, highest_bookstore = get_highest_values(ordered_list)
            max_len_offers = get_book_to_watch_qty(db, book["isbn"])
            current_price = get_cheapest_offer(get_similar_offers(data, max_len_offers))
            current_discount = (1 - float(current_price["promo_price"]) / float(current_price["regular_price"])) * 100
            other_offers = order_promo_prices(get_similar_offers(data, max_len_offers), current_price)
            content.append(RowItem(book["isbn"], current_price["promo_price"], current_price["regular_price"],
                                   current_price["currency"], current_price["bookstore"], current_price["url"],
                                   highest, highest_date, highest_price_discount, highest_bookstore, lowest,
                                   lowest_date, lowest_price_discount, lowest_bookstore, current_discount,
                                   current_price["photo_url"], other_offers))
            seen.append(book["isbn"])
    return [content[i * 3:(i + 1) * 3] for i in range((len(content) + 3 - 1) // 3)]


def send(data):
    """
    Send the e-mail with all the information collected
    :param data: data previously collected and analyzed in preprocess method
    """
    sender = formataddr((str(Header('The Book Is Right', 'utf-8')), FROM_EMAIL))
    receiver = TO_EMAIL

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Fresh book prices!"
    msg['From'] = sender
    msg['To'] = receiver

    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('mail.html')

    # Create the body of the message (a plain-text and an HTML version).
    html = template.render(rows=data)
    text = BeautifulSoup(html, features="html.parser").get_text('\n')

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(sender, receiver, msg.as_string())

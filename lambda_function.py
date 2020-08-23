from boto3.dynamodb.conditions import Attr

import utils
import bookstores
import mail
import tldextract


def lambda_handler(event, context):
    """
    The main function to execute
    :param event: the event argument provided by AWS
    :param context: the context argument provided by AWS
    """
    db = utils.get_db()
    get_books_to_watch(db)
    for book in get_books_to_watch(db):
        getattr(bookstores, tldextract.extract(book["url"]).domain).get_info(book["url"]).store(db)
    mail.send(mail.preprocess(db))


def get_books_to_watch(db):
    """
    Get all the books to scrape prices
    :param db: the instance of the database
    :return: the filtered database items
    """
    response = db.Table("books_to_watch").scan(
        FilterExpression=Attr("watch_status").eq(True)
    )
    return response['Items']

from datetime import datetime
from decimal import Decimal


class Book:
    """
    The object representation for Book
    """
    def __init__(self, isbn, promo_price, regular_price, currency, bookstore, url, photo_url):
        """
        The constructor for Book
        :param isbn: the ISBN-13 of the book
        :param promo_price: the promotional price of the book (if non-existent, keep the same as regular_price
        :param regular_price: the price of the book with no discounts
        :param currency: the currency of promo_price and regular_price
        :param bookstore: the bookstore that sells the Book
        :param url: the url of the book in the bookstore
        :param photo_url: the url of the photo of the book
        """
        self.isbn = isbn
        self.promo_price = promo_price
        self.regular_price = regular_price
        self.currency = currency
        self.bookstore = bookstore
        self.url = url
        self.photo_url = photo_url

    def get_isbn(self):
        """
        Get the isbn attribute
        :return: the isbn attribute of a Book instance
        """
        return self.isbn

    def set_isbn(self, isbn):
        """
        Set the isbn attribute
        :param isbn: the new isbn to set
        """
        self.isbn = isbn

    def get_promo_price(self):
        """
        Get the promo_price attribute
        :return: the promo_price attribute of a Book instance
        """
        return self.promo_price

    def set_promo_price(self, promo_price):
        """
        Set the promo_price attribute
        :param promo_price: the new promo_price to set
        """
        self.promo_price = promo_price

    def get_regular_price(self):
        """
        Get the regular_price attribute
        :return: the regular_price attribute of a Book instance
        """
        return self.regular_price

    def set_regular_price(self, regular_price):
        """
        Set the regular_price attribute
        :param regular_price: the new regular_price to set
        """
        self.regular_price = regular_price

    def get_currency(self):
        """
        Get the currency attribute
        :return: the currency attribute of a Book instance
        """
        return self.currency

    def set_currency(self, currency):
        """
        Set the currency attribute
        :param currency: the new currency to set
        """
        self.currency = currency

    def get_bookstore(self):
        """
        Get the bookstore attribute
        :return: the bookstore attribute of a Book instance
        """
        return self.bookstore

    def set_bookstore(self, bookstore):
        """
        Set the bookstore attribute
        :param bookstore: the new bookstore to set
        """
        self.bookstore = bookstore

    def get_url(self):
        """
        Get the url attribute
        :return: the url attribute of a Book instance
        """
        return self.url

    def set_url(self, url):
        """
        Set the url attribute
        :param url: the new url to set
        """
        self.url = url

    def get_photo_url(self):
        """
        Get the photo_url attribute
        :return: the photo_url attribute of a Book instance
        """
        return self.photo_url

    def set_photo_url(self, photo_url):
        """
        Set the photo_url attribute
        :param photo_url: the new photo_url to set
        """
        self.photo_url = photo_url

    def store(self, db):
        """
        Store this Book instance in the database
        :param db: the instance of the database
        """
        db.Table("books_price_data").put_item(
            Item={
                "isbn": self.isbn,
                "promo_price": Decimal(str(self.promo_price))
                if self.promo_price is not None else Decimal(str(self.regular_price)),
                "regular_price": Decimal(str(self.regular_price)),
                "currency": self.currency,
                "bookstore": self.bookstore,
                "url": self.url,
                "photo_url": self.photo_url,
                "timestamp": str(datetime.now())
            }
        )

    def __str__(self):
        """
        The __str__ method
        :return: the string representation of the Book instance
        """
        return f'Book(isbn={self.isbn},promo_price={self.promo_price},regular_price={self.regular_price},' \
               f'currency={self.currency},bookstore={self.bookstore},url={self.url}),photo_url={self.photo_url}'

    def __eq__(self, other):
        """
        The __eq__ method
        :param other: the other instance of Book
        :return: boolean from the comparison of the isbn attribute of both instances
        """
        return self.isbn == other.isbn

    def __lt__(self, other):
        """
        The __lt__ method
        :param other: the other instance of Book
        :return: boolean from the comparison of the regular_price and promo_price attributes of both instances
        """
        return self.regular_price < other.regular_price or self.promo_price < other.promo_price


class RowItem(Book):
    """
    The object representation for RowItem
    """
    def __init__(self, isbn, promo_price, regular_price, currency, bookstore, url, highest_price,
                 highest_price_date, highest_price_discount, highest_price_bookstore, lowest_price,
                 lowest_price_date, lowest_price_discount, lowest_price_bookstore, current_price_discount,
                 photo_url, other_offers):
        """
        The constructor for Book
        :param isbn: the ISBN-13 of the book
        :param promo_price: the promotional price of the book (if non-existent, keep the same as regular_price
        :param regular_price: the price of the book with no discounts
        :param currency: the currency of promo_price and regular_price
        :param bookstore: the bookstore that sells the Book
        :param url: the url of the book in the bookstore
        :param highest_price: the highest price recorded of this book
        :param highest_price_date: the date of the highest price recorded of this book
        :param highest_price_discount: the discount of the highest price recorded of this book
        :param highest_price_bookstore: the bookstore of the highest price recorded of this book
        :param lowest_price: the lowest price recorded of this book
        :param lowest_price_date: the date of the lowest price recorded of this book
        :param lowest_price_discount: the discount of the lowest price recorded of this book
        :param lowest_price_bookstore: the bookstore of the lowest price recorded of this book
        :param current_price_discount: the discount of the current price of this book
        :param photo_url: the url of the photo of the book
        :param other_offers: the other offers available for this book
        """
        super().__init__(isbn, promo_price, regular_price, currency, bookstore, url, photo_url)
        self.current_price_discount = current_price_discount
        self.highest_price = highest_price
        self.highest_price_date = highest_price_date
        self.highest_price_discount = highest_price_discount
        self.highest_price_bookstore = highest_price_bookstore
        self.lowest_price = lowest_price
        self.lowest_price_date = lowest_price_date
        self.lowest_price_discount = lowest_price_discount
        self.lowest_price_bookstore = lowest_price_bookstore
        self.other_offers = other_offers

    def __str__(self):
        """
        The __str__ method
        :return: the string representation of the RowItem instance
        """
        return f'RowItem(isbn={self.isbn},promo_price={self.promo_price},regular_price={self.regular_price},' \
               f'currency={self.currency},current_price_discount={self.current_price_discount}, ' \
               f'bookstore={self.bookstore}, url={self.url},highest_price={self.highest_price}, ' \
               f'highest_price_date={self.highest_price_date},highest_price_discount={self.highest_price_discount},' \
               f'highest_price_bookstore={self.highest_price_bookstore}, lowest_price={self.lowest_price},' \
               f'lowest_price_date={self.lowest_price}, lowest_price_discount={self.lowest_price_discount},' \
               f'lowest_price_bookstore={self.lowest_price_bookstore}, photo_url={self.photo_url}, ' \
               f'other_offers={self.other_offers})'

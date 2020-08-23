import requests
import boto3

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION


def get_page(url, headers=None):
    """
    Get the page HTML content
    :param headers: the headers dictionary to add to the request object
    :param url: the url to extract the contents
    :return: Request content of the given url
    """
    if headers:
        result = requests.get(url, headers=headers)
    else:
        result = requests.get(url)
    if result.status_code != 200:
        result.raise_for_status()
    else:
        return result.content


def get_db():
    """
    Start a dynamodb session with boto3
    :return: boto3's Session object
    """
    return boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    ).resource("dynamodb")

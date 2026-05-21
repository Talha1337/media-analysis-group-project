"""A load script to interact with DynamoDB on AWS."""

from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import ClientError


def connect_to_dynamodb() -> BaseClient:
    """Initialise connection to DynamoDB."""


def assign_feed_id(feed_link: str) -> str:
    """Assigns a unique feed ID based on the feed link."""


def assign_article_id(article_link: str) -> str:
    """Assigns a unique article ID based on the article link."""


def generate_article_sk(published_at: str, feed_id: str, article_id: str) -> str:
    """Creates a unique article SK with the format: 
    ARTICLE#[feed_id]#[published_at]#[article_id]"""


def prepare_item_for_load(article: dict, name: str) -> dict:
    """Converts enriched data for each article to DynamoDB item format with: 
    PK (name), SK, feed_id, names, published_at, sentiment_score, key_words."""


def load_all_items(articles: list[dict]) -> None:
    """Batch loads items into DynamoDB, partitioned by each identified name."""
    

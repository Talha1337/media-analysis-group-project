"""A load script to interact with DynamoDB on AWS."""

from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import ClientError


def connect_to_dynamodb() -> BaseClient:
    """Initialise connection to DynamoDB."""


def assign_feed_id(feed_name: str) -> str:
    """Assigns a unique feed ID based on the feed name."""


def generate_article_sort_key(published_at: str, feed_id: str, article_id: str) -> str:
    """Creates a unique article SK with the format: 
    ARTICLE#[feed_id]#[published_at]#[article_id]"""


def prepare_item_for_load(enriched_article: dict, name: str) -> dict:
    """Converts enriched data for each article to DynamoDB item format with: 
    PK (name), SK, feed_id, names, published_at, sentiment_score, key_words."""


def load_all_items(enriched_articles: list[dict]) -> None:
    """Batch loads items into DynamoDB, partitioned by each identified name."""
    

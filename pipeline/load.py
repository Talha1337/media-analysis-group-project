"""A load script to interact with DynamoDB on AWS."""

from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import ClientError


def connect_to_dynamodb() -> BaseClient:
    """Initialize connection to DynamoDB table."""


def assign_feed_id(feed_name: str) -> str:
    """Assigns a unique feed ID based on the feed name."""


def generate_article_sort_key(published_at: str, feed_id: str) -> str:
    """Creates a unique article SK with the format: 
    ARTICLE#[feed_id]#[published_at]#[title_hash]"""


def prepare_item_for_load(article: dict, public_figure_name: str) -> dict:
    """Converts enriched data for each article to DynamoDB item format with: 
    PK, SK, feed_id, names, published_at, sentiment, keywords."""


def load_all_items(enriched_articles: list[dict]) -> None:
    """Batch loads items into DynamoDB, partitioned by public figure."""
    

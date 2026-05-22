"""A load script to interact with DynamoDB on AWS."""
# pylint: disable=logging-fstring-interpolation

import logging
import hashlib
from boto3 import client
from botocore.client import BaseClient
from botocore.exceptions import ClientError

log = logging.getLogger(__name__)

URL_PARTS = ["https://", "http://", "news.", ".com", ".co.uk"]


def connect_to_dynamodb() -> BaseClient:
    """Initialise connection to DynamoDB."""
    try:
        dynamodb = client("dynamodb")
        log.info("Successfully connected to DynamoDB.")
        return dynamodb

    except ClientError as e:
        log.exception(f"Failed to connect to DynamoDB: {e}")
        raise


def assign_feed_id(feed_link: str, url_parts: list[str] = URL_PARTS) -> str:
    """Assigns a unique feed ID based on the feed link."""
    for item in url_parts:
        feed_link = feed_link.replace(item, "")

    feed_id = feed_link.replace("/", "_").lower()
    log.debug(f"Assigned feed ID: {feed_id}")
    return feed_id


def assign_article_id(article_link: str) -> str:
    """Assigns a unique article ID based on the article link."""
    article_id = hashlib.md5(article_link.encode()).hexdigest()[:5]
    log.info(f"Generated article ID: {article_id}")
    return article_id


def generate_article_sk(published_at: str, feed_id: str, article_id: str) -> str:
    """Creates a unique article sort key."""
    return f"ARTICLE#{feed_id}#{published_at}#{article_id}"


def prepare_item_for_load(
    article: dict, name: str, url_parts: list[str] = URL_PARTS
) -> dict:
    """Converts enriched data for each article to DynamoDB item format with:
    PK (name), SK, feed_id, names, published_at, sentiment_score, key_words."""
    try:
        feed_id = assign_feed_id(article["feed_link"], url_parts)
        article_id = assign_article_id(article["article_link"])
        sort_key = generate_article_sk(
            article["published_at"], feed_id, article_id)
    except KeyError as e:
        log.error(f"Missing expected article field: {e}")
        raise

    return {
        "PK": {"S": name},
        "SK": {"S": sort_key},
        "feed_id": {"S": feed_id},
        "names": {"SS": article["names"]},
        "published_at": {"S": article["published_at"]},
        "sentiment_score": {"N": str(article["sentiment_score"])},
        "key_words": {"SS": article["key_words"]},
    }


def find_existing_items(
    dynamodb,
    table_name: str,
    name: str,
    published_at: str,
    feed_id: str,
) -> list:
    """Checks for existing items in DynamoDB for a given name to prevent duplicates."""
    sk_prefix = f"ARTICLE#{feed_id}#{published_at}#"
    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :name AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":name": {"S": name},
                ":sk_prefix": {"S": sk_prefix},
            },
        )
        return response.get("Items", [])
    except ClientError as e:
        print(f"Failed to query DynamoDB: {e}")
        raise


def load_all_items(articles: list[dict], url_parts: list[str] = URL_PARTS) -> None:
    """Batch loads items into DynamoDB, partitioned by each identified name."""
    dynamodb = connect_to_dynamodb()
    requests = []  # Placeholder for batch write requests
    for article in articles:
        if not article["names"]:
            log.warning(
                f"Article {article['article_link']} has no identified names. Skipping."
            )
        else:
            for name in article["names"]:  # For each name, create a separate item
                feed_id = assign_feed_id(article["feed_link"], url_parts)

                existing_items = find_existing_items(
                    dynamodb,
                    "c23-epipelagic-dynamo-public-figures",
                    name,
                    article["published_at"],
                    feed_id,
                )
                if not existing_items:
                    item = prepare_item_for_load(article, name, url_parts)
                    requests.append({"PutRequest": {"Item": item}})

    if requests:
        try:
            dynamodb.batch_write_item(
                RequestItems={
                    "c23-epipelagic-dynamo-public-figures": requests},
            )
            log.info(
                f"Successfully loaded {len(requests)} items into DynamoDB.")
        except ClientError as e:
            log.error(f"Failed to batch load into DynamoDB: {e}")

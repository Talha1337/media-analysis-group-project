"""Tests for load.py using pytest."""
# pylint: disable=redefined-outer-name

from unittest.mock import patch, MagicMock
import pytest
from botocore.exceptions import ClientError
from load import (
    connect_to_dynamodb,
    generate_article_sk,
    assign_article_id,
    assign_feed_id,
    prepare_item_for_load,
    load_all_items
)


@pytest.fixture
def sample_article():
    """Fixture for a sample enriched article."""
    return {
        "article_link": "https://www.bbc.co.uk/news/business/2",
        "published_at": "2026-05-20T13:15:00Z",
        "feed_link": "https://feeds.bbci.co.uk/news/rss.xml",
        "names": ["joe_biden"],
        "sentiment_score": 0.5,
        "key_words": ["markets", "rise", "economic", "data"]
    }


@pytest.fixture
def mock_dynamodb():
    """Fixture for mocked DynamoDB setup."""
    with patch('load.connect_to_dynamodb') as mock_connect, \
            patch('load.prepare_item_for_load') as mock_prepare, \
            patch('load.find_existing_items') as mock_find_existing:
        mock_client = MagicMock()
        mock_client.batch_write_item = MagicMock()

        mock_connect.return_value = mock_client
        mock_prepare.return_value = {"PK": {"S": "test"}}
        mock_find_existing.return_value = []

        yield mock_connect, mock_prepare, mock_find_existing


@pytest.fixture
def url_parts():
    """Fixture for URL parts to strip from feed links."""
    return ["https://", "http://", "news.", ".com", ".co.uk"]


class TestDynamoDBConnection:
    """Test cases for DynamoDB connection."""

    @patch('load.client')
    def test_connect_to_dynamodb_success(self, mock_client):
        """Test successful connection to DynamoDB."""
        mock_client.return_value = "DynamoDB Client"
        result = connect_to_dynamodb()
        assert result == "DynamoDB Client"

    @patch('load.client')
    def test_connect_to_dynamodb_failure(self, mock_client):
        """Test handling of DynamoDB connection failure."""
        mock_client.side_effect = ClientError(
            {"Error": {"Code": "ConnectionError"}}, "Connect")
        with pytest.raises(ClientError):
            connect_to_dynamodb()


class TestGenerateArticleSortKey:
    """Test cases for generating article sort keys."""

    def test_generate_article_sort_key_format(self, url_parts):
        """Test that the generated sort key has the correct format."""
        timestamp = "2026-05-20T13:15:00Z"
        feed_link = "https://feeds.bbci.co.uk/news/rss.xml"
        article_id = "12345"

        feed_id = assign_feed_id(feed_link, url_parts)
        result = generate_article_sk(timestamp, feed_id, article_id)

        parts = result.split('#')
        assert len(parts) == 4
        assert parts[0] == "ARTICLE"
        assert parts[1] == feed_id
        assert parts[2] == timestamp
        assert parts[3] == article_id


class TestAssignFeedID:
    """Test cases for assigning feed IDs."""

    def test_assign_feed_id_consistency(self, url_parts):
        """Test that the same feed link always gets the same feed ID."""
        feed_link = "https://feeds.bbci.co.uk/news/rss.xml"
        feed_id_1 = assign_feed_id(feed_link, url_parts)
        feed_id_2 = assign_feed_id(feed_link, url_parts)
        assert feed_id_1 == "feeds.bbci_news_rss.xml"
        assert feed_id_1 == feed_id_2

    def test_assign_feed_id_uniqueness(self, url_parts):
        """Test that different feed links get different feed IDs."""
        feed_link_1 = "https://feeds.bbci.co.uk/news/rss.xml"
        feed_link_2 = "https://feeds.sky.com/feeds/rss/home.xml"
        feed_id_1 = assign_feed_id(feed_link_1, url_parts)
        feed_id_2 = assign_feed_id(feed_link_2, url_parts)
        assert feed_id_1 == "feeds.bbci_news_rss.xml"
        assert feed_id_2 == "feeds.sky_feeds_rss_home.xml"
        assert feed_id_1 != feed_id_2


class TestAssignArticleID:
    """Test cases for assigning article IDs."""

    def test_assign_article_id_consistency(self):
        """Test that the same article link always gets the same article ID."""
        article_link = "https://www.bbc.co.uk/news/articles/1"
        article_id_1 = assign_article_id(article_link)
        article_id_2 = assign_article_id(article_link)
        assert all([isinstance(article_id_1, str),
                   isinstance(article_id_2, str)])
        assert article_id_1 == article_id_2

    def test_assign_article_id_uniqueness(self):
        """Test that different article links get different article IDs."""
        article_link_1 = "https://www.bbc.co.uk/news/articles/1"
        article_link_2 = "https://www.bbc.co.uk/news/articles/2"
        article_id_1 = assign_article_id(article_link_1)
        article_id_2 = assign_article_id(article_link_2)
        assert article_id_1 != article_id_2


class TestPrepareItemForLoad:
    """Test cases for preparing items for load."""

    def test_prepare_item_for_load_structure(self, sample_article, url_parts):
        """Test that the prepared item has the correct structure."""
        item = prepare_item_for_load(sample_article, "joe_biden", url_parts)

        assert item['PK'] == {"S": "joe_biden"}
        assert 'SK' in item and isinstance(item['SK'], dict)
        assert item['feed_id'] == {"S": assign_feed_id(
            sample_article['feed_link'], url_parts)}
        assert item['published_at'] == {"S": sample_article['published_at']}
        assert item['names'] == {"SS": sample_article['names']}
        assert item['sentiment_score'] == {
            "N": str(sample_article['sentiment_score'])}
        assert item['key_words'] == {"SS": sample_article['key_words']}

    def test_prepare_item_for_load_missing_field(self, url_parts):
        """Test that prepare_item_for_load raises error when required field is missing."""
        article = {
            "article_link": "https://www.bbc.co.uk/news/articles/1",
            "published_at": "2026-05-20T13:15:00Z",
            # Missing feed_link
            "names": ["joe_biden"],
            "sentiment_score": 0.5,
            "key_words": ["markets"]
        }
        with pytest.raises(KeyError):
            prepare_item_for_load(article, "joe_biden", url_parts)


class TestLoadAllItems:
    """Test cases for loading all items into DynamoDB."""

    def test_load_all_items_calls_prepare_and_connect(self, mock_dynamodb,
                                                      sample_article, url_parts):
        """Test that load_all_items calls prepare_item_for_load and connect_to_dynamodb."""
        mock_connect, mock_prepare, mock_find_existing = mock_dynamodb

        # PK and SK aren't in the enriched articles, they're generated in prepare_item_for_load
        enriched_articles = [sample_article]
        load_all_items(enriched_articles, url_parts)

        mock_connect.assert_called_once()
        mock_prepare.assert_called_once_with(
            enriched_articles[0], "joe_biden", url_parts)
        mock_find_existing.assert_called_once()


    def test_load_all_items_batch_loads_with_partitioning(self, mock_dynamodb,
                                                          sample_article, url_parts):
        """Test that load_all_items batch loads multiple articles partitioned by name."""
        mock_connect, mock_prepare, mock_find_existing = mock_dynamodb

        enriched_articles = [
            sample_article,
            {
                "article_link": "https://news.sky.com/technology/articles/1",
                "published_at": "2026-05-21T10:00:00Z",
                "feed_link": "https://feeds.skynews.com/feeds/rss/technology.xml",
                "names": ["joe_biden", "elon_musk"],
                "sentiment_score": 0.7,
                "key_words": ["tech", "innovation"]
            }
        ]
        load_all_items(enriched_articles, url_parts)

        mock_connect.assert_called_once()
        assert mock_prepare.call_count == 3
        assert mock_find_existing.call_count == 3

        mock_prepare.assert_any_call(
            enriched_articles[0], "joe_biden", url_parts)
        mock_prepare.assert_any_call(
            enriched_articles[1], "joe_biden", url_parts)
        mock_prepare.assert_any_call(
            enriched_articles[1], "elon_musk", url_parts)

    def test_load_all_items_empty_names_list(self, mock_dynamodb, url_parts):
        """Test that load_all_items handles article with empty names list."""
        mock_connect, mock_prepare, mock_find_existing = mock_dynamodb

        enriched_articles = [
            {
                "article_link": "https://www.bbc.co.uk/news/articles/1",
                "published_at": "2026-05-20T13:15:00Z",
                "feed_link": "https://feeds.bbci.co.uk/news/rss.xml",
                "names": [],  # Empty names
                "sentiment_score": 0.5,
                "key_words": ["test"]
            }
        ]
        load_all_items(enriched_articles, url_parts)

        mock_connect.assert_called_once()
        mock_prepare.assert_not_called()  # Should not call prepare if no names
        mock_find_existing.assert_not_called()  # Should not call find_existing if no names

"""Tests for load.py using pytest."""

import pytest
from unittest.mock import patch
from load import (
    connect_to_dynamodb,
    generate_article_sort_key,
    assign_feed_id,
    prepare_item_for_load,
    load_all_items
)

@pytest.fixture
def sample_article():
    """Fixture for a sample enriched article."""
    return {
        "title": "Markets Rise on Economic Data",
        "published_at": "2026-05-20T13:15:00Z",
        "feed_name": "BBC News - Home",
        "names": ["joe_biden"],
        "sentiment_score": 0.5,
        "key_words": ["markets", "rise", "economic", "data"]
    }

@pytest.fixture
def mock_dynamodb():
    """Fixture for mocked DynamoDB setup."""
    with patch('load.connect_to_dynamodb') as mock_connect, \
         patch('load.prepare_item_for_load') as mock_prepare:
        mock_connect.return_value = "DynamoDB Client"
        mock_prepare.return_value = {"PK": "test"}
        yield mock_connect, mock_prepare


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
        from botocore.exceptions import ClientError
        mock_client.side_effect = ClientError({"Error": {"Code": "ConnectionError"}}, "Connect")
        with pytest.raises(ClientError):
            connect_to_dynamodb()


class TestGenerateArticleSortKey:
    """Test cases for generating article sort keys."""

    def test_generate_article_sort_key_format(self):
        """Test that the generated sort key has the correct format."""
        timestamp = "2026-05-20T13:15:00Z"
        feed_name = "BBC News - Home"
        article_id = "12345"

        feed_id = assign_feed_id(feed_name)
        result = generate_article_sort_key(timestamp, feed_id, article_id)

        parts = result.split('#')
        assert len(parts) == 4
        assert parts[0] == "ARTICLE"
        assert parts[1] == feed_id
        assert parts[2] == timestamp
        assert parts[3] == article_id


class TestAssignFeedID:
    """Test cases for assigning feed IDs."""

    def test_assign_feed_id_consistency(self):
        """Test that the same feed name always gets the same feed ID."""
        feed_name = "BBC News - Home"
        feed_id1 = assign_feed_id(feed_name)
        feed_id2 = assign_feed_id(feed_name)
        assert feed_id1 == "BBC"
        assert feed_id1 == feed_id2

    def test_assign_feed_id_uniqueness(self):
        """Test that different feed names get different feed IDs."""
        feed_name1 = "BBC News - Home"
        feed_name2 = "Sky News - Home"
        feed_id1 = assign_feed_id(feed_name1)
        feed_id2 = assign_feed_id(feed_name2)
        assert feed_id1 == "BBC"
        assert feed_id2 == "SKY"
        assert feed_id1 != feed_id2


class TestPrepareItemForLoad:
    """Test cases for preparing items for load."""

    def test_prepare_item_for_load_structure(self, sample_article):
        """Test that the prepared item has the correct structure."""
        item = prepare_item_for_load(sample_article, "joe_biden")

        assert item['PK'] == "joe_biden"
        assert 'SK' in item and isinstance(item['SK'], str)
        assert item['feed_id'] == assign_feed_id(sample_article['feed_name'])
        assert item['published_at'] == sample_article['published_at']
        assert item['names'] == sample_article['names']
        assert item['sentiment_score'] == sample_article['sentiment_score']
        assert item['key_words'] == sample_article['key_words']


    def test_prepare_item_for_load_missing_field(self):
        """Test that prepare_item_for_load raises error when required field is missing."""
        article = {
            "title": "Markets Rise",
            "published_at": "2026-05-20T13:15:00Z",
            # Missing feed_name
            "names": ["joe_biden"],
            "sentiment_score": 0.5,
            "key_words": ["markets"]
        }
        with pytest.raises(KeyError):
            prepare_item_for_load(article, "joe_biden")


class TestLoadAllItems:
    """Test cases for loading all items into DynamoDB."""

    def test_load_all_items_calls_prepare_and_connect(self, mock_dynamodb, sample_article):
        """Test that load_all_items calls prepare_item_for_load and connect_to_dynamodb."""
        mock_connect, mock_prepare = mock_dynamodb

        # PK and SK aren't in the enriched articles, they're generated in prepare_item_for_load
        enriched_articles = [sample_article]
        load_all_items(enriched_articles)

        mock_connect.assert_called_once()
        mock_prepare.assert_called_once_with(enriched_articles[0], "joe_biden")


    def test_load_all_items_batch_loads_with_partitioning(self, mock_dynamodb, sample_article):
        """Test that load_all_items batch loads multiple articles partitioned by name."""
        mock_connect, mock_prepare = mock_dynamodb

        enriched_articles = [
            sample_article,
            {
                "title": "Tech Innovations in 2026",
                "published_at": "2026-05-21T10:00:00Z",
                "feed_name": "SKY News - Technology",
                "names": ["joe_biden", "elon_musk"],
                "sentiment_score": 0.7,
                "key_words": ["tech", "innovation"]
            }
        ]       
        load_all_items(enriched_articles)

        mock_connect.assert_called_once()
        assert mock_prepare.call_count == 3

        mock_prepare.assert_any_call(enriched_articles[0], "joe_biden")
        mock_prepare.assert_any_call(enriched_articles[1], "joe_biden")
        mock_prepare.assert_any_call(enriched_articles[1], "elon_musk")


    def test_load_all_items_empty_names_list(self, mock_dynamodb):
        """Test that load_all_items handles article with empty names list."""
        mock_connect, mock_prepare = mock_dynamodb
        
        enriched_articles = [
            {
                "title": "Article with no names",
                "published_at": "2026-05-20T13:15:00Z",
                "feed_name": "BBC News - Home",
                "names": [],  # Empty names
                "sentiment_score": 0.5,
                "key_words": ["test"]
            }
        ]  
        load_all_items(enriched_articles)
        
        mock_connect.assert_called_once()
        mock_prepare.assert_not_called()  # Should not call prepare if no names

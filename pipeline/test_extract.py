"""Testing the extract script with pytest."""

import pytest
from unittest.mock import patch
from extract import extract_all_rss_feeds, extract_rss_feed


@pytest.fixture
def valid_input():
    """Fixture for valid input data."""
    return "http://example.com/rss"


@pytest.fixture
def mock_feedparser_response():
    """Fixture for mocked feedparser response data."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.feed = {
        'title': 'BBC News - Home',
        'link': 'https://www.bbc.co.uk/news',
        'updated': 'Wed, 20 May 2026 14:30:00 GMT',
    }
    mock_response.entries = [
        {
            'title': 'Breaking: Tech Company Announces New Product',
            'link': 'https://www.bbc.co.uk/news/tech/article1',
            'published': 'Wed, 20 May 2026 14:25:00 GMT',
            'summary': 'A major technology company has announced a new product today.',
        },
        {
            'title': 'Markets Rise on Economic Data',
            'link': 'https://www.bbc.co.uk/news/business/article2',
            'published': 'Wed, 20 May 2026 13:15:00 GMT',
            'summary': 'Financial markets increased following positive economic indicators.',
        }
    ]
    return mock_response


class TestExtractURLs:
    """Test cases for invalid inputs to the extract script."""

    @pytest.mark.parametrize("invalid_urls", [
        None,
        1239,
        [],
        12.39,
        True
    ])
    def test_extract_rss_feed_invalid_type(self, invalid_urls):
        """Test that extraction raises an error for invalid input types."""
        with pytest.raises(TypeError):
            extract_rss_feed(invalid_urls)

    @pytest.mark.parametrize("valid_urls", [
        "http://example.com/rss",
        "https://example.com/feed",
        "http://example.com/rss.xml",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml"
    ])
    @patch('extract.feedparser.parse')
    def test_extract_rss_feed_valid(self, mock_parse, valid_urls, mock_feedparser_response):
        """Test that extraction works for valid input types."""
        mock_parse.return_value = mock_feedparser_response
        extract_rss_feed(valid_urls)


class TestExtractFeedData:
    """Test cases for outputs from the extract script."""

    def test_extract_all_rss_feeds_output_type(self):
        """Test that the output of extract_all_rss_feeds is a list."""
        result = extract_all_rss_feeds()
        assert isinstance(result, list)

    def test_extract_rss_feed_output_type(self, mock_feedparser_response):
        """Test that the output of extract_rss_feed is a dictionary."""
        with patch('extract.feedparser.parse', return_value=mock_feedparser_response):
            result = extract_rss_feed('http://example.com/rss')
            assert isinstance(result, dict)

    @patch('extract.feedparser.parse')
    def test_extract_rss_feed_structure(self, mock_parse, mock_feedparser_response):
        """Test that extract_rss_feed returns correct structure."""
        mock_parse.return_value = mock_feedparser_response

        result = extract_rss_feed('http://example.com/rss')
        assert result['feed_name'] == 'BBC News - Home'
        assert result['feed_link'] == 'https://www.bbc.co.uk/news'
        assert len(result['entries']) == 2

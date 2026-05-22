"""Tests for the transform functions in transform.py."""

import pytest

from transform import (
    find_names,
    find_sentiment,
    get_key_words,
    enrich_data,
    enrich_all_data,
    normalise_name,
)


class TestFindName:
    """Tests for the find_names function."""

    @pytest.mark.parametrize(
        "content, expected_names",
        [
            (
                "President Joe Biden met with Prime Minister Boris Johnson.",
                ["Joe Biden", "Boris Johnson"],
            ),
            ("Elon Musk announced a new Tesla model.", ["Elon Musk"]),
        ],
    )
    def test_find_names(self, content, expected_names):
        """Test the find_names function with a sample content."""
        assert find_names(content) == expected_names

    @pytest.mark.parametrize(
        "content, expected_names",
        [
            ("Trump did something.", ["Trump"]),
            ("Merkel and Macron attended the summit.", ["Merkel", "Macron"]),
            ("Tesla's CEO is Elon Musk.", ["Elon Musk"]),
            ("Apple owner Steve Jobs.", ["Steve Jobs"]),
        ],
    )
    def test_find_names_single_name(self, content, expected_names):
        """Test the find_names function with content containing a single name."""
        assert find_names(content) == expected_names

    def test_find_names_invalid_input(self):
        """Test the find_names function with invalid input."""
        with pytest.raises(TypeError):
            find_names(123)  # Non-string input should raise an error

    def test_find_names_empty_string(self):
        """Test the find_names function with an empty string."""
        with pytest.raises(ValueError):
            find_names("")  # Empty string should raise an error

    def test_find_names_no_names(self):
        """Test the find_names function with content that has no names."""
        with pytest.raises(ValueError):
            find_names(
                "This is a sentence without any names."
            )  # No names should raise an error


class TestFindSentiment:
    """Tests for the find_sentiment function."""

    @pytest.mark.parametrize(
        "content",
        [
            ("I love this new policy! It's fantastic."),
            ("This is an amazing day for science and technology."),
            ("We are thrilled with the progress made on this project."),
        ],
    )
    def test_find_sentiment_positive(self, content):
        """Test the find_sentiment function with sample positive content."""
        assert find_sentiment(content) > 0

    @pytest.mark.parametrize(
        "content",
        [
            ("I hate this new policy! It's terrible."),
            ("This is a horrible day for science and technology."),
            ("We are disappointed with the progress made on this project."),
        ],
    )
    def test_find_sentiment_negative(self, content):
        """Test the find_sentiment function with sample negative content."""
        assert find_sentiment(content) < 0

    @pytest.mark.parametrize(
        "content",
        [
            ("There is a chair on the table."),
            ("The sky is blue and the grass is green."),
            ("This is a neutral statement without strong sentiment."),
        ],
    )
    def test_find_sentiment_neutral(self, content):
        """Test the find_sentiment function with sample neutral content."""
        assert -0.1 < find_sentiment(content) < 0.1


class TestFindKeywords:
    """Tests for the get_key_words function."""

    def test_get_key_words_correct_type(self):
        """Test that get_key_words returns a list of strings."""
        content = "This is a test sentence to extract key words."
        result = get_key_words(content)
        assert isinstance(result, list)
        assert all(isinstance(word, str) for word in result)

    def test_get_key_words_empty_string(self):
        """Test that get_key_words raises an error for an empty string."""
        with pytest.raises(ValueError):
            get_key_words("")

    def test_get_key_words_nonsensical(self):
        """Test that get_key_words raises an error for nonsensical input."""
        with pytest.raises(ValueError):
            get_key_words("asldkfj asldkfj asldkfj")


class TestEnrichData:
    """Tests for the enrich_data function."""

    @pytest.fixture
    def sample_article(self):
        """Provides a sample article content dictionary for testing."""
        return {
            "title": "Biden and Johnson Discuss Climate Change",
            "summary": "Joe Biden met with Boris Johnson to discuss climate change.",
        }

    def test_enrich_data_keys(self, sample_article):
        """Test that enrich_data adds the expected keys to the article content."""
        enriched_article = enrich_data(sample_article)
        assert "names" in enriched_article
        assert "sentiment_score" in enriched_article
        assert "key_words" in enriched_article


class TestEnrichAllData:
    """Tests for the enrich_all_data function."""

    @pytest.fixture
    def sample_articles(self):
        """Provides a list of sample article content dictionaries for testing."""
        return [
            {
                "title": "Biden and Johnson Discuss Climate Change",
                "summary": "Joe Biden met with Boris Johnson to discuss climate change.",
            },
            {
                "title": "Elon Musk Announces New Tesla Model",
                "summary": "Elon Musk announced a new Tesla model that will be released next year.",
            },
        ]

    def test_enrich_all_data_keys(self, sample_articles):
        """Test that enrich_all_data adds the expected keys to each article content."""
        enriched_articles = enrich_all_data(sample_articles)
        for article in enriched_articles:
            assert "names" in article
            assert "sentiment_score" in article
            assert "key_words" in article


class TestNormaliseName:
    """Tests for the normalise_name function."""

    @pytest.mark.parametrize(
        "name, expected_normalised",
        [
            ("Joe Biden", "joe_biden"),
            ("Boris Johnson", "boris_johnson"),
            ("Elon Musk", "elon_musk"),
        ],
    )
    def test_normalise_name(self, name, expected_normalised):
        """Test that normalise_name converts names to lowercase."""
        assert normalise_name(name) == expected_normalised

    @pytest.mark.parametrize(
        "name, expected_normalised",
        [("  Joe Biden  ", "joe_biden"), ("Boris   Johnson", "boris_johnson")],
    )
    def test_normalise_name_extra_spaces(self, name, expected_normalised):
        """Test that normalise_name handles extra spaces correctly."""
        assert normalise_name(name) == expected_normalised

    @pytest.mark.parametrize(
        "name, expected_normalised",
        [("Joe", "joe"), ("Biden", "biden"), ("Elon", "elon")],
    )
    def test_normalise_name_single_word(self, name, expected_normalised):
        """Test that normalise_name works correctly for single-word names."""
        assert normalise_name(name) == expected_normalised

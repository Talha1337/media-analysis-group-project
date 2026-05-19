"""Testing the extract script with pytest."""

import pytest
from extract import placeholder



@pytest.fixture
def valid_input():
    """Fixture for valid input data."""
    return "http://example.com/rss"


class TestExtractInvalid:
    """Test cases for invalid inputs to the extract script."""

    @pytest.mark.parametrize("input_data", [
        None,
        123,
        [],
        12.39,
        True
    ])
    def test_placeholder_invalid_type(self, input_data):
        """Test that extraction raises an error for invalid input types."""
        with pytest.raises(TypeError):
            placeholder(input_data)


    @pytest.mark.parametrize("input_data", [
        "nothing",
        "",
        "http:/invalid-url",
        "ftp://example.com/rss"
    ])
    def test_placeholder_invalid_value(self, input_data):
        """Test that extraction raises an error for invalid input values."""
        with pytest.raises(ValueError):
            placeholder(input_data)


class TestExtractValid:

    @pytest.mark.parametrize("input_data", [
        "http://example.com/rss",
        "https://example.com/feed",
        "http://example.com/rss.xml"
    ])
    def test_placeholder_valid(self, input_data):
        """Test that extraction works for valid input types."""
        placeholder(input_data)

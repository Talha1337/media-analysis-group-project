"""An extract script to interact with the RSS data."""

from datetime import datetime
import feedparser
from pprint import pprint


def extract_rss_feed(url: str) -> dict:
    """Extracts data from a single RSS feed and its entries."""
    if not isinstance(url, str):
        print(f"Invalid URL: {url}. URL must be a string.")
        raise TypeError("URL must be a string.")
    data = feedparser.parse(url)
    validate_feed_data(data)

    return {
        "feed_name": data.feed["title"],
        "feed_link": data.feed["link"],
        "feed_updated_at": data.feed["updated"],
        "entries": data.entries,
        "extracted_at": datetime.now().isoformat(),
    }


def validate_feed_data(data: feedparser.FeedParserDict) -> None:
    """Validates the structure of the feed data."""
    entry_req_keys = ["title", "summary_detail", "published", "summary", "id"]
    if not isinstance(data, feedparser.FeedParserDict):
        raise TypeError("Feed data must be a FeedParserDict.")
    if not hasattr(data, "feed") or not hasattr(data, "entries"):
        raise AttributeError(
            "Feed data must have 'feed' and 'entries' attributes.")
    if not isinstance(data.feed, dict):
        raise TypeError("Feed metadata must be a dictionary.")
    if not isinstance(data.entries, list):
        raise TypeError("Entries data must be a list.")
    # Validate that all entries have required keys
    for entry in data.entries:
        missing_keys = [key for key in entry_req_keys if key not in entry]
        if missing_keys:
            raise AttributeError(
                f"Entry missing required keys: {missing_keys}")


def extract_all_rss_feeds(urls: list[str]) -> list:
    """Extracts data from all RSS feeds."""
    all_data = []

    for url in urls:
        feed_data = extract_rss_feed(url)
        all_data.append(feed_data)

    return all_data


if __name__ == "__main__":
    urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ]
    extracted_data = extract_all_rss_feeds(urls)
    # Show structure of the first entry
    if extracted_data[0]['entries']:
        print("First entry keys:", extracted_data[0]['entries'][0].keys())
    # Show structure of the feed data
    pprint(extracted_data[0])
    print()
    print()
    # pprint(extracted_data[0].items())
    pprint(extracted_data[0]['entries'][0])

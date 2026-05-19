"""An extract script to interact with the RSS data."""

from datetime import datetime
import feedparser

FEED_URLS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.skynews.com/feeds/rss/home.xml"
]

def extract_rss_feed(url: str) -> dict:
    """Extracts data from a single RSS feed and its entries, returning it as a dictionary."""
    pass


def extract_all_rss_feeds() -> list:
    """Extracts data from all RSS feeds, returning a list of dictionaries."""
    pass
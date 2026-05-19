"""An extract script to interact with the RSS data."""

from datetime import datetime
import feedparser

FEED_URLS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.skynews.com/feeds/rss/home.xml"
]

def extract_rss_feed(url: str) -> dict:
    """Extracts data from a single RSS feed and its entries."""
    data = feedparser.parse(url)

    return {
        'feed_name': data.feed.get('title', 'No title'),
        'feed_link': data.feed.get('link', 'No link'),
        'feed_updated_at': data.feed.get('updated', 'No update time'),
        'entries': data.entries,
        'extracted_at': datetime.now().isoformat()
    }


def extract_all_rss_feeds() -> list:
    """Extracts data from all RSS feeds."""
    all_data = []
    
    for url in FEED_URLS:
        feed_data = extract_rss_feed(url)
        all_data.append(feed_data)
    
    return all_data

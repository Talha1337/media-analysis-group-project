"""An extract script to interact with the RSS data."""

import logging
from datetime import datetime
import feedparser
from pprint import pprint

log = logging.getLogger(__name__)


def extract_rss_feed(url: str) -> dict:
    """Extracts data from a single RSS feed and its entries."""
    log.info(f"Extracting RSS feed from URL: {url}")
    data = feedparser.parse(url)

    log.info(f"Extracted feed: {data.feed.get("link", "(Unknown link)")} with {len(data.entries)} entries.")

    return {
        "feed_name": data.feed.get("title", "No title"),
        "feed_link": data.feed.get("link", "No link"),
        "feed_updated_at": data.feed.get("updated", "No update time"),
        "entries": data.entries,
        "extracted_at": datetime.now().isoformat(),
    }


def extract_all_rss_feeds(urls: list[str]) -> list:
    """Extracts data from all RSS feeds."""
    all_data = []

    for url in urls:
        feed_data = extract_rss_feed(url)

        if feed_data:
            all_data.append(feed_data)
        else:
            log.warning(f"No data extracted from {url}. Skipping.")

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

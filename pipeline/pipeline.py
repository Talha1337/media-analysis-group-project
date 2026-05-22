"""A pipeline script to orchestrate the ETL process."""

from extract import extract_all_rss_feeds
from transform import enrich_all_data
from load import load_all_items


def run_pipeline(urls: list[str]) -> None:
    """Run the ETL pipeline: extracting from RSS, transforming by enriching, and loading into DynamoDB."""
    # Extracts a list of feeds
    extracted_feeds = extract_all_rss_feeds(urls)
    for feed in extracted_feeds:
        # Enriches each article entry in the feed
        enriched_entries = enrich_all_data(feed['entries'])
        load_all_items(enriched_entries)


if __name__ == "__main__":
    urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ]
    run_pipeline(urls)

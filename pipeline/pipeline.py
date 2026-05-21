"""A pipeline script to orchestrate the ETL process."""

from extract import extract_all_rss_feeds
from transform import enrich_all_data
from load import load_all_items


def run_pipeline(urls: list[str]) -> None:
    """Run the ETL pipeline: extracting from RSS, transforming by enriching, and loading into DynamoDB."""
    extracted_data = extract_all_rss_feeds(urls)
    enriched_data = enrich_all_data(extracted_data)
    load_all_items(enriched_data)


if __name__ == "__main__":
    urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ]
    run_pipeline(urls)

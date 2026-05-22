"""A pipeline script to orchestrate the ETL process."""

import logging

from extract import extract_all_rss_feeds
from transform import enrich_all_data
from load import load_all_items

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)

def run_pipeline(urls: list[str]) -> None:
    """Run the ETL pipeline: extracting from RSS, transforming by enriching, and loading into DynamoDB."""
    log.info("--- Starting the ETL pipeline ---")

    log.info("Step 1: EXTRACT")
    extracted_data = extract_all_rss_feeds(urls)

    log.info("Step 2: TRANSFORM")
    enriched_data = enrich_all_data(extracted_data)

    log.info("Step 3: LOAD")
    load_all_items(enriched_data)
    
    log.info("--- ETL pipeline completed ---")


if __name__ == "__main__":
    urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ]
    run_pipeline(urls)

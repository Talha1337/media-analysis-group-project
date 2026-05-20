"""A transform script to process and clean the extracted data, ready to load into DynamoDB."""

import spacy
import vader


def find_names(content: str) -> list[str]:
    """Extracts names of public figures from the given content using spaCy."""


def find_sentiment(content: str) -> float:
    """Analyzes the sentiment of the given content using VADER, giving a score between -1 (negative) and 1 (positive)."""


def get_key_words(content: str) -> list[str]:
    """Cleans the content by removing stop words and punctuation, returning a list of significant words."""


def enrich_data(article_content: dict) -> dict:
    """Enriches the article data by adding extracted names and sentiment score."""


def enrich_all_data(articles: list[dict]) -> list[dict]:
    """Enriches a list of article data dictionaries."""

"""A transform script to process and clean the extracted data, ready to load into DynamoDB."""

import spacy

# Crucial: You must import the keyword_spacy package to register the factory!
import keyword_spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def find_names(content: str) -> list[str]:
    """Extracts names of public figures from the given content using spaCy."""


def find_sentiment(content: str) -> float:
    """Analyzes the sentiment of the given content using VADER, giving a score between -1 (negative) and 1 (positive)."""
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(content)
    return sentiment_dict["compound"]


def get_key_words(content: str) -> list[str]:
    """Cleans the content by removing stop words and punctuation, returning a list of significant words."""
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe(
        "keyword_extractor",
        last=True,
        config={"top_n": 10, "min_ngram": 3, "max_ngram": 3, "strict": True},
    )
    doc = nlp(content)
    all_keywords = [keyword[0] for keyword in doc._.keywords]
    if not all_keywords:
        raise ValueError("No keywords found in the content.")
    return all_keywords


def enrich_data(article_content: dict) -> dict:
    """Enriches the article data by adding extracted names and sentiment score."""


def enrich_all_data(articles: list[dict]) -> list[dict]:
    """Enriches a list of article data dictionaries."""


if __name__ == "__main__":
    # Example usage
    positive_sample_article = {
        "title": "Tech CEO Elon Musk Announces Groundbreaking Innovation",
        "content": """Elon Musk has achieved remarkable success with his latest venture.
                    The brilliant entrepreneur's innovative approach has impressed industry
                    leaders and brought tremendous joy to millions of users worldwide.
                    His excellent leadership and outstanding vision have transformed the technology sector positively.""",
    }
    negative_sample_article = {
        "title": "Political Crisis: Boris Johnson Faces Serious Allegations",
        "content": """Boris Johnson is under intense scrutiny following damaging
                    revelations about his administration. Critics argue the former
                    prime minister's catastrophic decisions have harmed the economy.""",
    }
    positive_sentiment = find_sentiment(positive_sample_article["content"])
    negative_sentiment = find_sentiment(negative_sample_article["content"])
    print(f"Positive article sentiment: {positive_sentiment}")
    print(f"Negative article sentiment: {negative_sentiment}")
    print(
        f"Positive article keywords: {get_key_words(positive_sample_article['content'])}"
    )
    print(
        f"Negative article keywords: {get_key_words(negative_sample_article['content'])}"
    )

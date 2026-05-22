"""A transform script to process and clean the extracted data, ready to load into DynamoDB."""

import spacy
from pprint import pprint

# Crucial: You must import the keyword_spacy package to register the factory!
# python -m spacy download en_core_web_md
import keyword_spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ==============================================================================
# GLOBAL INITIALIZATION: Load the model ONCE when the script starts up
# ==============================================================================
print("Loading spaCy NLP model into memory...")
nlp = spacy.load("en_core_web_md")

# Add the keyword pipeline component globally so it doesn't get re-added over and over
nlp.add_pipe(
    "keyword_extractor",
    last=True,
    config={"top_n": 10, "min_ngram": 2, "max_ngram": 2, "strict": True},
)

# Initialize the VADER analyzer globally as well for a slight performance boost
sid_obj = SentimentIntensityAnalyzer()
print("Models loaded successfully!")
# ==============================================================================


def find_names(content: str) -> list[str]:
    """Extracts names of public figures from the given content using spaCy."""
    if not content:
        raise ValueError("Content cannot be empty.")
    if not isinstance(content, str):
        raise TypeError("Content must be a string.")
    # Load the English model matching keywords
    doc = nlp(content)

    # Extract PERSON entities
    names = [normalise_name(ent.text) for ent in doc.ents if ent.label_ == "PERSON"]
    if not names:
        # raise ValueError("No names found in the content.")
        print("no names found")
    return names


def find_sentiment(content: str) -> float:
    """Analyzes the sentiment of the given content using VADER, giving a score between -1 (negative) and 1 (positive)."""
    sentiment_dict = sid_obj.polarity_scores(content)
    return sentiment_dict["compound"]


def get_key_words(content: str) -> list[str]:
    """Extracts up to 10 keyword phrases from the content as two-word n-grams.

    Returns a list of extracted keyword strings. Raises ValueError if the
    extractor does not find any keywords in the content.
    """
    if not content:
        raise ValueError("Content cannot be empty.")
    if not isinstance(content, str):
        raise TypeError("Content must be a string.")
    # Note: The keyword_spacy package must be installed and the keyword_extractor
    # python -m spacy download en_core_web_md
    doc = nlp(content)
    all_keywords = [keyword[0] for keyword in doc._.keywords]
    if not all_keywords:
        print("No keywords found in the content.")
    return all_keywords


def enrich_data(article_content: dict) -> dict:
    """Enriches the article data by adding extracted names and sentiment score."""
    enriched_data = {}
    enriched_data["names"] = find_names(article_content["summary"])
    enriched_data["sentiment_score"] = find_sentiment(article_content["summary"])
    enriched_data["key_words"] = get_key_words(article_content["summary"])
    enriched_data["published_at"] = article_content.get(
        "published", "No published date"
    )
    enriched_data["article_link"] = article_content.get("id", "No article link")
    enriched_data["feed_link"] = article_content.get("summary_detail", {}).get(
        "base", "No feed link"
    )
    return enriched_data


def enrich_all_data(articles: list[dict]) -> list[dict]:
    """Enriches a list of article data dictionaries."""
    return [enrich_data(article) for article in articles]


def normalise_name(name: str) -> str:
    """Normalises a name by converting to lowercase and replacing spaces with underscores."""
    return "_".join(name.strip().lower().split())


if __name__ == "__main__":
    from extract import extract_all_rss_feeds

    urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.skynews.com/feeds/rss/home.xml",
    ]
    extracted_data = extract_all_rss_feeds(urls)
    enriched_data = enrich_data(extracted_data[0]["entries"][0])
    pprint(enriched_data)
    # Example usage
    positive_sample_article = {
        "title": "Tech CEO Elon Musk Announces Groundbreaking Innovation",
        "summary": """Elon Musk has achieved remarkable success with his latest venture.
                    The brilliant entrepreneur's innovative approach has impressed industry
                    leaders and brought tremendous Trump joy to millions of users worldwide.
                    His excellent Donald Trump leadership and outstanding vision have transformed the technology sector positively.""",
    }
    negative_sample_article = {
        "title": "Political Crisis: Boris Johnson Faces Serious Allegations",
        "summary": """Johnson, Trump and Biden is under intense scrutiny following damaging
                    revelations about his administration. Mandelson critics argue the former
                    prime minister's catastrophic Obama decisions have harmed the economy.""",
    }
    positive_sentiment = find_sentiment(positive_sample_article["summary"])
    negative_sentiment = find_sentiment(negative_sample_article["summary"])
    print(f"Positive article sentiment: {positive_sentiment}")
    print(f"Negative article sentiment: {negative_sentiment}")

    print(
        f"Names in positive article: {find_names(positive_sample_article['summary'])}"
    )
    print(
        f"Names in negative article: {find_names(negative_sample_article['summary'])}"
    )
    print(
        f"Positive article keywords: {get_key_words(positive_sample_article['summary'])}"
    )
    print(
        f"Negative article keywords: {get_key_words(negative_sample_article['summary'])}"
    )

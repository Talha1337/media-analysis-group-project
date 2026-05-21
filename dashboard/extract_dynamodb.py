"""Utilities for extracting public figure mention volumes from DynamoDB."""

import boto3
from boto3.dynamodb.conditions import Key
import streamlit as st
import pandas as pd


def initialise_dynamodb_resource():
    """Initializes and returns a DynamoDB resource using boto3."""
    return boto3.resource(
        "dynamodb", region_name="eu-west-2"
    )  # Adjust region as needed


def obtain_public_figure_volume(dynamodb_resource, figure_name: str) -> list:
    """Fetches the volume of mentions for a given public figure from DynamoDB."""
    # Initialize the DynamoDB resource
    table_name = "c23-epipelagic-dynamo-public-figures"
    table = dynamodb_resource.Table(table_name)

    # Querying with ONLY the partition key returns all matching sort key rows
    response = table.query(KeyConditionExpression=Key("PK").eq(figure_name))

    items = response.get("Items", [])
    return items


def display_public_figure_volume(items: list) -> None:
    """Show table of all mentions for a public figure."""
    if items:
        st.write("Mentions for the public figure:")
        st.table(items)
    else:
        st.write("No mentions found for the public figure.")


def display_public_figure_sentiment_chart(items: list) -> None:
    """Show a bar chart of sentiment scores sorted by decreasing order."""
    if items:
        df = pd.DataFrame(items)
        df_sorted = df.sort_values(by="sentiment_score", ascending=False).astype(
            {"sentiment_score": float}
        )
        st.bar_chart(df_sorted["sentiment_score"])
    else:
        st.write("No sentiment data available for the public figure.")


def main():
    st.title("Public Figure Mention Volume Dashboard")
    figure_name = st.text_input(
        "Enter the name of the public figure (e.g., 'joe_biden'):"
    )

    if figure_name:
        dynamodb_resource = initialise_dynamodb_resource()
        volume_data = obtain_public_figure_volume(dynamodb_resource, figure_name)
        display_public_figure_volume(volume_data)
        display_public_figure_sentiment_chart(volume_data)


if __name__ == "__main__":
    main()

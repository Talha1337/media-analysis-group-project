"""Utilities for extracting public figure mention volumes from DynamoDB."""


def obtain_public_figure_volume(dynamodb_client, figure_name: str) -> dict:
    """Fetches the volume of mentions for a given public figure from DynamoDB."""

import json
import boto3
from boto3.dynamodb.conditions import Key


def create_dynamodb_resource():
    """Initializes and returns a DynamoDB resource using boto3."""
    return boto3.resource(
        "dynamodb", region_name="eu-west-2"
    )  # Adjust region as needed


def get_public_figure_volume(dynamodb_resource, figure_name: str) -> list:
    """Fetches the volume of mentions for a given public figure from DynamoDB."""
    # Initialize the DynamoDB resource
    table_name = "c23-epipelagic-dynamo-public-figures"
    table = dynamodb_resource.Table(table_name)

    # Querying with ONLY the partition key returns all matching sort key rows
    response = table.query(KeyConditionExpression=Key("PK").eq(figure_name))

    items = response.get("Items", [])
    return items


def handle_event(event, context):
    # Log the incoming event to CloudWatch so we can inspect it
    print(f"Received event: {json.dumps(event)}")

    # Safely extract the name from the JSON payload
    # Note: API Gateway Proxy passes the payload as a string in event['body']
    # We will handle that below!
    user_name = "Stranger"
    print(event.get("pathParameters", {}))  # Log path parameters if any
    query_params = event.get("queryStringParameters", {})  # Log query parameters if any
    print(query_params)
    if not query_params or "name" not in query_params:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "No query parameters provided. Provide a name parameter in the query string."
                }
            ),
        }
    user_name = query_params.get("name")
    # The structural format API Gateway strictly requires:
    dynamodb_resource = create_dynamodb_resource()
    known_articles = get_public_figure_volume(dynamodb_resource, user_name)
    number_of_articles = len(known_articles)
    average_sentiment = (
        sum(float(article["sentiment_score"]) for article in known_articles)
        / number_of_articles
        if number_of_articles > 0
        else 0
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "message": f"Hello {user_name}, Lambda container worked!",
                "number_of_articles": number_of_articles,
                "average_sentiment": average_sentiment,
            }
        ),
    }


if __name__ == "__main__":
    test_event = {"name": "Alice"}
    try:
        response = handle_event(test_event, None)
        print(response)
    except Exception as e:
        print(f"Error occurred: {e}")

from datetime import datetime, timezone

import boto3

from app.config import AWS_REGION, DYNAMODB_ENDPOINT_URL, DYNAMODB_TABLE_NAME
from app.models.application import Application

# boto3 resource client, configured once at module load time.
_dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT_URL,
)
_table = _dynamodb.Table(DYNAMODB_TABLE_NAME)


def _serialize(app: Application) -> dict:
    """Convert an Application model into a DynamoDB-safe dict.
    DynamoDB doesn't understand Python date/datetime objects directly,
    so we convert them to ISO strings."""
    data = app.model_dump(mode="json")
    return data


def create_item(app: Application) -> Application:
    """Insert a new application item into DynamoDB."""
    _table.put_item(Item=_serialize(app))
    return app


def list_items(user_id: str) -> list[Application]:
    """Query all applications belonging to a given user."""
    response = _table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id)
    )
    items = response.get("Items", [])
    return [Application(**item) for item in items]


def get_item(user_id: str, application_id: str) -> Application | None:
    """Fetch a single application by its full primary key."""
    response = _table.get_item(
        Key={"user_id": user_id, "application_id": application_id}
    )
    item = response.get("Item")
    if item is None:
        return None
    return Application(**item)


def update_item(user_id: str, application_id: str, update_data: dict) -> Application | None:
    """Update specific fields on an existing item, then return the full updated item."""
    existing = get_item(user_id, application_id)
    if existing is None:
        return None

    updated = existing.model_copy(update=update_data)
    updated.updated_at = datetime.now(timezone.utc)
    _table.put_item(Item=_serialize(updated))
    return updated


def delete_item(user_id: str, application_id: str) -> bool:
    """Delete an item. Returns True if it existed and was deleted, False if not found."""
    existing = get_item(user_id, application_id)
    if existing is None:
        return False
    _table.delete_item(Key={"user_id": user_id, "application_id": application_id})
    return True
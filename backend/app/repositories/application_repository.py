import os
from datetime import datetime, timezone

import boto3

from app.config import AWS_REGION, DYNAMODB_ENDPOINT_URL, DYNAMODB_TABLE_NAME
from app.models.application import Application

# Uses AWS_PROFILE from environment (set via .env) if present, otherwise
# falls back to default AWS credentials. This lets the exact same code
# work against DynamoDB Local (Phase 3 Step 2) and real AWS (Phase 3 Step 3)
# with zero code changes — only environment configuration differs.
# Only use a named profile when explicitly running locally outside Lambda.
# AWS_EXECUTION_ENV is automatically set by Lambda's runtime and never present locally.
_is_running_in_lambda = os.getenv("AWS_EXECUTION_ENV") is not None
_profile = None if _is_running_in_lambda else os.getenv("AWS_PROFILE")

_session = boto3.Session(profile_name=_profile)
_dynamodb = _session.resource(
    "dynamodb",
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT_URL,
)
_table = _dynamodb.Table(DYNAMODB_TABLE_NAME)


def _serialize(app: Application) -> dict:
    """Convert an Application model into a DynamoDB-safe dict.
    DynamoDB doesn't understand Python date/datetime objects directly,
    so we convert them to ISO strings via Pydantic's JSON mode."""
    data = app.model_dump(mode="json")
    return data


def create_item(app: Application) -> Application:
    """Insert a new application item into DynamoDB."""
    _table.put_item(Item=_serialize(app))
    return app


def list_items(user_id: str) -> list[Application]:
    """Query all applications belonging to a given user.
    Uses the partition key (user_id) for a fast, cheap query —
    never a full-table scan."""
    response = _table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id)
    )
    items = response.get("Items", [])
    return [Application(**item) for item in items]


def get_item(user_id: str, application_id: str) -> Application | None:
    """Fetch a single application by its full primary key
    (partition key + sort key). Returns None if not found —
    callers decide how to translate that into an HTTP response."""
    response = _table.get_item(
        Key={"user_id": user_id, "application_id": application_id}
    )
    item = response.get("Item")
    if item is None:
        return None
    return Application(**item)


def update_item(user_id: str, application_id: str, update_data: dict) -> Application | None:
    """Update specific fields on an existing item (read-then-write),
    then return the full updated item. Returns None if not found."""
    existing = get_item(user_id, application_id)
    if existing is None:
        return None

    updated = existing.model_copy(update=update_data)
    updated.updated_at = datetime.now(timezone.utc)
    _table.put_item(Item=_serialize(updated))
    return updated


def delete_item(user_id: str, application_id: str) -> bool:
    """Delete an item. Returns True if it existed and was deleted,
    False if it didn't exist in the first place."""
    existing = get_item(user_id, application_id)
    if existing is None:
        return False
    _table.delete_item(Key={"user_id": user_id, "application_id": application_id})
    return True

def find_by_follow_up_date(follow_up_date: str) -> list[Application]:
    """Query ALL applications (across all users) with this exact follow_up_date,
    using the FollowUpDateIndex GSI. Used by the scheduled reminder job —
    not exposed via any API route, since it deliberately bypasses user isolation."""
    response = _table.query(
        IndexName="FollowUpDateIndex",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("follow_up_date").eq(follow_up_date),
    )
    items = response.get("Items", [])
    return [Application(**item) for item in items]
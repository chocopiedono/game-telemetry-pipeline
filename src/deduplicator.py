import os
import time
import hashlib
import boto3
import json
from typing import Dict, Any
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Configuration
DDB_TABLE = os.environ.get("DEDUP_TABLE", "game-events-dedup")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
TTL_SECONDS = 1800  # 30 minutes

# Initialize module-level DynamoDB client
try:
    ddb = boto3.client("dynamodb", region_name=AWS_REGION)
except Exception as e:
    logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
    raise


def generate_event_id(event: Dict[str, Any]) -> str:
    """Generate a unique hash for the event."""
    try:
        base_str = json.dumps(event, sort_keys=True)
        return hashlib.sha256(base_str.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate event ID: {str(e)}")
        raise


def is_duplicate(event_id: str) -> bool:
    """Check if an event ID already exists in DynamoDB."""
    try:
        response = ddb.get_item(TableName=DDB_TABLE, Key={"event_id": {"S": event_id}})
        return "Item" in response
    except Exception as e:
        logger.error(f"Failed to check for duplicate event {event_id}: {str(e)}")
        # In case of error, we assume it's not a duplicate to avoid data loss
        return False


def mark_event_id(event_id: str) -> None:
    """Mark an event ID as processed in DynamoDB."""
    try:
        ttl = int(time.time()) + TTL_SECONDS
        ddb.put_item(
            TableName=DDB_TABLE,
            Item={"event_id": {"S": event_id}, "ttl": {"N": str(ttl)}},
        )
    except Exception as e:
        logger.error(f"Failed to mark event {event_id}: {str(e)}")
        raise

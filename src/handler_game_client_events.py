import json
import logging
from typing import Dict, Any, List, Optional
import traceback
from datetime import datetime
from botocore.exceptions import ClientError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Use absolute imports for AWS Lambda compatibility
from src.deduplicator import is_duplicate, mark_event_id, generate_event_id
from src.normalizer import normalize_event
from src.cleaner import clean_event
from src.schemas import GameEvent, LambdaResponse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(ClientError),
)
def process_single_event(raw_body: str) -> Optional[Dict[str, Any]]:
    """
    Process a single event from the queue.
    Includes retry logic for DynamoDB operations.
    """
    try:
        event_data = json.loads(raw_body)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse event JSON: {str(e)}")
        return None

    try:
        # Validate and normalize the event
        normalized = normalize_event(event_data)
        cleaned = clean_event(normalized)

        # Validate against schema
        game_event = GameEvent(**cleaned)

        # Generate or get event ID
        if not game_event.event_id:
            game_event.event_id = generate_event_id(
                game_event.model_dump(exclude={"timestamp"})
            )

        # Check for duplicates
        if is_duplicate(game_event.event_id):
            logger.info(f"Skipping duplicate event: {game_event.event_id}")
            return None

        # Mark as processed
        mark_event_id(game_event.event_id)
        logger.info(f"Successfully processed event: {game_event.event_id}")
        return game_event.model_dump()

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}\n{traceback.format_exc()}")
        return None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing game client events.
    Handles event deduplication and normalization.
    """
    processed_events: List[Dict[str, Any]] = []
    failed_count = 0

    try:
        records = event.get("Records", [])
        logger.info(f"Received {len(records)} records to process")

        for record in records:
            raw_body = record.get("body")
            if not raw_body:
                logger.warning("Received record without body, skipping")
                continue

            processed_event = process_single_event(raw_body)
            if processed_event:
                processed_events.append(processed_event)
            else:
                failed_count += 1

        logger.info(
            f"Successfully processed {len(processed_events)} events, {failed_count} failed"
        )

        response = LambdaResponse(
            statusCode=200,
            body={
                "processed_count": len(processed_events),
                "failed_count": failed_count,
                "processed_events": processed_events,
            },
        )

        return response.model_dump()

    except Exception as e:
        error_msg = f"Fatal error in lambda handler: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)

        response = LambdaResponse(
            statusCode=500,
            body={
                "error": "Internal server error",
                "processed_count": len(processed_events),
                "failed_count": failed_count,
            },
        )

        return response.model_dump()

import pytest
import json
from unittest.mock import patch, MagicMock

# Import the functions to test
from src.handler_game_client_events import lambda_handler, process_single_event

# Test data
VALID_EVENT = {
    "Records": [
        {
            "body": json.dumps(
                {
                    "event_type": "player_action",
                    "player_id": "player123",
                    "game_version": "1.0.0",
                    "data": {"action": "jump"},
                }
            )
        }
    ]
}


@pytest.fixture(autouse=True)
def mock_ddb():
    """Mock the DynamoDB client at module level"""
    mock_client = MagicMock()
    # Set up default responses
    mock_client.get_item.return_value = {}
    mock_client.put_item.return_value = {}

    # Patch the module-level ddb client
    with patch("src.deduplicator.ddb", mock_client):
        yield mock_client


def test_process_single_event(mock_ddb):
    event_json = {
        "event_type": "player_action",
        "player_id": "player123",
        "game_version": "1.0.0",
        "data": {"action": "jump"},
    }

    # Process the event
    result = process_single_event(json.dumps(event_json))

    # Check the result
    assert result is not None
    assert result["event_type"] == "player_action"
    assert result["player_id"] == "player123"
    assert "event_id" in result

    # Simulate duplicate by making get_item return an item
    mock_ddb.get_item.return_value = {"Item": {"event_id": {"S": "test"}}}

    # Process the same event again - should be marked as duplicate
    result2 = process_single_event(json.dumps(event_json))
    assert result2 is None


def test_lambda_handler_success():
    response = lambda_handler(VALID_EVENT, None)

    assert response["statusCode"] == 200
    assert "body" in response
    body = (
        json.loads(response["body"])
        if isinstance(response["body"], str)
        else response["body"]
    )
    assert body["processed_count"] == 1
    assert body["failed_count"] == 0
    assert len(body["processed_events"]) == 1


def test_lambda_handler_invalid_json():
    invalid_event = {"Records": [{"body": "invalid json"}]}

    response = lambda_handler(invalid_event, None)
    assert response["statusCode"] == 200  # We don't fail the entire batch
    body = (
        json.loads(response["body"])
        if isinstance(response["body"], str)
        else response["body"]
    )
    assert body["processed_count"] == 0
    assert body["failed_count"] == 1


def test_lambda_handler_empty_records():
    empty_event = {"Records": []}
    response = lambda_handler(empty_event, None)

    assert response["statusCode"] == 200
    body = (
        json.loads(response["body"])
        if isinstance(response["body"], str)
        else response["body"]
    )
    assert body["processed_count"] == 0
    assert body["failed_count"] == 0

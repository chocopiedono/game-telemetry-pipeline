import pytest
from unittest.mock import patch, MagicMock
from src.deduplicator import is_duplicate, mark_event_id, generate_event_id


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


def test_is_duplicate(mock_ddb):
    event_id = "test123"

    # First check should return False (no item found)
    mock_ddb.get_item.return_value = {}
    assert not is_duplicate(event_id)

    # Verify get_item was called correctly
    mock_ddb.get_item.assert_called_with(
        TableName="game-events-dedup", Key={"event_id": {"S": event_id}}
    )

    # Mark the event
    mark_event_id(event_id)

    # Simulate item exists in DynamoDB
    mock_ddb.get_item.return_value = {"Item": {"event_id": {"S": event_id}}}

    # Second check should return True
    assert is_duplicate(event_id)


def test_generate_event_id():
    event = {
        "event_type": "test_event",
        "player_id": "player123",
        "data": {"action": "jump"},
    }

    # Same event should generate same ID
    id1 = generate_event_id(event)
    id2 = generate_event_id(event.copy())
    assert id1 == id2

    # Different event should generate different ID
    event["player_id"] = "player456"
    id3 = generate_event_id(event)
    assert id1 != id3


def test_mark_event_id(mock_ddb):
    event_id = "test456"
    mark_event_id(event_id)

    # Verify put_item was called with correct parameters
    mock_ddb.put_item.assert_called_once()
    call_args = mock_ddb.put_item.call_args[1]
    assert call_args["TableName"] == "game-events-dedup"
    assert call_args["Item"]["event_id"]["S"] == event_id
    assert "ttl" in call_args["Item"]

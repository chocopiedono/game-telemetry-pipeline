import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from src.schemas import GameEvent, LambdaResponse
from src.normalizer import normalize_event


def test_valid_game_event():
    event_data = {
        "event_type": "player_action",
        "player_id": "player123",
        "game_version": "1.0.0",
        "data": {"action": "jump"},
    }
    event = GameEvent(**event_data)
    assert event.event_type == "player_action"
    assert event.player_id == "player123"
    assert isinstance(event.timestamp, datetime)


def test_invalid_game_event():
    with pytest.raises(ValidationError):
        GameEvent(
            event_type="",  # empty event type
            player_id="player123",
            game_version="1.0.0",
        )

    with pytest.raises(ValidationError):
        GameEvent(
            event_type="player_action",
            player_id="",  # empty player_id
            game_version="1.0.0",
        )


def test_game_event_normalization():
    event_data = {
        "EVENT_TYPE": "  PLAYER_ACTION  ",
        "player_id": "  player123  ",
        "game_version": "1.0.0",
        "data": {"action": "jump"},
    }
    # Normalize the event data first
    normalized_data = normalize_event(event_data)
    event = GameEvent(**normalized_data)
    assert event.event_type == "player_action"
    assert event.player_id == "player123"


def test_lambda_response():
    response = LambdaResponse(
        statusCode=200, body={"processed_count": 1, "failed_count": 0}
    )
    assert response.statusCode == 200
    assert response.body["processed_count"] == 1

    # Test with datetime in body
    now = datetime.now(timezone.utc)
    response = LambdaResponse(statusCode=200, body={"timestamp": now})
    assert isinstance(response.model_dump()["body"]["timestamp"], str)

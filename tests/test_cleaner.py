from src.cleaner import clean_event, UNWANTED_FIELDS


def test_clean_event_removes_unwanted_fields():
    event = {
        "event_type": "click",
        "player_id": "player123",
        "debug_info": {"debug": "data"},
        "unused_field": "test",
    }
    cleaned = clean_event(event)

    # Check unwanted fields are removed
    assert "debug_info" not in cleaned
    assert "unused_field" not in cleaned

    # Check wanted fields remain
    assert cleaned["event_type"] == "click"
    assert cleaned["player_id"] == "player123"


def test_clean_event_keeps_normal_fields():
    event = {
        "event_type": "click",
        "player_id": "player123",
        "game_version": "1.0.0",
        "data": {"action": "jump"},
    }
    cleaned = clean_event(event)
    assert cleaned == event  # All fields should remain


def test_clean_event_empty_input():
    event = {}
    cleaned = clean_event(event)
    assert cleaned == {}

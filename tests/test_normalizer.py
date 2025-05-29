from src.normalizer import normalize_event, normalize_value


def test_normalize_event():
    event = {
        "EVENT_TYPE": "  ClickEvent  ",
        "PLAYER_ID": "  player123  ",
        "data": {"ACTION": "JUMP"},
    }
    normalized = normalize_event(event)

    assert normalized["event_type"] == "clickevent"
    assert normalized["player_id"] == "player123"
    assert (
        normalized["data"]["action"] == "jump"
    )  # nested values should also be lowercase


def test_normalize_value():
    # Test string normalization
    assert normalize_value("  TEST  ") == "test"

    # Test dict normalization
    nested_dict = {"KEY": "  Value  "}
    assert normalize_value(nested_dict) == {"key": "value"}

    # Test list normalization
    assert normalize_value(["  A  ", "  B  "]) == ["a", "b"]

    # Test other types pass through unchanged
    assert normalize_value(123) == 123
    assert normalize_value(True) is True

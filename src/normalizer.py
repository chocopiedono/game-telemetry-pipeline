from typing import Dict, Any, Union


def normalize_value(value: Any) -> Any:
    """
    Normalize a single value.
    - Strings are stripped and lowercased
    - Dictionaries are recursively normalized
    - Lists have each element normalized
    - Other types are returned as-is
    """
    if isinstance(value, str):
        return value.strip().lower()
    elif isinstance(value, dict):
        return normalize_event(value)
    elif isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value


def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize event data by converting keys to lowercase and cleaning string values.
    Handles nested dictionaries and lists.
    """
    normalized = {}
    for k, v in event.items():
        if k is None:
            continue
        key = str(k).lower().strip()
        normalized[key] = normalize_value(v)
    return normalized

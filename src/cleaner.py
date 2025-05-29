UNWANTED_FIELDS = {"debug_info", "unused_field"}


def clean_event(event: dict) -> dict:
    return {k: v for k, v in event.items() if k not in UNWANTED_FIELDS}

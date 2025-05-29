from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone


class GameEvent(BaseModel):
    """Base model for game events"""

    event_id: Optional[str] = None
    event_type: str = Field(..., description="Type of the game event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    player_id: str = Field(..., description="ID of the player who generated the event")
    game_version: str = Field(..., description="Version of the game client")
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event data"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if "timestamp" in data and isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data

    @field_validator("event_type")
    def validate_event_type(cls, v):
        if not v.strip():
            raise ValueError("event_type cannot be empty")
        return v.lower().strip()

    @field_validator("player_id")
    def validate_player_id(cls, v):
        if not v.strip():
            raise ValueError("player_id cannot be empty")
        return v.strip()


class LambdaResponse(BaseModel):
    """Response model for Lambda function"""

    statusCode: int = Field(..., description="HTTP status code")
    body: Dict[str, Any] = Field(..., description="Response body")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Convert any datetime objects in the body to ISO format
        if isinstance(data.get("body"), dict):
            for key, value in data["body"].items():
                if isinstance(value, datetime):
                    data["body"][key] = value.isoformat()
                elif isinstance(value, list):
                    data["body"][key] = [
                        item.isoformat() if isinstance(item, datetime) else item
                        for item in value
                    ]
        return data

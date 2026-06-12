from pydantic import BaseModel


# --- Response schemas ---


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "email": "john@example.com",
                "created_at": "2026-01-15T10:30:00",
            }
        }
    }


class UserPublicResponse(BaseModel):
    id: str
    username: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
            }
        }
    }

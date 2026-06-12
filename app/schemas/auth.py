from pydantic import BaseModel, Field
from .types import UsernameStr, EmailStr, PasswordStr
from .users import UserResponse


# --- Request schemas ---


class RegisterBody(BaseModel):
    username: UsernameStr = Field(description="Unique username (max 80 characters)")
    email: EmailStr = Field(description="Valid email address (max 120 characters)")
    password: PasswordStr = Field(description="Password between 8 and 128 characters")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123",
            }
        }
    }


class LoginBody(BaseModel):
    email: EmailStr = Field(description="Registered email address")
    password: str = Field(description="Account password")

    model_config = {
        "json_schema_extra": {
            "example": {"email": "john@example.com", "password": "securepassword123"}
        }
    }


# --- Response schemas ---


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "johndoe",
                    "email": "john@example.com",
                    "created_at": "2026-01-15T10:30:00",
                },
            }
        }
    }


class AccessTokenResponse(BaseModel):
    access_token: str

    model_config = {
        "json_schema_extra": {
            "example": {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    }

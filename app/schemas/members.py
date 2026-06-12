from pydantic import BaseModel, Field, RootModel
from .types import UUIDStr, ProjectRole


# --- Request schemas ---


class AddMemberBody(BaseModel):
    user_id: UUIDStr = Field(description="UUID of the user to add as a member")

    model_config = {
        "json_schema_extra": {
            "example": {"user_id": "550e8400-e29b-41d4-a716-446655440000"}
        }
    }


class UpdateRoleBody(BaseModel):
    role: ProjectRole = Field(
        description='New role for the member: "member" or "admin"'
    )

    model_config = {"json_schema_extra": {"example": {"role": "admin"}}}


# --- Response schemas ---


class MemberResponse(BaseModel):
    user_id: str
    username: str | None
    role: ProjectRole
    joined_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "johndoe",
                "role": "member",
                "joined_at": "2026-01-15T10:30:00",
            }
        }
    }


class MemberListResponse(RootModel[list[MemberResponse]]):
    pass

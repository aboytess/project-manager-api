from pydantic import BaseModel, Field, RootModel
from .types import ProjectNameStr, ProjectDescriptionStr


# --- Request schemas ---


class CreateProjectBody(BaseModel):
    name: ProjectNameStr = Field(description="Project name (max 120 characters)")
    description: ProjectDescriptionStr | None = Field(
        default=None, description="Optional project description (max 500 characters)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "My Project",
                "description": "A project for tracking feature development",
            }
        }
    }


class UpdateProjectBody(BaseModel):
    name: ProjectNameStr = Field(
        default=None, description="New project name (max 120 characters)"
    )  # type: ignore[assignment]
    description: ProjectDescriptionStr | None = Field(
        default=None, description="New project description, or null to clear it"
    )

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Renamed Project", "description": "Updated description"}
        }
    }


# --- Response schemas ---


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    created_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "My Project",
                "description": "A sample project description",
                "owner_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-01-15T10:30:00",
            }
        }
    }


class ProjectListResponse(RootModel[list[ProjectResponse]]):
    pass

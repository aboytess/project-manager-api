from pydantic import BaseModel, Field, RootModel
from .types import (
    TaskTitleStr,
    TaskDescriptionStr,
    TaskStatus,
    TaskPriority,
    UUIDStr,
    ISODateStr,
)


# --- Request schemas ---


class CreateTaskBody(BaseModel):
    title: TaskTitleStr = Field(description="Task title (max 200 characters)")
    description: TaskDescriptionStr | None = Field(
        default=None, description="Optional task description (max 1000 characters)"
    )
    status: TaskStatus = Field(
        default="todo", description='Task status: "todo", "in_progress", or "done"'
    )
    priority: TaskPriority = Field(
        default="medium", description='Task priority: "low", "medium", or "high"'
    )
    assignee_id: UUIDStr | None = Field(
        default=None, description="UUID of a project member to assign this task to"
    )
    due_date: ISODateStr | None = Field(
        default=None,
        description="Due date in ISO 8601 format (e.g. 2026-12-31 or 2026-12-31T23:59:59)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Fix login bug",
                "description": "Users cannot log in with Google OAuth",
                "status": "todo",
                "priority": "high",
                "assignee_id": "550e8400-e29b-41d4-a716-446655440000",
                "due_date": "2026-12-31",
            }
        }
    }


class UpdateTaskBody(BaseModel):
    title: TaskTitleStr = Field(
        default=None, description="New task title (max 200 characters)"
    )  # type: ignore[assignment]
    description: TaskDescriptionStr | None = Field(
        default=None, description="New task description, or null to clear it"
    )
    status: TaskStatus = Field(
        default=None, description='New task status: "todo", "in_progress", or "done"'
    )  # type: ignore[assignment]
    priority: TaskPriority = Field(
        default=None, description='New task priority: "low", "medium", or "high"'
    )  # type: ignore[assignment]
    assignee_id: UUIDStr | None = Field(
        default=None, description="New assignee UUID, or null to unassign"
    )
    due_date: ISODateStr | None = Field(
        default=None, description="New due date in ISO 8601 format, or null to clear it"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in_progress",
                "priority": "medium",
                "due_date": "2026-11-15",
            }
        }
    }


# --- Response schemas ---


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: str
    assignee_id: str | None
    assignee_username: str | None
    due_date: str | None
    created_at: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "title": "Fix login bug",
                "description": "Users cannot log in with Google OAuth",
                "status": "in_progress",
                "priority": "high",
                "project_id": "550e8400-e29b-41d4-a716-446655440001",
                "assignee_id": "550e8400-e29b-41d4-a716-446655440000",
                "assignee_username": "johndoe",
                "due_date": "2026-12-31T00:00:00",
                "created_at": "2026-01-15T10:30:00",
            }
        }
    }


class TaskListResponse(RootModel[list[TaskResponse]]):
    pass

from pydantic import BaseModel, Field
from .types import TaskTitleStr, TaskDescriptionStr, TaskStatus, TaskPriority, UUIDStr, ISODateStr


class CreateTaskBody(BaseModel):
    title: TaskTitleStr
    description: TaskDescriptionStr | None = Field(
        default=None, description='Optional task description'
    )
    status: TaskStatus = Field(default='todo', description='Task status')
    priority: TaskPriority = Field(default='medium', description='Task priority')
    assignee_id: UUIDStr | None = Field(default=None, description='Optional assignee user ID')
    due_date: ISODateStr | None = Field(
        default=None, description='Optional due date in ISO 8601 format (e.g. 2026-12-31)'
    )


class UpdateTaskBody(BaseModel):
    title: TaskTitleStr = Field(default=None, description='New task title')  # type: ignore[assignment]
    description: TaskDescriptionStr | None = Field(
        default=None, description='New task description, or null to clear it'
    )
    status: TaskStatus = Field(default=None, description='New task status')  # type: ignore[assignment]
    priority: TaskPriority = Field(default=None, description='New task priority')  # type: ignore[assignment]
    assignee_id: UUIDStr | None = Field(
        default=None, description='New assignee user ID, or null to unassign'
    )
    due_date: ISODateStr | None = Field(
        default=None, description='New due date in ISO 8601 format, or null to clear it'
    )

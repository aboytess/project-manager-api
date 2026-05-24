from pydantic import BaseModel


class CreateTaskBody(BaseModel):
    title: str
    description: str | None = None
    status: str = 'todo'
    priority: str = 'medium'
    assignee_id: str | None = None
    due_date: str | None = None


class UpdateTaskBody(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee_id: str | None = None
    due_date: str | None = None

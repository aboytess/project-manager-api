from pydantic import BaseModel


class ProjectPath(BaseModel):
    project_id: str


class TaskPath(BaseModel):
    project_id: str
    task_id: str


class MemberPath(BaseModel):
    project_id: str
    user_id: str


class UserPath(BaseModel):
    user_id: str

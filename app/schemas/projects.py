from pydantic import BaseModel


class CreateProjectBody(BaseModel):
    name: str
    description: str | None = None


class UpdateProjectBody(BaseModel):
    name: str | None = None
    description: str | None = None

from pydantic import BaseModel, Field
from .types import ProjectNameStr, ProjectDescriptionStr


class CreateProjectBody(BaseModel):
    name: ProjectNameStr
    description: ProjectDescriptionStr | None = Field(
        default=None, description='Optional project description'
    )


class UpdateProjectBody(BaseModel):
    name: ProjectNameStr = Field(default=None, description='New project name')  # type: ignore[assignment]
    description: ProjectDescriptionStr | None = Field(
        default=None, description='New project description, or null to clear it'
    )

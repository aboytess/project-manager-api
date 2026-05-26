from pydantic import BaseModel
from .types import UUIDStr, ProjectRole


class AddMemberBody(BaseModel):
    user_id: UUIDStr


class UpdateRoleBody(BaseModel):
    role: ProjectRole

from pydantic import BaseModel


class AddMemberBody(BaseModel):
    user_id: str


class UpdateRoleBody(BaseModel):
    role: str

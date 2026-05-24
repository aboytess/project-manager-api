from pydantic import BaseModel


class RegisterBody(BaseModel):
    username: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str

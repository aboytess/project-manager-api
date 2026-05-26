from pydantic import BaseModel
from .types import UsernameStr, EmailStr, PasswordStr


class RegisterBody(BaseModel):
    username: UsernameStr
    email: EmailStr
    password: PasswordStr


class LoginBody(BaseModel):
    email: EmailStr
    password: str

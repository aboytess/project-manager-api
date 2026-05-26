from typing import Annotated, Literal
from pydantic import StringConstraints

ProjectNameStr = Annotated[str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True)]
ProjectDescriptionStr = Annotated[str, StringConstraints(min_length=1, max_length=500, strip_whitespace=True)]
TaskTitleStr = Annotated[str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)]
TaskDescriptionStr = Annotated[str, StringConstraints(min_length=1, max_length=1000, strip_whitespace=True)]
UsernameStr = Annotated[str, StringConstraints(min_length=1, max_length=80, strip_whitespace=True)]
EmailStr = Annotated[str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True, to_lower=True)]
PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=128)]
UUIDStr = Annotated[str, StringConstraints(min_length=1, max_length=36, strip_whitespace=True)]
ISODateStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

TaskStatus = Literal['todo', 'in_progress', 'done']
TaskPriority = Literal['low', 'medium', 'high']
ProjectRole = Literal['member', 'admin']

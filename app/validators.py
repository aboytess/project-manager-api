from flask import request
from .errors import ValidationError, NotFoundError, ForbiddenError
from .models.project import Project
from .models.task import Task
from .models.project_member import ProjectMember


def parse_json() -> dict:
    data = request.get_json()
    if data is None:
        raise ValidationError('Request body must be valid JSON')
    return data


def validate_string(value: object, field_name: str, max_length: int) -> str:
    if not isinstance(value, str):
        raise ValidationError(f'{field_name} must be a string')
    value = value.strip()
    if not value:
        raise ValidationError(f'{field_name} cannot be empty')
    if len(value) > max_length:
        raise ValidationError(f'{field_name} cannot exceed {max_length} characters')
    return value


def validate_optional_string(value: object, field_name: str, max_length: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f'{field_name} must be a string')
    value = value.strip()
    if not value:
        return None
    if len(value) > max_length:
        raise ValidationError(f'{field_name} cannot exceed {max_length} characters')
    return value


def validate_enum(value: object, field_name: str, valid_values: set) -> str:
    if value not in valid_values:
        raise ValidationError(f'{field_name} must be one of: {", ".join(sorted(valid_values))}')
    return value


def validate_assignee(assignee_id: object, project_id: str) -> str:
    if not isinstance(assignee_id, str) or not assignee_id.strip():
        raise ValidationError('assignee_id must be a valid user id')
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=assignee_id).first()
    if not member:
        raise ValidationError('assignee must be a member of the project')
    return assignee_id


def get_accessible_project(project_id: str, user_id: str) -> Project:
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project {project_id} not found')
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        raise ForbiddenError('You do not have permission to access this project')
    return project


def get_owned_project(project_id: str, user_id: str) -> Project:
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project {project_id} not found')
    if project.owner_id != user_id:
        raise ForbiddenError('Only the project owner can perform this action')
    return project


def get_task_in_project(task_id: str, project_id: str) -> Task:
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        raise NotFoundError(f'Task {task_id} not found in project {project_id}')
    return task

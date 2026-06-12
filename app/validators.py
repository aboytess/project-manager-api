from datetime import datetime
from .errors import ValidationError, NotFoundError
from .models.project import Project
from .models.task import Task
from .models.project_member import ProjectMember


def validate_date(value: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(
            f"{field_name} must be a valid ISO 8601 date (e.g. 2026-12-31)"
        )


def validate_assignee(assignee_id: str, project_id: str) -> str:
    member = ProjectMember.query.filter_by(
        project_id=project_id, user_id=assignee_id
    ).first()
    if not member:
        raise ValidationError("assignee must be a member of the project")
    return assignee_id


def get_accessible_project(project_id: str, user_id: str) -> Project:
    project = (
        Project.query.join(ProjectMember, Project.id == ProjectMember.project_id)
        .filter(Project.id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if not project:
        raise NotFoundError(f"Project {project_id} not found")
    return project


def get_managed_project(project_id: str, user_id: str) -> Project:
    project = (
        Project.query.join(ProjectMember, Project.id == ProjectMember.project_id)
        .filter(
            Project.id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_(["owner", "admin"]),
        )
        .first()
    )
    if not project:
        raise NotFoundError(f"Project {project_id} not found")
    return project


def get_owned_project(project_id: str, user_id: str) -> Project:
    project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
    if not project:
        raise NotFoundError(f"Project {project_id} not found")
    return project


def get_task_in_project(task_id: str, project_id: str) -> Task:
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        raise NotFoundError(f"Task {task_id} not found in project {project_id}")
    return task

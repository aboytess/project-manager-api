from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.task import Task
from ..validators import validate_date, validate_assignee, get_accessible_project, get_task_in_project
from ..schemas.paths import ProjectPath, TaskPath
from ..schemas.tasks import CreateTaskBody, UpdateTaskBody, TaskResponse, TaskListResponse
from ..schemas.shared import MessageResponse, BadRequestResponse, UnauthorizedResponse, NotFoundResponse, UnprocessableResponse

_tag = Tag(name='tasks', description='Task management within projects')

tasks_bp = APIBlueprint(
    'tasks', __name__,
    url_prefix='/api/projects',
    abp_tags=[_tag],
    abp_security=[{'bearerAuth': []}]
)


def current_user_id() -> str:
    return get_jwt_identity()


@tasks_bp.get(
    '/<project_id>/tasks',
    summary='List all tasks in a project',
    description='Returns all tasks for a project. Requires membership in the project (any role).',
    responses={
        '200': TaskListResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse
    }
)
@jwt_required()
def get_tasks(path: ProjectPath):
    get_accessible_project(path.project_id, current_user_id())
    tasks = Task.query.options(joinedload(Task.assignee)).filter_by(project_id=path.project_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.get(
    '/<project_id>/tasks/<task_id>',
    summary='Get a task by ID',
    description='Returns a task by ID. Requires membership in the project (any role).',
    responses={
        '200': TaskResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse
    }
)
@jwt_required()
def get_task(path: TaskPath):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    return jsonify(task.to_dict()), 200


@tasks_bp.post(
    '/<project_id>/tasks',
    summary='Create a new task',
    description=(
        'Creates a new task in a project. Requires membership in the project (any role). '
        '`assignee_id` must be the UUID of an existing project member. '
        '`due_date` must be a valid ISO 8601 string (e.g. `2026-12-31`).'
    ),
    responses={
        '201': TaskResponse,
        '400': BadRequestResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse,
        '422': UnprocessableResponse
    }
)
@jwt_required()
def create_task(path: ProjectPath, body: CreateTaskBody):
    get_accessible_project(path.project_id, current_user_id())
    task = Task(
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        project_id=path.project_id,
        assignee_id=validate_assignee(body.assignee_id, path.project_id) if body.assignee_id else None,
        due_date=validate_date(body.due_date, 'due_date') if body.due_date else None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.patch(
    '/<project_id>/tasks/<task_id>',
    summary='Update a task',
    description=(
        'Partially updates a task. Only provided fields are updated. '
        'Requires membership in the project (any role). '
        '`assignee_id` must be the UUID of an existing project member, or `null` to unassign.'
    ),
    responses={
        '200': TaskResponse,
        '400': BadRequestResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse,
        '422': UnprocessableResponse
    }
)
@jwt_required()
def update_task(path: TaskPath, body: UpdateTaskBody):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    data = body.model_dump(exclude_unset=True)
    if 'title' in data:
        task.title = body.title
    if 'description' in data:
        task.description = body.description
    if 'status' in data:
        task.status = body.status
    if 'priority' in data:
        task.priority = body.priority
    if 'assignee_id' in data:
        task.assignee_id = validate_assignee(body.assignee_id, path.project_id) if body.assignee_id else None
    if 'due_date' in data:
        task.due_date = validate_date(body.due_date, 'due_date') if body.due_date else None
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.delete(
    '/<project_id>/tasks/<task_id>',
    summary='Delete a task',
    description='Permanently deletes a task. Requires membership in the project (any role).',
    responses={
        '200': MessageResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse
    }
)
@jwt_required()
def delete_task(path: TaskPath):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task.title} deleted successfully'}), 200

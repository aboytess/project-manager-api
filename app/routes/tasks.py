from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.task import Task
from ..validators import (
    validate_string, validate_optional_string,
    validate_enum, validate_date, validate_assignee, get_accessible_project, get_task_in_project
)
from ..schemas.paths import ProjectPath, TaskPath
from ..schemas.tasks import CreateTaskBody, UpdateTaskBody

_tag = Tag(name='tasks', description='Task management within projects')

tasks_bp = APIBlueprint(
    'tasks', __name__,
    url_prefix='/api/projects',
    abp_tags=[_tag],
    abp_security=[{'bearerAuth': []}]
)

VALID_STATUSES = {'todo', 'in_progress', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high'}


def current_user_id() -> str:
    return get_jwt_identity()


@tasks_bp.get('/<project_id>/tasks', summary='List all tasks in a project')
@jwt_required()
def get_tasks(path: ProjectPath):
    get_accessible_project(path.project_id, current_user_id())
    tasks = Task.query.options(joinedload(Task.assignee)).filter_by(project_id=path.project_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.get('/<project_id>/tasks/<task_id>', summary='Get a task by ID')
@jwt_required()
def get_task(path: TaskPath):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    return jsonify(task.to_dict()), 200


@tasks_bp.post('/<project_id>/tasks', summary='Create a new task')
@jwt_required()
def create_task(path: ProjectPath, body: CreateTaskBody):
    get_accessible_project(path.project_id, current_user_id())
    assignee_id = validate_assignee(body.assignee_id, path.project_id) if body.assignee_id else None
    task = Task(
        title=validate_string(body.title, 'title', max_length=200),
        description=validate_optional_string(body.description, 'description', max_length=1000),
        status=validate_enum(body.status, 'status', VALID_STATUSES),
        priority=validate_enum(body.priority, 'priority', VALID_PRIORITIES),
        project_id=path.project_id,
        assignee_id=assignee_id,
        due_date=validate_date(body.due_date, 'due_date') if body.due_date else None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.put('/<project_id>/tasks/<task_id>', summary='Update a task')
@jwt_required()
def update_task(path: TaskPath, body: UpdateTaskBody):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    data = body.model_dump(exclude_unset=True)
    if 'title' in data:
        task.title = validate_string(body.title, 'title', max_length=200)
    if 'description' in data:
        task.description = validate_optional_string(body.description, 'description', max_length=1000)
    if 'status' in data:
        task.status = validate_enum(body.status, 'status', VALID_STATUSES)
    if 'priority' in data:
        task.priority = validate_enum(body.priority, 'priority', VALID_PRIORITIES)
    if 'assignee_id' in data:
        task.assignee_id = validate_assignee(body.assignee_id, path.project_id) if body.assignee_id else None
    if 'due_date' in data:
        task.due_date = validate_date(body.due_date, 'due_date') if body.due_date else None
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.delete('/<project_id>/tasks/<task_id>', summary='Delete a task')
@jwt_required()
def delete_task(path: TaskPath):
    get_accessible_project(path.project_id, current_user_id())
    task = get_task_in_project(path.task_id, path.project_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task.title} deleted successfully'}), 200

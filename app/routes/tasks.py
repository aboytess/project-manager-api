from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.task import Task
from ..validators import (
    parse_json, validate_string, validate_optional_string,
    validate_enum, validate_date, validate_assignee, get_accessible_project, get_task_in_project
)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/projects')

VALID_STATUSES = {'todo', 'in_progress', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high'}


def current_user_id() -> str:
    return get_jwt_identity()


@tasks_bp.route('/<project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id: str):
    get_accessible_project(project_id, current_user_id())
    tasks = Task.query.options(joinedload(Task.assignee)).filter_by(project_id=project_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.route('/<project_id>/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(project_id: str, task_id: str):
    get_accessible_project(project_id, current_user_id())
    task = get_task_in_project(task_id, project_id)
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id: str):
    get_accessible_project(project_id, current_user_id())
    data = parse_json()
    assignee_id = validate_assignee(data['assignee_id'], project_id) if data.get('assignee_id') else None
    task = Task(
        title=validate_string(data.get('title'), 'title', max_length=200),
        description=validate_optional_string(data.get('description'), 'description', max_length=1000),
        status=validate_enum(data.get('status', 'todo'), 'status', VALID_STATUSES),
        priority=validate_enum(data.get('priority', 'medium'), 'priority', VALID_PRIORITIES),
        project_id=project_id,
        assignee_id=assignee_id,
        due_date=validate_date(data['due_date'], 'due_date') if data.get('due_date') else None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<project_id>/tasks/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(project_id: str, task_id: str):
    get_accessible_project(project_id, current_user_id())
    task = get_task_in_project(task_id, project_id)
    data = parse_json()
    if 'title' in data:
        task.title = validate_string(data['title'], 'title', max_length=200)
    if 'description' in data:
        task.description = validate_optional_string(data['description'], 'description', max_length=1000)
    if 'status' in data:
        task.status = validate_enum(data['status'], 'status', VALID_STATUSES)
    if 'priority' in data:
        task.priority = validate_enum(data['priority'], 'priority', VALID_PRIORITIES)
    if 'assignee_id' in data:
        task.assignee_id = validate_assignee(data['assignee_id'], project_id) if data['assignee_id'] else None
    if 'due_date' in data:
        task.due_date = validate_date(data['due_date'], 'due_date') if data['due_date'] else None
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<project_id>/tasks/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(project_id: str, task_id: str):
    get_accessible_project(project_id, current_user_id())
    task = get_task_in_project(task_id, project_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task.title} deleted successfully'}), 200

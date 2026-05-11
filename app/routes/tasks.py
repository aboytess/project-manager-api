from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.task import Task
from ..models.project import Project
from ..errors import NotFoundError, ValidationError

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/projects')

VALID_STATUSES = {'todo', 'in_progress', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high'}


@tasks_bp.route('/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')
    return jsonify([t.to_dict() for t in project.tasks]), 200


@tasks_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        raise NotFoundError(f'Task {task_id} not found in project {project_id}')
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')

    data = request.get_json()
    if not data or not data.get('title'):
        raise ValidationError('title is required')

    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')

    if status not in VALID_STATUSES:
        raise ValidationError(f'status must be one of: {", ".join(VALID_STATUSES)}')
    if priority not in VALID_PRIORITIES:
        raise ValidationError(f'priority must be one of: {", ".join(VALID_PRIORITIES)}')

    task = Task(
        title=data['title'],
        description=data.get('description'),
        status=status,
        priority=priority,
        project_id=project_id,
        assignee_id=data.get('assignee_id')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        raise NotFoundError(f'Task {task_id} not found in project {project_id}')

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ValidationError(f'status must be one of: {", ".join(VALID_STATUSES)}')
        task.status = data['status']
    if 'priority' in data:
        if data['priority'] not in VALID_PRIORITIES:
            raise ValidationError(f'priority must be one of: {", ".join(VALID_PRIORITIES)}')
        task.priority = data['priority']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first()
    if not task:
        raise NotFoundError(f'Task {task_id} not found in project {project_id}')

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': f'Task {task_id} deleted successfully'}), 200

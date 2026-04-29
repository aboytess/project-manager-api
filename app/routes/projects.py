from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.project import Project
from ..models.user import User
from ..errors import NotFoundError, ValidationError

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')
    return jsonify(project.to_dict()), 200


@projects_bp.route('', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data or not data.get('name'):
        raise ValidationError('name is required')
    if not data.get('owner_id'):
        raise ValidationError('owner_id is required')

    owner = User.query.get(data['owner_id'])
    if not owner:
        raise NotFoundError(f'User with id {data["owner_id"]} not found')

    project = Project(
        name=data['name'],
        description=data.get('description'),
        owner_id=data['owner_id']
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')

    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']

    db.session.commit()
    return jsonify(project.to_dict()), 200


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': f'Project {project_id} deleted successfully'}), 200

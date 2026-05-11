from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.project import Project
from ..errors import NotFoundError, ValidationError, ForbiddenError

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')
    return jsonify(project.to_dict()), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get('name'):
        raise ValidationError('name is required')

    project = Project(
        name=data['name'],
        description=data.get('description'),
        owner_id=current_user_id
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = int(get_jwt_identity())
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')
    if project.owner_id != current_user_id:
        raise ForbiddenError('You do not have permission to modify this project')

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
@jwt_required()
def delete_project(project_id):
    current_user_id = int(get_jwt_identity())
    project = Project.query.get(project_id)
    if not project:
        raise NotFoundError(f'Project with id {project_id} not found')
    if project.owner_id != current_user_id:
        raise ForbiddenError('You do not have permission to delete this project')

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': f'Project {project_id} deleted successfully'}), 200

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..validators import parse_json, validate_string, validate_optional_string, get_accessible_project, get_owned_project

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


def current_user_id() -> str:
    return get_jwt_identity()


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = current_user_id()
    projects = (Project.query
                .join(ProjectMember, Project.id == ProjectMember.project_id)
                .filter(ProjectMember.user_id == user_id)
                .all())
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id: str):
    project = get_accessible_project(project_id, current_user_id())
    return jsonify(project.to_dict()), 200


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = current_user_id()
    data = parse_json()
    project = Project(
        name=validate_string(data.get('name'), 'name', max_length=120),
        description=validate_optional_string(data.get('description'), 'description', max_length=500),
        owner_id=user_id
    )
    db.session.add(project)
    db.session.flush()  # populates project.id before commit
    membership = ProjectMember(project_id=project.id, user_id=user_id, role='owner')
    db.session.add(membership)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id: str):
    project = get_owned_project(project_id, current_user_id())
    data = parse_json()
    if 'name' in data:
        project.name = validate_string(data['name'], 'name', max_length=120)
    if 'description' in data:
        project.description = validate_optional_string(data['description'], 'description', max_length=500)
    db.session.commit()
    return jsonify(project.to_dict()), 200


@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id: str):
    project = get_owned_project(project_id, current_user_id())
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': f'Project {project.name} deleted successfully'}), 200

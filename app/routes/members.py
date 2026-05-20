from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.user import User
from ..models.project_member import ProjectMember
from ..validators import parse_json, validate_enum, get_accessible_project, get_managed_project
from ..errors import NotFoundError, ConflictError, ValidationError

members_bp = Blueprint('members', __name__, url_prefix='/api/projects')

VALID_ROLES = {'member', 'admin'}


def current_user_id() -> str:
    return get_jwt_identity()


@members_bp.route('/<project_id>/members', methods=['GET'])
@jwt_required()
def get_members(project_id: str):
    get_accessible_project(project_id, current_user_id())
    members = (ProjectMember.query
               .options(joinedload(ProjectMember.user))
               .filter_by(project_id=project_id)
               .all())
    return jsonify([m.to_dict() for m in members]), 200


@members_bp.route('/<project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id: str):
    get_managed_project(project_id, current_user_id())
    data = parse_json()

    user_id = data.get('user_id')
    if not user_id or not isinstance(user_id, str):
        raise ValidationError('user_id is required')

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')
    if ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first():
        raise ConflictError('User is already a member of this project')

    member = ProjectMember(project_id=project_id, user_id=user_id, role='member')
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@members_bp.route('/<project_id>/members/<user_id>', methods=['PUT'])
@jwt_required()
def update_member_role(project_id: str, user_id: str):
    project = get_managed_project(project_id, current_user_id())

    if user_id == project.owner_id:
        raise ValidationError('Cannot change the role of the project owner')

    data = parse_json()
    role = validate_enum(data.get('role'), 'role', VALID_ROLES)

    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        raise NotFoundError('User is not a member of this project')

    member.role = role
    db.session.commit()
    return jsonify(member.to_dict()), 200


@members_bp.route('/<project_id>/members/<user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(project_id: str, user_id: str):
    project = get_managed_project(project_id, current_user_id())

    if user_id == project.owner_id:
        raise ValidationError('Cannot remove the project owner')

    member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        raise NotFoundError('User is not a member of this project')

    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member removed successfully'}), 200

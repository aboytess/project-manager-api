from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_openapi3 import APIBlueprint, Tag
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.user import User
from ..models.project_member import ProjectMember
from ..validators import validate_string, validate_enum, get_accessible_project, get_managed_project
from ..errors import NotFoundError, ConflictError, ValidationError
from ..schemas.paths import ProjectPath, MemberPath
from ..schemas.members import AddMemberBody, UpdateRoleBody

_tag = Tag(name='members', description='Project member management')

members_bp = APIBlueprint(
    'members', __name__,
    url_prefix='/api/projects',
    abp_tags=[_tag],
    abp_security=[{'bearerAuth': []}]
)

VALID_ROLES = {'member', 'admin'}


def current_user_id() -> str:
    return get_jwt_identity()


@members_bp.get('/<project_id>/members', summary='List all members of a project')
@jwt_required()
def get_members(path: ProjectPath):
    get_accessible_project(path.project_id, current_user_id())
    members = (ProjectMember.query
               .options(joinedload(ProjectMember.user))
               .filter_by(project_id=path.project_id)
               .all())
    return jsonify([m.to_dict() for m in members]), 200


@members_bp.post('/<project_id>/members', summary='Add a member to a project (owner or admin)')
@jwt_required()
def add_member(path: ProjectPath, body: AddMemberBody):
    get_managed_project(path.project_id, current_user_id())

    user_id = validate_string(body.user_id, 'user_id', max_length=36)

    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')
    if ProjectMember.query.filter_by(project_id=path.project_id, user_id=user_id).first():
        raise ConflictError('User is already a member of this project')

    member = ProjectMember(project_id=path.project_id, user_id=user_id, role='member')
    db.session.add(member)
    db.session.commit()
    return jsonify(member.to_dict()), 201


@members_bp.put('/<project_id>/members/<user_id>', summary="Update a member's role (owner or admin)")
@jwt_required()
def update_member_role(path: MemberPath, body: UpdateRoleBody):
    project = get_managed_project(path.project_id, current_user_id())

    if path.user_id == project.owner_id:
        raise ValidationError('Cannot change the role of the project owner')

    role = validate_enum(body.role, 'role', VALID_ROLES)

    member = ProjectMember.query.filter_by(project_id=path.project_id, user_id=path.user_id).first()
    if not member:
        raise NotFoundError('User is not a member of this project')

    member.role = role
    db.session.commit()
    return jsonify(member.to_dict()), 200


@members_bp.delete('/<project_id>/members/<user_id>', summary='Remove a member from a project (owner or admin)')
@jwt_required()
def remove_member(path: MemberPath):
    project = get_managed_project(path.project_id, current_user_id())

    if path.user_id == project.owner_id:
        raise ValidationError('Cannot remove the project owner')

    member = ProjectMember.query.filter_by(project_id=path.project_id, user_id=path.user_id).first()
    if not member:
        raise NotFoundError('User is not a member of this project')

    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member removed successfully'}), 200

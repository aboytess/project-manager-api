from datetime import datetime, timezone
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_openapi3 import APIBlueprint, Tag
from ..extensions import db
from ..models.user import User
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.revoked_token import RevokedToken
from ..errors import NotFoundError, ConflictError
from ..schemas.paths import UserPath
from ..schemas.users import UserPublicResponse
from ..schemas.shared import MessageResponse, UnauthorizedResponse, NotFoundResponse, ConflictResponse

_tag = Tag(name='users', description='User operations')

users_bp = APIBlueprint(
    'users', __name__,
    url_prefix='/api/users',
    abp_tags=[_tag],
    abp_security=[{'bearerAuth': []}]
)


@users_bp.get(
    '/<user_id>',
    summary='Get a public user profile by ID',
    description='Returns a user\'s public profile (id and username only).',
    responses={
        '200': UserPublicResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse
    }
)
@jwt_required()
def get_user(path: UserPath):
    user = User.query.get(path.user_id)
    if not user:
        raise NotFoundError(f'User {path.user_id} not found')
    return jsonify(user.to_public_dict()), 200


@users_bp.delete(
    '/me',
    summary='Delete own account and revoke current token',
    description=(
        'Permanently deletes the authenticated user\'s account and revokes the current token. '
        'Fails with 409 if the user still owns any projects — transfer ownership or delete them first.'
    ),
    responses={
        '200': MessageResponse,
        '401': UnauthorizedResponse,
        '404': NotFoundResponse,
        '409': ConflictResponse
    }
)
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')

    if Project.query.filter_by(owner_id=user_id).first():
        raise ConflictError('Transfer ownership or delete your projects before deleting your account')

    token = get_jwt()
    db.session.add(RevokedToken(
        jti=token['jti'],
        expires_at=datetime.fromtimestamp(token['exp'], tz=timezone.utc)
    ))
    ProjectMember.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Account deleted successfully'}), 200

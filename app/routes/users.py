from datetime import datetime, timezone
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ..extensions import db
from ..models.user import User
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..models.revoked_token import RevokedToken
from ..errors import NotFoundError, ConflictError

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id: str):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')
    return jsonify(user.to_public_dict()), 200


@users_bp.route('/me', methods=['DELETE'])
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

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..models.user import User
from ..errors import NotFoundError

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id: str):
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f'User {user_id} not found')
    return jsonify(user.to_public_dict()), 200

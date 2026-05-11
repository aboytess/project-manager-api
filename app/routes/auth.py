from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from ..extensions import db, jwt_blocklist
from ..models.user import User
from ..errors import ValidationError, ConflictError, UnauthorizedError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username:
        raise ValidationError('username is required')
    if not email:
        raise ValidationError('email is required')
    if not password:
        raise ValidationError('password is required')
    if len(password) < 8:
        raise ValidationError('password must be at least 8 characters')

    if User.query.filter_by(email=email).first():
        raise ConflictError('email already registered')
    if User.query.filter_by(username=username).first():
        raise ConflictError('username already taken')

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        raise ValidationError('Request body is required')

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        raise ValidationError('email and password are required')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        raise UnauthorizedError('Invalid email or password')

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(current_user_id))
    return jsonify({'access_token': new_access_token}), 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jwt_blocklist.add(token['jti'])
    return jsonify({'message': 'Token revoked successfully'}), 200

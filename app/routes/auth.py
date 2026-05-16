from datetime import datetime, timezone
from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from ..extensions import db
from ..models.user import User
from ..models.revoked_token import RevokedToken
from ..validators import parse_json, validate_string
from ..errors import ValidationError, ConflictError, UnauthorizedError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _issue_tokens(user: User) -> dict:
    return {
        'access_token': create_access_token(identity=user.id),
        'refresh_token': create_refresh_token(identity=user.id),
        'user': user.to_dict()
    }


@auth_bp.route('/register', methods=['POST'])
def register():
    data = parse_json()
    username = validate_string(data.get('username'), 'username', max_length=80)
    email = validate_string(data.get('email'), 'email', max_length=120).lower()
    password = validate_string(data.get('password'), 'password', max_length=128)

    if len(password) < 8:
        raise ValidationError('password must be at least 8 characters')
    if User.query.filter_by(email=email).first():
        raise ConflictError('email already registered')
    if User.query.filter_by(username=username).first():
        raise ConflictError('username already taken')

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    return jsonify(_issue_tokens(user)), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = parse_json()
    email = validate_string(data.get('email'), 'email', max_length=120).lower()
    password = validate_string(data.get('password'), 'password', max_length=128)

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise UnauthorizedError('Invalid email or password')

    return jsonify(_issue_tokens(user)), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    new_access_token = create_access_token(identity=get_jwt_identity())
    return jsonify({'access_token': new_access_token}), 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    revoked = RevokedToken(
        jti=token['jti'],
        expires_at=datetime.fromtimestamp(token['exp'], tz=timezone.utc)
    )
    db.session.add(revoked)
    db.session.commit()
    return jsonify({'message': 'Token revoked successfully'}), 200

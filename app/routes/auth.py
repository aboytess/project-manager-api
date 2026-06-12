from datetime import datetime, timezone
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from flask_openapi3 import APIBlueprint, Tag
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.user import User
from ..models.revoked_token import RevokedToken
from ..errors import ConflictError, UnauthorizedError
from ..schemas.auth import RegisterBody, LoginBody, TokenResponse, AccessTokenResponse
from ..schemas.shared import (
    MessageResponse,
    UnauthorizedResponse,
    ConflictResponse,
    UnprocessableResponse,
)

_tag = Tag(name="auth", description="Authentication and token management")
_jwt_security = [{"bearerAuth": []}]

auth_bp = APIBlueprint("auth", __name__, url_prefix="/api/auth", abp_tags=[_tag])


def _issue_tokens(user: User) -> dict:
    return {
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id),
        "user": user.to_dict(),
    }


@auth_bp.post(
    "/register",
    summary="Register a new user",
    description="Create a new user account. Returns access and refresh tokens on success.",
    responses={
        "201": TokenResponse,
        "409": ConflictResponse,
        "422": UnprocessableResponse,
    },
)
def register(body: RegisterBody):
    if User.query.filter_by(email=body.email).first():
        raise ConflictError("email already registered")
    if User.query.filter_by(username=body.username).first():
        raise ConflictError("username already taken")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=generate_password_hash(body.password),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(_issue_tokens(user)), 201


@auth_bp.post(
    "/login",
    summary="Login and receive tokens",
    description="Authenticate with email and password. Returns access and refresh tokens.",
    responses={
        "200": TokenResponse,
        "401": UnauthorizedResponse,
        "422": UnprocessableResponse,
    },
)
def login(body: LoginBody):
    user = User.query.filter_by(email=body.email).first()
    if not user or not check_password_hash(user.password_hash, body.password):
        raise UnauthorizedError("Invalid email or password")

    return jsonify(_issue_tokens(user)), 200


@auth_bp.post(
    "/refresh",
    summary="Get a new access token using a refresh token",
    description=(
        "Exchange a valid refresh token for a new access token. "
        "Send the refresh token in the `Authorization: Bearer <token>` header."
    ),
    security=_jwt_security,
    responses={"200": AccessTokenResponse, "401": UnauthorizedResponse},
)
@jwt_required(refresh=True)
def refresh():
    new_access_token = create_access_token(identity=get_jwt_identity())
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.delete(
    "/logout",
    summary="Revoke the current token",
    description=(
        "Revoke the current access or refresh token. "
        "The token is added to a blocklist and cannot be used again."
    ),
    security=_jwt_security,
    responses={"200": MessageResponse, "401": UnauthorizedResponse},
)
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    revoked = RevokedToken(
        jti=token["jti"],
        expires_at=datetime.fromtimestamp(token["exp"], tz=timezone.utc),
    )
    db.session.add(revoked)
    db.session.commit()
    return jsonify({"message": "Token revoked successfully"}), 200

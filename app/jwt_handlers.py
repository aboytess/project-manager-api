from flask import jsonify
from .models.revoked_token import RevokedToken


def register_jwt_handlers(jwt):
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return RevokedToken.query.filter_by(jti=jwt_payload['jti']).first() is not None

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'TokenExpired', 'message': 'The token has expired', 'status_code': 401}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'InvalidToken', 'message': 'Token signature verification failed', 'status_code': 401}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Request does not contain an access token', 'status_code': 401}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'TokenRevoked', 'message': 'The token has been revoked', 'status_code': 401}), 401

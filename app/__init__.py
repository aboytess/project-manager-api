from flask import Flask, jsonify
from .config import DevelopmentConfig
from .extensions import db, migrate, jwt, jwt_blocklist
from .errors import register_error_handlers


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in jwt_blocklist

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

    from .models import User, Project, Task  # noqa: F401

    from .routes.auth import auth_bp
    from .routes.projects import projects_bp
    from .routes.tasks import tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)

    register_error_handlers(app)

    return app

from flask import Flask
from .config import DevelopmentConfig
from .extensions import db, migrate, jwt
from .errors import register_error_handlers
from .jwt_handlers import register_jwt_handlers


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_jwt_handlers(jwt)

    from .models import User, Project, Task, ProjectMember, RevokedToken  # noqa: F401

    from .routes.auth import auth_bp
    from .routes.projects import projects_bp
    from .routes.tasks import tasks_bp
    from .routes.members import members_bp
    from .routes.users import users_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(users_bp)

    register_error_handlers(app)

    return app

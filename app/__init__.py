from flask import Flask
from .config import DevelopmentConfig
from .extensions import db, migrate
from .errors import register_error_handlers


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User, Project, Task  # noqa: F401

    from .routes.projects import projects_bp
    from .routes.tasks import tasks_bp
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)

    register_error_handlers(app)

    return app

from flask_openapi3 import OpenAPI, Info, Contact
from .config import DevelopmentConfig
from .extensions import db, migrate, jwt
from .errors import register_error_handlers
from .jwt_handlers import register_jwt_handlers

_info = Info(
    title='Project Manager API',
    version='1.1.0',
    description=(
        'A REST API for managing projects, tasks, and teams — inspired by tools like Jira.\n\n'
        '## Authentication\n'
        'Most endpoints require a Bearer token. Use `POST /api/auth/login` to obtain one, '
        'then include it in the `Authorization: Bearer <token>` header.\n\n'
        '## Roles\n'
        'Projects support three roles: **owner** (full control), **admin** (can manage members and tasks), '
        'and **member** (can view and edit tasks).'
    ),
    contact=Contact(name='Andres', email='aboytes623@gmail.com')
)

_security_schemes = {
    'bearerAuth': {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT'
    }
}


def create_app(config_class=DevelopmentConfig):
    app = OpenAPI(__name__, info=_info, security_schemes=_security_schemes)
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
    app.register_api(auth_bp)
    app.register_api(projects_bp)
    app.register_api(tasks_bp)
    app.register_api(members_bp)
    app.register_api(users_bp)

    register_error_handlers(app)

    return app

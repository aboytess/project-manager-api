from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_openapi3 import APIBlueprint, Tag
from ..extensions import db
from ..models.project import Project
from ..models.project_member import ProjectMember
from ..validators import get_accessible_project, get_managed_project, get_owned_project
from ..schemas.paths import ProjectPath
from ..schemas.projects import (
    CreateProjectBody,
    UpdateProjectBody,
    ProjectResponse,
    ProjectListResponse,
)
from ..schemas.shared import (
    MessageResponse,
    UnauthorizedResponse,
    NotFoundResponse,
    UnprocessableResponse,
)

_tag = Tag(name="projects", description="Project CRUD operations")

projects_bp = APIBlueprint(
    "projects",
    __name__,
    url_prefix="/api/projects",
    abp_tags=[_tag],
    abp_security=[{"bearerAuth": []}],
)


def current_user_id() -> str:
    return get_jwt_identity()


@projects_bp.get(
    "",
    summary="List all projects the current user belongs to",
    description="Returns all projects where the authenticated user is a member, regardless of role.",
    responses={"200": ProjectListResponse, "401": UnauthorizedResponse},
)
@jwt_required()
def get_projects():
    user_id = current_user_id()
    projects = (
        Project.query.join(ProjectMember, Project.id == ProjectMember.project_id)
        .filter(ProjectMember.user_id == user_id)
        .all()
    )
    return jsonify([p.to_dict() for p in projects]), 200


@projects_bp.get(
    "/<project_id>",
    summary="Get a project by ID",
    description="Returns a project by ID. Returns 404 if the project does not exist or the authenticated user is not a member.",
    responses={
        "200": ProjectResponse,
        "401": UnauthorizedResponse,
        "404": NotFoundResponse,
    },
)
@jwt_required()
def get_project(path: ProjectPath):
    project = get_accessible_project(path.project_id, current_user_id())
    return jsonify(project.to_dict()), 200


@projects_bp.post(
    "",
    summary="Create a new project",
    description="Creates a new project. The authenticated user is automatically added as owner.",
    responses={
        "201": ProjectResponse,
        "401": UnauthorizedResponse,
        "422": UnprocessableResponse,
    },
)
@jwt_required()
def create_project(body: CreateProjectBody):
    user_id = current_user_id()
    project = Project(name=body.name, description=body.description, owner_id=user_id)
    db.session.add(project)
    db.session.flush()
    membership = ProjectMember(project_id=project.id, user_id=user_id, role="owner")
    db.session.add(membership)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.patch(
    "/<project_id>",
    summary="Update a project (owner or admin)",
    description=(
        "Partially updates a project's name or description. Requires Owner or Admin role. "
        "Returns 404 if the project does not exist or the authenticated user is not a member with sufficient privileges."
    ),
    responses={
        "200": ProjectResponse,
        "401": UnauthorizedResponse,
        "404": NotFoundResponse,
        "422": UnprocessableResponse,
    },
)
@jwt_required()
def update_project(path: ProjectPath, body: UpdateProjectBody):
    project = get_managed_project(path.project_id, current_user_id())
    data = body.model_dump(exclude_unset=True)
    if "name" in data:
        project.name = body.name
    if "description" in data:
        project.description = body.description
    db.session.commit()
    return jsonify(project.to_dict()), 200


@projects_bp.delete(
    "/<project_id>",
    summary="Delete a project (owner only)",
    description=(
        "Permanently deletes a project and all its tasks. Requires Owner role. "
        "Returns 404 if the project does not exist or the authenticated user is not the owner."
    ),
    responses={
        "200": MessageResponse,
        "401": UnauthorizedResponse,
        "404": NotFoundResponse,
    },
)
@jwt_required()
def delete_project(path: ProjectPath):
    project = get_owned_project(path.project_id, current_user_id())
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": f"Project {project.name} deleted successfully"}), 200

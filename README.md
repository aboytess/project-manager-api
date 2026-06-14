# Project Manager API

A RESTful task management API built with Flask and PostgreSQL — a lightweight backend for organizing projects and tasks across teams, inspired by tools like Jira.

![CI](https://github.com/aboytess/project-manager-api/actions/workflows/ci.yml/badge.svg)

## Stack

- **Flask** + **Flask-OpenAPI3** — API framework with automatic OpenAPI documentation
- **PostgreSQL** — relational database
- **SQLAlchemy** + **Flask-Migrate** — ORM and schema migrations
- **JWT** — stateless authentication with access and refresh tokens
- **Docker** + **docker-compose** — containerized dev and production environments
- **GitHub Actions** — CI pipeline with parallel lint, security, and test jobs

## Quick Start

Requires [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/).

```bash
git clone https://github.com/aboytess/project-manager-api.git
cd project-manager-api
cp .env.example .env   # fill in your values
docker compose up
```

The API will be available at `http://localhost:5000`.

## Environment Variables

Copy `.env.example` to `.env` and fill in the required values before running:

```
SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=postgresql://user:password@db:5432/dbname
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
```

## API Documentation

Interactive documentation (Swagger UI) is available at `http://localhost:5000/openapi/swagger` once the server is running.

## Running Tests

```bash
pytest -v
```

Tests require a running PostgreSQL instance. Set `TEST_DATABASE_URL` in your environment or `.env` file before running locally:

```
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
```

## Technical Highlights

- Role-based access control with admin and member roles
- JWT authentication with short-lived access tokens and rotating refresh tokens
- Schema migrations with Flask-Migrate for safe, version-controlled database changes
- Separate dev and production Docker configurations via docker-compose override files
- Parallel CI jobs: style and lint (ruff), vulnerability scanning (pip-audit), and integration tests (pytest + PostgreSQL)
- Isolated test teardown using `NullPool` and explicit session release to prevent PostgreSQL lock conflicts

---

*Built as a portfolio project — the majority of the stack (PostgreSQL, Docker, JWT, CI/CD, OpenAPI) was learned hands-on during development.*

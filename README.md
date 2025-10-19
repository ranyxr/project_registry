# Project Registry API

FastAPI service for managing data projects with PostgreSQL persistence, JWT-based authentication, and Docker-first deployment.

## Architecture & Design Decisions
- **FastAPI + SQLAlchemy 2.0**: async-ready web framework coupled with modern SQLAlchemy ORM for type-safe persistence.
- **PostgreSQL via Docker**: production-parity database managed through Docker Compose; migrations handled with Alembic.
- **Layered modules**: `models.py`, `schemas.py`, `service.py`, and `views.py` separate persistence, validation, business logic, and routing for testability and clarity.
- **Authentication & Authorization**: OAuth2 password flow with JWT tokens. Project endpoints require valid tokens and enforce per-owner access control.
- **Configuration via Settings**: `pydantic-settings` centralizes environment configuration with sane defaults and `.env` overrides.
- **CI/CD ready**: GitHub Actions workflow installs dependencies with `uv`, runs tests, and is ready to extend for container builds/pushes.
- **Cloud deployment strategy**: containerized app designed for orchestration platforms (ECS/Fargate, AKS, GKE) behind an HTTPS ingress. Stateless API with external Postgres facilitates horizontal scaling.

## Getting Started
1. **Install uv** (if not already): `pip install uv`
2. **Set up environment**: copy `.env.example` to `.env` and adjust secrets.
3. **Install dependencies**: `uv sync`
4. **Run database migrations**: `uv run alembic upgrade head`
5. **Start the API**: `uv run uvicorn app.main:app --reload`
6. Visit `http://localhost:8000/docs` for interactive OpenAPI docs.

## Docker Compose
```bash
docker compose up --build
```
Services:
- `api`: FastAPI app served by Uvicorn (port 8000)
- `db`: PostgreSQL 15 with persistent volume `postgres_data`

## Database & Migrations
- SQLAlchemy models live in `app/models.py`
- Alembic environment configured in `migrations/env.py`
- Generate new migrations: `uv run alembic revision --autogenerate -m "description"`
- Apply migrations: `uv run alembic upgrade head`

## Authentication Flow
- Register with `POST /auth/register`
- Obtain token via OAuth2 password flow `POST /auth/token`
- Authorize requests with `Authorization: Bearer <token>` header
- Project endpoints are owner-scoped; users can manipulate only their projects.

## Testing
```bash
uv run pytest
```
Pytest uses an in-memory SQLite database to keep tests fast and deterministic while exercising full request flows via FastAPI `TestClient`.

## CI/CD and Deployment Guidance
- **CI**: `.github/workflows/ci.yml` installs dependencies with uv, runs linting (via Ruff) and tests. Extend with Docker image builds and registry pushes for production pipelines.
- **CD**: recommended approach is building and pushing the container image, then deploying via:
  1. AWS ECS/Fargate + RDS PostgreSQL
  2. Azure Container Apps + Azure Database for PostgreSQL
  3. Google Cloud Run + Cloud SQL for PostgreSQL
- **Networking**: place the API behind a managed load balancer or API gateway. Enforce HTTPS, configure connection limits for Postgres, and expose only port 8000 internally.
- **Secrets**: store credentials (JWT secret, database URL) in a secrets manager (AWS Secrets Manager, Azure Key Vault, Google Secret Manager) rather than environment files.

## Project Structure
```
app/
  config.py        # Environment settings
  database.py      # SQLAlchemy engine/session management
  main.py          # FastAPI application factory
  models.py        # ORM models
  schemas.py       # Pydantic models
  service.py       # Domain logic for users/projects
  views.py         # API routers and endpoints
  security.py      # Password hashing + JWT helpers
  dependencies.py  # FastAPI dependency wiring
migrations/        # Alembic environment and revisions
scripts/           # Entry scripts for containers
tests/             # Pytest suite
```

## API Snapshot
- `GET /health` – health probe
- `POST /auth/register` – create user
- `POST /auth/token` – login (OAuth2 password flow)
- `GET /projects/` – list projects for current user
- `POST /projects/` – create project
- `GET /projects/{id}` – read single project
- `PATCH /projects/{id}` – update project metadata
- `DELETE /projects/{id}` – delete project

## Next Steps
- Integrate background jobs for expiration reminders (e.g., Celery or APScheduler)
- Add pagination and filtering to project listing
- Extend authorization with role-based access control for shared projects

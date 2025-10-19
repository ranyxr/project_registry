from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.security import create_access_token
from app.service import ProjectService, UserService

router = APIRouter()

auth_router = APIRouter(prefix="/auth", tags=["auth"])
project_router = APIRouter(prefix="/projects", tags=["projects"])


@auth_router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return the created profile."""

    user_service = UserService(db)
    user = user_service.create_user(user_in)
    return user


@auth_router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user credentials and return a JWT access token."""

    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    token = create_access_token(subject=user.email)
    return schemas.Token(access_token=token)


@project_router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a project owned by the authenticated user."""

    project_service = ProjectService(db)
    project = project_service.create_project(current_user.id, project_in)
    return project


@project_router.get("/", response_model=List[schemas.ProjectRead])
def list_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all projects owned by the current user."""

    project_service = ProjectService(db)
    return project_service.list_projects(owner_id=current_user.id)


@project_router.get("/{project_id}", response_model=schemas.ProjectRead)
def get_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single project ensuring ownership."""

    project_service = ProjectService(db)
    return project_service.get_project(project_id, owner_id=current_user.id)


@project_router.patch("/{project_id}", response_model=schemas.ProjectRead)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply partial updates to a project when the current user is the owner."""

    project_service = ProjectService(db)
    return project_service.update_project(project_id, owner_id=current_user.id, project_update=project_update)


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a project owned by the current user."""

    project_service = ProjectService(db)
    project_service.delete_project(project_id, owner_id=current_user.id)
    return None

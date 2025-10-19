from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.security import get_password_hash, verify_password


class UserService:
    """Domain logic for user lifecycle operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.db.scalar(select(models.User).where(models.User.email == email))

    def create_user(self, user_in: schemas.UserCreate) -> models.User:
        if self.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = models.User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> models.User:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        return user


class ProjectService:
    """Project business logic separated from transport concerns."""

    def __init__(self, db: Session):
        self.db = db

    def create_project(self, owner_id: int, project_in: schemas.ProjectCreate) -> models.Project:
        project = models.Project(
            name=project_in.name,
            description=project_in.description,
            expiration_date=project_in.expiration_date,
            owner_id=owner_id,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_projects(self, owner_id: Optional[int] = None) -> Iterable[models.Project]:
        stmt = select(models.Project)
        if owner_id is not None:
            stmt = stmt.where(models.Project.owner_id == owner_id)
        stmt = stmt.order_by(models.Project.created_at.desc())
        return self.db.scalars(stmt).all()

    def get_project(self, project_id: int, owner_id: Optional[int] = None) -> models.Project:
        stmt = select(models.Project).where(models.Project.id == project_id)
        if owner_id is not None:
            stmt = stmt.where(models.Project.owner_id == owner_id)
        project = self.db.scalar(stmt)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    def update_project(
        self,
        project_id: int,
        owner_id: int,
        project_update: schemas.ProjectUpdate,
    ) -> models.Project:
        project = self.get_project(project_id, owner_id)
        for field, value in project_update.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: int, owner_id: int) -> None:
        project = self.get_project(project_id, owner_id)
        self.db.delete(project)
        self.db.commit()

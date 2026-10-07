from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository handling database operations for User entities."""

    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Fetch a single user by primary key ID."""
        statement = select(User).where(User.id == user_id)
        return db.scalar(statement)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Fetch a user by normalized email address."""
        statement = select(User).where(User.email == email.strip().lower())
        return db.scalar(statement)

    def create(self, db: Session, user: User) -> User:
        """Persist a new User entity to the database."""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User) -> User:
        """Update and commit an existing User entity."""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository()

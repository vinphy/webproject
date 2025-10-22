from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Session

from util.db import Base, init_db


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RolePermission(Base):
    __tablename__ = "role_permissions"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    __table_args__ = (UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role")
    created_at = Column(DateTime, default=datetime.utcnow)


# Ensure tables exist
init_db(Base)


# CRUD helpers
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
    return db.query(User).filter((User.username == identifier) | (User.email == identifier)).first()


def get_user_by_id(db: Session, pk: int) -> Optional[User]:
    return db.query(User).get(pk)


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()


def create_role(db: Session, name: str, description: Optional[str] = None) -> Role:
    role = Role(name=name, description=description)
    db.add(role)
    db.flush()
    return role


def create_user(db: Session, username: str, email: str, hashed_password: str, role_obj: Optional[Role] = None) -> User:
    user = User(username=username, email=email, hashed_password=hashed_password, role=role_obj)
    db.add(user)
    db.flush()
    return user


def list_users(db: Session):
    return db.query(User).all()


def list_roles(db: Session):
    return db.query(Role).all()


def update_user_role(db: Session, user_id: int, role_name: Optional[str]):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    role = get_role_by_name(db, role_name) if role_name else None
    user.role = role
    db.commit()
    return user


def ensure_default_admin(db: Session):
    """Ensure an 'admin' role and 'admin' user exist. Idempotent."""
    admin_role = get_role_by_name(db, "admin")
    if admin_role is None:
        admin_role = Role(name="admin", description="Administrator")
        db.add(admin_role)
        db.flush()
    user = get_user_by_username(db, "admin")
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if user is None:
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=pwd_context.hash("123456"),
            role=admin_role,
        )
        db.add(user)
    else:
        if not user.role_id:
            user.role = admin_role
    db.commit()

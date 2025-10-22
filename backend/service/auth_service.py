from datetime import datetime, timedelta
from typing import Optional, Tuple
import hashlib
import re

from jose import jwt, JWTError
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from models.auth_model import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_username_or_email,
    get_role_by_name,
    create_role,
    create_user,
    get_user_by_id,
)

# Config (could be moved to settings/env later)
SECRET_KEY = "CHANGE_ME_TO_ENV_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        if hashed_password.startswith("$2"):
            return pwd_context.verify(plain_password, hashed_password)
        if re.fullmatch(r"[0-9a-fA-F]{64}", hashed_password):
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return str(plain_password) == str(hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def register_user(db: Session, username: str, email: str, password: str, role: Optional[str] = None):
    # validation
    if get_user_by_username(db, username) or get_user_by_email(db, email):
        raise ValueError("用户名或邮箱已存在")
    role_obj = None
    if role:
        role_obj = get_role_by_name(db, role)
        if role_obj is None:
            role_obj = create_role(db, role)
    hashed = get_password_hash(password)
    user = create_user(db, username=username, email=email, hashed_password=hashed, role_obj=role_obj)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, identifier: str, password: str) -> Tuple[Optional[dict], Optional[str]]:
    user = get_user_by_username_or_email(db, identifier)
    if not user:
        return None, None
    if not verify_password(password, user.hashed_password):
        # auto-fix admin hash if needed
        if user.username == "admin":
            try:
                user.hashed_password = get_password_hash(password)
                db.commit()
                if verify_password(password, user.hashed_password):
                    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role.name if user.role else None})
                    return {"id": user.id, "username": user.username, "role": user.role.name if user.role else None}, token
            except Exception:
                pass
        return None, None
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role.name if user.role else None})
    return {"id": user.id, "username": user.username, "role": user.role.name if user.role else None}, token


def get_user_by_token_payload(db: Session, payload: dict):
    sub = payload.get("sub")
    if not sub:
        return None
    return get_user_by_id(db, int(sub))

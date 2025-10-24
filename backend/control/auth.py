from fastapi import APIRouter, Depends, HTTPException, status, Body, Request, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from util.db import get_db
from models import auth_model
from service import auth_service
from service import log_service

# Local aliases to simplify references in this controller
Role = auth_model.Role
Permission = auth_model.Permission
RolePermission = auth_model.RolePermission
User = auth_model.User


# Schemas (kept here for API contracts)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[str]

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class UserCreateAdmin(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class PermissionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class RoleAssignPermissions(BaseModel):
    permissions: list[int] = []


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", response_model=UserOut)
async def register(
    request: Request,
    db: Session = Depends(get_db),
    username: str | None = Form(None),
    email: str | None = Form(None),
    password: str | None = Form(None),
    role: str | None = Form(None),
    role_file: UploadFile | None = File(None),
):
    """Thin controller: parse request (JSON or multipart), extract role/file, then delegate to auth_service.register_user"""
    ctype = request.headers.get("content-type", "")
    if ctype.startswith("multipart/form-data"):
        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="缺少注册字段: username/email/password")
        # handle optional uploaded file
        if role_file and not role:
            try:
                content = await role_file.read()
                try:
                    text = content.decode("utf-8")
                except Exception:
                    text = content.decode("latin1", errors="ignore")
                extracted = text.strip().splitlines()[0] if text.strip() else None
                if extracted:
                    role = extracted[:200]
                else:
                    role = role_file.filename
            except Exception:
                # ignore file errors at controller level; service will validate
                role = role or None
    else:
        body = await request.json()
        u = UserCreate(**body)
        username = u.username
        email = u.email
        password = u.password
        role = u.role

    try:
        user = auth_service.register_user(db, username=username, email=email, password=password, role=role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserOut(id=user.id, username=user.username, email=user.email, role=user.role.name if user.role else None)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_info, token = auth_service.login_user(db, form_data.username, form_data.password)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    # record login log
    try:
        log_service.create_log(db, type='操作日志', source='认证', user=user_info.get('username'), message=f"用户登录：{user_info.get('username')}", level='INFO')
    except Exception:
        pass
    return {"access_token": token, "token_type": "bearer"}


# logout route implemented after get_current_user definition to avoid forward reference issues


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    from jose import jwt, JWTError

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="凭证无效",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth_model.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: auth_model.User = Depends(get_current_user)):
    return UserOut(id=current_user.id, username=current_user.username, email=current_user.email, role=current_user.role.name if current_user.role else None)


@router.get('/me/permissions')
def read_my_permissions(db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    """Return list of permission codes for current user. Empty list if none."""
    try:
        if not current_user or not getattr(current_user, 'role_id', None):
            return []
        joins = db.query(Permission).join(RolePermission, RolePermission.permission_id == Permission.id).filter(RolePermission.role_id == current_user.role_id).all()
        return [p.code for p in joins]
    except Exception:
        return []


# Now define logout properly (after get_current_user is defined)
@router.post('/logout')
def logout(db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    # record logout
    try:
        print("退出*****")
        uname = current_user.username if current_user else 'unknown'
        log_service.create_log(db, type='操作日志', source='认证', user=uname, message=f"用户退出：{uname}", level='INFO')
    except Exception:
        pass
    return { 'ok': True }


@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    rows = auth_model.list_users(db)
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role.name if u.role else None}
        for u in rows
    ]


@router.post("/users")
def create_user_admin(payload: UserCreateAdmin, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    if auth_model.get_user_by_username(db, payload.username) or auth_model.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    role = auth_model.get_role_by_name(db, payload.role) if payload.role else None
    new_user = auth_model.create_user(db, username=payload.username, email=payload.email, hashed_password=auth_service.get_password_hash(payload.password), role_obj=role)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id}

# 为用户指派角色
@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, body: dict = Body(...), db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    user = auth_model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    role_name = body.get("role")
    role = auth_model.get_role_by_name(db, role_name) if role_name else None
    user.role = role
    db.commit()
    return {"ok": True}

# 角色列表
@router.get("/roles")
def list_roles(db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    rows = auth_model.list_roles(db)
    return [
        {"id": r.id, "name": r.name, "description": r.description}
        for r in rows
    ]

# 创建角色
@router.post("/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    exists = auth_model.get_role_by_name(db, role.name)
    if exists:
        raise HTTPException(status_code=400, detail="角色已存在")
    new_role = auth_model.create_role(db, role.name, role.description)
    db.commit()
    db.refresh(new_role)
    return {"id": new_role.id}


@router.put("/roles/{role_id}")
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    role = db.query(auth_model.Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if payload.name:
        conflict = db.query(auth_model.Role).filter(auth_model.Role.name == payload.name, auth_model.Role.id != role_id).first()
        if conflict:
            raise HTTPException(status_code=400, detail="角色名已存在")
        role.name = payload.name
    if payload.description is not None:
        role.description = payload.description
    db.commit()
    return {"ok": True}

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    # 不能删除 admin 角色
    if role.name == "admin":
        raise HTTPException(status_code=400, detail="不能删除系统管理员角色")
    db.delete(role)
    db.commit()
    return {"ok": True}

# 权限列表
@router.get("/permissions")
def list_permissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    rows = db.query(Permission).all()
    return [{"id": p.id, "code": p.code, "name": p.name, "description": p.description} for p in rows]

# 创建权限
@router.post("/permissions")
def create_permission(payload: PermissionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    exists = db.query(Permission).filter(Permission.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="权限已存在")
    p = Permission(code=payload.code, name=payload.name, description=payload.description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id}

@router.put("/permissions/{perm_id}")
def update_permission(perm_id: int, payload: PermissionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    p = db.query(Permission).get(perm_id)
    if not p:
        raise HTTPException(status_code=404, detail="权限不存在")
    if payload.code:
        conflict = db.query(Permission).filter(Permission.code == payload.code, Permission.id != perm_id).first()
        if conflict:
            raise HTTPException(status_code=400, detail="权限编码已存在")
        p.code = payload.code
    if payload.name:
        p.name = payload.name
    if payload.description is not None:
        p.description = payload.description
    db.commit()
    return {"ok": True}

@router.delete("/permissions/{perm_id}")
def delete_permission(perm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    p = db.query(Permission).get(perm_id)
    if not p:
        raise HTTPException(status_code=404, detail="权限不存在")
    db.delete(p)
    db.commit()
    return {"ok": True}

# 读取角色权限
@router.get("/roles/{role_id}/permissions")
def role_permissions(role_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    joins = db.query(RolePermission, Permission).join(Permission, RolePermission.permission_id == Permission.id).filter(RolePermission.role_id == role_id).all()
    return [{"id": p.id, "code": p.code, "name": p.name} for _, p in joins]

# 分配角色权限
@router.post("/roles/{role_id}/permissions")
def assign_permissions(role_id: int, payload: RoleAssignPermissions, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    # delete old
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    # insert new
    for pid in payload.permissions:
        db.add(RolePermission(role_id=role_id, permission_id=pid))
    db.commit()
    return {"ok": True}

@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if payload.email:
        conflict = auth_model.get_user_by_email(db, payload.email)
        if conflict and conflict.id != user_id:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        user.email = payload.email
    if payload.password:
        user.hashed_password = auth_service.get_password_hash(payload.password)
    if payload.role is not None:
        role = auth_model.get_role_by_name(db, payload.role) if payload.role else None
        user.role = role
    db.commit()
    return {"ok": True}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 不允许删除自己或内置 admin
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="不能删除系统管理员用户")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录用户")
    db.delete(user)
    db.commit()
    return {"ok": True} 
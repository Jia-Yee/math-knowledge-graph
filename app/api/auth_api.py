# 认证 API
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import uuid
import hashlib

from app.api.database import get_db
from app.api.models_user import User, RefreshToken

router = APIRouter(prefix="/auth", tags=["认证"])

# JWT 配置
SECRET_KEY = "mathkg-jwt-secret-key-change-in-production-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


# ===== Pydantic 模型 =====
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=6, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    current_level: str
    created_at: datetime


# ===== 辅助函数 =====
def hash_password(password: str) -> str:
    """密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_access_token(user_id: str, username: str) -> tuple[str, datetime]:
    """创建访问令牌"""
    expires = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "username": username,
        "type": "access",
        "exp": expires,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires


def create_refresh_token(user_id: str, db: Session) -> str:
    """创建刷新令牌并存储到数据库"""
    token = str(uuid.uuid4())
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires
    )
    db.add(db_token)
    db.commit()
    
    return token


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """验证 JWT Token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ===== API 路由 =====
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        display_name=request.display_name or request.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建令牌
    access_token, expires = create_access_token(str(user.id), user.username)
    refresh_token = create_refresh_token(str(user.id), db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((expires - datetime.utcnow()).total_seconds()),
        user={
            "id": str(user.id),
            "username": user.username,
            "display_name": user.display_name,
            "current_level": user.current_level
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 创建令牌
    access_token, expires = create_access_token(str(user.id), user.username)
    refresh_token = create_refresh_token(str(user.id), db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int((expires - datetime.utcnow()).total_seconds()),
        user={
            "id": str(user.id),
            "username": user.username,
            "display_name": user.display_name,
            "current_level": user.current_level
        }
    )


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """刷新访问令牌"""
    # 计算令牌哈希
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    # 查找刷新令牌
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    # 获取用户
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 创建新的访问令牌
    access_token, expires = create_access_token(str(user.id), user.username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int((expires - datetime.utcnow()).total_seconds())
    }


@router.post("/logout")
async def logout(
    refresh_token: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """登出（撤销刷新令牌）"""
    if refresh_token:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).update({"revoked": True})
        db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=str(user.id),
        username=user.username,
        display_name=user.display_name,
        current_level=user.current_level,
        created_at=user.created_at
    )


@router.put("/password")
async def change_password(
    old_password: str,
    new_password: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    user.password_hash = hash_password(new_password)
    db.commit()
    
    # 撤销所有刷新令牌
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id
    ).update({"revoked": True})
    db.commit()
    
    return {"message": "Password changed successfully"}

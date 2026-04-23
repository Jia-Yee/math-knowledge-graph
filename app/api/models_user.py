# 用户模型
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.api.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    
    # 学习相关
    current_level = Column(String(20), default='primary')
    total_study_minutes = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_study_date = Column(DateTime, nullable=True)
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # 设置
    settings = Column(JSON, default=dict)


class UserKnowledge(Base):
    __tablename__ = "user_knowledge"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    node_id = Column(String(100), nullable=False)
    
    status = Column(String(20), default='unknown')
    confidence = Column(Float, default=0.5)
    
    study_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    last_study_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False)

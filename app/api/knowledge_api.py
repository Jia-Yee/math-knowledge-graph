"""
用户知识掌握 API
"""

import sys
sys.path.insert(0, '/Users/jia/.qclaw/workspace/math-knowledge-graph')

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.database import get_db
from app.api.models_user import User, UserKnowledge
from app.api.auth_api import get_current_user

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# ==================== 响应模型 ====================

class KnowledgeItem(BaseModel):
    node_id: str
    status: str
    confidence: float
    study_count: int
    correct_count: int
    last_study_at: Optional[str] = None

class KnowledgeListResponse(BaseModel):
    items: List[KnowledgeItem]
    total: int

class KnowledgeUpdateRequest(BaseModel):
    node_id: str
    status: str  # known, learning, unknown
    confidence: float = 0.0  # 0.0 - 1.0
    correct: bool = True  # 本次学习是否正确

class LearningStats(BaseModel):
    total_known: int
    total_learning: int
    total_unknown: int
    total_studied: int
    accuracy: float  # 正确率
    streak_days: int
    total_study_minutes: int

class StudyRecord(BaseModel):
    node_id: str
    status: str
    timestamp: str

# ==================== API 端点 ====================

@router.get("", response_model=KnowledgeListResponse)
async def get_knowledge_list(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的知识掌握列表
    
    - status: 筛选状态 (known/learning/unknown)
    - limit: 返回数量上限
    - offset: 跳过数量
    """
    query = db.query(UserKnowledge).filter(UserKnowledge.user_id == current_user.id)
    
    if status:
        query = query.filter(UserKnowledge.status == status)
    
    total = query.count()
    items = query.order_by(UserKnowledge.updated_at.desc()).offset(offset).limit(limit).all()
    
    return KnowledgeListResponse(
        total=total,
        items=[
            KnowledgeItem(
                node_id=item.node_id,
                status=item.status,
                confidence=item.confidence or 0.0,
                study_count=item.study_count or 0,
                correct_count=item.correct_count or 0,
                last_study_at=item.last_study_at.isoformat() if item.last_study_at else None
            )
            for item in items
        ]
    )

@router.put("")
async def update_knowledge(
    request: KnowledgeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新知识点掌握状态
    
    - node_id: 知识点 ID
    - status: 掌握状态 (known/learning/unknown)
    - confidence: 置信度 (0.0 - 1.0)
    - correct: 本次学习是否正确
    """
    # 查找或创建记录
    knowledge = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.node_id == request.node_id
    ).first()
    
    now = datetime.now(timezone.utc)
    
    if knowledge:
        # 更新现有记录
        knowledge.status = request.status
        knowledge.study_count = (knowledge.study_count or 0) + 1
        if request.correct:
            knowledge.correct_count = (knowledge.correct_count or 0) + 1
        # 更新置信度（加权平均）
        old_conf = knowledge.confidence or 0.0
        knowledge.confidence = old_conf * 0.7 + request.confidence * 0.3
        knowledge.last_study_at = now
        knowledge.updated_at = now
    else:
        # 创建新记录
        knowledge = UserKnowledge(
            user_id=current_user.id,
            node_id=request.node_id,
            status=request.status,
            confidence=request.confidence,
            study_count=1,
            correct_count=1 if request.correct else 0,
            last_study_at=now,
            created_at=now,
            updated_at=now
        )
        db.add(knowledge)
    
    db.commit()
    db.refresh(knowledge)
    
    return {
        "success": True,
        "node_id": request.node_id,
        "status": knowledge.status,
        "confidence": knowledge.confidence,
        "study_count": knowledge.study_count,
        "accuracy": knowledge.correct_count / knowledge.study_count if knowledge.study_count > 0 else 0
    }

@router.get("/stats", response_model=LearningStats)
async def get_learning_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取学习统计数据
    """
    # 统计各类知识数量
    known_count = db.query(func.count(UserKnowledge.id)).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.status == "known"
    ).scalar() or 0
    
    learning_count = db.query(func.count(UserKnowledge.id)).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.status == "learning"
    ).scalar() or 0
    
    unknown_count = db.query(func.count(UserKnowledge.id)).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.status == "unknown"
    ).scalar() or 0
    
    # 计算总学习次数和正确率
    total_studied = db.query(
        func.sum(UserKnowledge.study_count),
        func.sum(UserKnowledge.correct_count)
    ).filter(
        UserKnowledge.user_id == current_user.id
    ).first()
    
    total_study_count = total_studied[0] or 0
    total_correct_count = total_studied[1] or 0
    
    accuracy = total_correct_count / total_study_count if total_study_count > 0 else 0.0
    
    return LearningStats(
        total_known=known_count,
        total_learning=learning_count,
        total_unknown=unknown_count,
        total_studied=int(total_study_count),
        accuracy=round(accuracy * 100, 1),  # 转为百分比
        streak_days=current_user.streak_days or 0,
        total_study_minutes=current_user.total_study_minutes or 0
    )

@router.get("/node/{node_id}", response_model=KnowledgeItem)
async def get_node_knowledge(
    node_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取特定知识点的掌握状态
    """
    knowledge = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.node_id == node_id
    ).first()
    
    if not knowledge:
        # 返回默认状态
        return KnowledgeItem(
            node_id=node_id,
            status="unknown",
            confidence=0.0,
            study_count=0,
            correct_count=0,
            last_study_at=None
        )
    
    return KnowledgeItem(
        node_id=knowledge.node_id,
        status=knowledge.status,
        confidence=knowledge.confidence or 0.0,
        study_count=knowledge.study_count or 0,
        correct_count=knowledge.correct_count or 0,
        last_study_at=knowledge.last_study_at.isoformat() if knowledge.last_study_at else None
    )

@router.get("/recent", response_model=List[StudyRecord])
async def get_recent_studies(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取最近学习记录
    """
    records = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user.id
    ).order_by(
        UserKnowledge.last_study_at.desc()
    ).limit(limit).all()
    
    return [
        StudyRecord(
            node_id=r.node_id,
            status=r.status,
            timestamp=r.last_study_at.isoformat() if r.last_study_at else ""
        )
        for r in records
    ]

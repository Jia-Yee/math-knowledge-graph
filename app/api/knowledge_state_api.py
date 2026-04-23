"""
API 扩展模块 - 统一数据格式支持
此模块扩展 main.py 的功能，支持新的 knowledge_state 数据格式
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
USER_DATA_FILE = DATA_DIR / "user-profiles.json"

# ===== 数据模型 =====

class KnowledgeState(BaseModel):
    """知识点学习状态"""
    mastery: int = 0
    first_learned: str = ""
    last_practice: str = ""
    practice_count: int = 0
    review_count: int = 0
    confidence: float = 0.5
    history: List[dict] = []

class LearningEvent(BaseModel):
    """学习事件"""
    node_id: str
    event_type: str
    mastery_after: Optional[int] = None
    time_spent: Optional[int] = None
    correct_count: Optional[int] = None
    total_count: Optional[int] = None
    source: str = "api"

class DetailedAssessment(BaseModel):
    """详细评估（支持4级掌握度）"""
    node_id: str
    level: int
    notes: Optional[str] = None

# ===== 数据操作函数 =====

def load_all_user_data() -> dict:
    """加载所有用户数据"""
    if USER_DATA_FILE.exists():
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
    return {}

def save_all_user_data(data: dict):
    """保存所有用户数据"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

def load_user_data(user_id: str) -> Optional[dict]:
    """加载单个用户数据"""
    all_data = load_all_user_data()
    return all_data.get(user_id)

def save_user_data(user_id: str, user_data: dict):
    """保存单个用户数据"""
    all_data = load_all_user_data()
    all_data[user_id] = user_data
    save_all_user_data(all_data)

def create_default_user(user_id: str) -> dict:
    """创建默认用户数据"""
    now = datetime.now().isoformat()[:10]
    return {
        "profile": {
            "name": user_id,
            "grade": "小学四年级",
            "created_at": now,
            "updated_at": now
        },
        "abilities": {},
        "knowledge_state": {},
        "learning_summary": {
            "total_concepts": 0,
            "mastered_concepts": 0,
            "learning_concepts": 0,
            "weak_concepts": 0,
            "total_practice_time": 0,
            "current_streak": 0,
            "longest_streak": 0
        },
        "weaknesses": [],
        "interests": [],
        "achievements": [],
        "settings": {
            "daily_reminder": True,
            "reminder_time": "07:00",
            "difficulty_preference": "adaptive",
            "visualization_enabled": True
        }
    }

def calculate_learning_summary(knowledge_state: dict) -> dict:
    """计算学习汇总统计"""
    total = len(knowledge_state)
    mastered = 0
    learning = 0
    weak = 0
    total_time = 0
    
    for state in knowledge_state.values():
        mastery = state.get("mastery", 0)
        if mastery >= 80:
            mastered += 1
        elif mastery >= 50:
            learning += 1
        else:
            weak += 1
        total_time += state.get("practice_count", 0) * 5
    
    return {
        "total_concepts": total,
        "mastered_concepts": mastered,
        "learning_concepts": learning,
        "weak_concepts": weak,
        "total_practice_time": total_time,
        "current_streak": 0,
        "longest_streak": 0
    }

def update_knowledge_state(user_id: str, node_id: str, update: dict, source: str = "api") -> dict:
    """更新知识点的学习状态"""
    user_data = load_user_data(user_id)
    if not user_data:
        user_data = create_default_user(user_id)
    
    now = datetime.now().isoformat()[:10]
    
    if "knowledge_state" not in user_data:
        user_data["knowledge_state"] = {}
    
    state = user_data["knowledge_state"].get(node_id, {})
    
    if not state:
        state = {
            "mastery": 0,
            "first_learned": now,
            "last_practice": now,
            "practice_count": 0,
            "review_count": 0,
            "confidence": 0.5,
            "history": []
        }
    
    # 应用更新
    if "mastery" in update:
        old_mastery = state.get("mastery", 0)
        state["mastery"] = update["mastery"]
        state["last_practice"] = now
        state["practice_count"] = state.get("practice_count", 0) + 1
        
        if update["mastery"] > old_mastery:
            state["review_count"] = state.get("review_count", 0) + 1
    
    if "practice_count" in update:
        state["practice_count"] = update["practice_count"]
    
    # 更新历史
    state["history"].append({
        "date": now,
        "mastery": state["mastery"],
        "event": update.get("event_type", "update"),
        "source": source
    })
    
    # 保存
    user_data["knowledge_state"][node_id] = state
    user_data["learning_summary"] = calculate_learning_summary(user_data["knowledge_state"])
    user_data["profile"]["updated_at"] = now
    
    save_user_data(user_id, user_data)
    return state

def get_review_queue(user_id: str, knowledge_graph: dict, limit: int = 10) -> List[dict]:
    """获取需要复习的知识点队列"""
    user_data = load_user_data(user_id)
    if not user_data:
        return []
    
    knowledge_state = user_data.get("knowledge_state", {})
    today = datetime.now()
    queue = []
    
    for node_id, state in knowledge_state.items():
        mastery = state.get("mastery", 0)
        last_practice = state.get("last_practice", "")
        
        if not last_practice:
            continue
        
        try:
            last_date = datetime.fromisoformat(last_practice)
            days_since = (today - last_date).days
        except:
            continue
        
        needs_review = False
        priority = "low"
        reason = ""
        
        if mastery < 50:
            needs_review = True
            priority = "high"
            reason = "掌握度较低，需要加强"
        elif mastery < 80 and days_since > 7:
            needs_review = True
            priority = "medium"
            reason = f"掌握度中等，已 {days_since} 天未复习"
        elif days_since > 14:
            needs_review = True
            priority = "medium"
            reason = f"已 {days_since} 天未复习，建议巩固"
        
        if needs_review:
            node = knowledge_graph.get(node_id, {})
            queue.append({
                "node_id": node_id,
                "name": node.get("name", {"zh": node_id}),
                "mastery": mastery,
                "days_since_practice": days_since,
                "priority": priority,
                "reason": reason
            })
    
    priority_order = {"high": 0, "medium": 1, "low": 2}
    queue.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["mastery"]))
    
    return queue[:limit]

# ===== API 路由处理函数 =====

async def get_knowledge_profile_handler(user_id: str, knowledge_graph: dict):
    """处理获取知识画像请求"""
    user_data = load_user_data(user_id)
    if not user_data:
        user_data = create_default_user(user_id)
        save_user_data(user_id, user_data)
    
    knowledge_state = user_data.get("knowledge_state", {})
    today = datetime.now()
    
    needs_review = 0
    for state in knowledge_state.values():
        mastery = state.get("mastery", 0)
        last_practice = state.get("last_practice", "")
        if last_practice:
            try:
                last_date = datetime.fromisoformat(last_practice)
                days_since = (today - last_date).days
                if (mastery < 50) or (mastery < 80 and days_since > 7) or (days_since > 14):
                    needs_review += 1
            except:
                pass
    
    summary = user_data.get("learning_summary", {})
    
    return {
        "user_id": user_id,
        "profile": user_data.get("profile", {}),
        "abilities": user_data.get("abilities", {}),
        "knowledge_state": knowledge_state,
        "stats": {
            "total_concepts": summary.get("total_concepts", 0),
            "mastered": summary.get("mastered_concepts", 0),
            "learning": summary.get("learning_concepts", 0),
            "weak": summary.get("weak_concepts", 0),
            "needs_review": needs_review
        },
        "learning_summary": summary,
        "weaknesses": user_data.get("weaknesses", []),
        "interests": user_data.get("interests", []),
        "achievements": user_data.get("achievements", [])
    }

async def get_review_queue_handler(user_id: str, knowledge_graph: dict, limit: int = 10):
    """处理获取复习队列请求"""
    queue = get_review_queue(user_id, knowledge_graph, limit)
    return {
        "user_id": user_id,
        "queue": queue,
        "total": len(queue),
        "estimated_time": len(queue) * 5
    }

async def record_learning_events_handler(user_id: str, events: List[LearningEvent]):
    """处理记录学习事件请求"""
    results = []
    
    for event in events:
        update = {
            "mastery": event.mastery_after or 0,
            "event_type": event.event_type
        }
        
        state = update_knowledge_state(user_id, event.node_id, update, event.source)
        results.append({
            "node_id": event.node_id,
            "success": True,
            "new_mastery": state.get("mastery", 0)
        })
    
    return {
        "user_id": user_id,
        "recorded": len(results),
        "results": results
    }

async def detailed_assessment_handler(user_id: str, assessments: List[DetailedAssessment]):
    """处理详细评估请求"""
    level_to_mastery = {
        0: (0, 39),
        1: (40, 69),
        2: (70, 89),
        3: (90, 100)
    }
    
    results = []
    for assessment in assessments:
        level = assessment.level
        min_mastery, max_mastery = level_to_mastery.get(level, (0, 100))
        
        user_data = load_user_data(user_id)
        existing = user_data.get("knowledge_state", {}).get(assessment.node_id, {}) if user_data else {}
        current_mastery = existing.get("mastery", 0)
        
        if current_mastery < min_mastery:
            new_mastery = min_mastery + 10
        elif current_mastery > max_mastery:
            new_mastery = max_mastery - 5
        else:
            new_mastery = min(current_mastery + 5, max_mastery)
        
        new_mastery = max(0, min(100, new_mastery))
        
        update = {
            "mastery": new_mastery,
            "event_type": "assessment",
            "notes": assessment.notes
        }
        
        state = update_knowledge_state(user_id, assessment.node_id, update, "web_sync")
        results.append({
            "node_id": assessment.node_id,
            "level": level,
            "new_mastery": new_mastery,
            "success": True
        })
    
    return {
        "user_id": user_id,
        "assessed": len(results),
        "results": results
    }

# 兼容层：将 known_nodes 风格评估转换为 knowledge_state
def convert_known_to_state(user_id: str, assessments: list, knowledge_graph: dict) -> dict:
    """将 known/unknown 评估转换为 knowledge_state 更新"""
    results = []
    
    for assessment in assessments:
        node_id = assessment.get("node_id") or assessment.get("nodeId")
        known = assessment.get("known", False)
        
        if known:
            update = {
                "mastery": 100,
                "event_type": "assess_known"
            }
        else:
            update = {
                "mastery": 0,
                "event_type": "assess_unknown"
            }
        
        state = update_knowledge_state(user_id, node_id, update, "web_sync")
        results.append({
            "node_id": node_id,
            "known": known,
            "new_mastery": state.get("mastery", 0)
        })
    
    # 获取更新后的汇总
    user_data = load_user_data(user_id)
    summary = user_data.get("learning_summary", {}) if user_data else {}
    
    return {
        "user_id": user_id,
        "updated_count": len(results),
        "current_level": user_data.get("profile", {}).get("grade", "小学四年级") if user_data else "小学四年级",
        "summary": {
            "total_known": summary.get("mastered_concepts", 0),
            "total_learning": summary.get("learning_concepts", 0),
            "total_weak": summary.get("weak_concepts", 0)
        },
        "results": results
    }

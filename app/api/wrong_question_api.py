"""
错题记录 API 模块
提供错题的保存、查询、复习等功能
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import uuid

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
WRONG_QUESTIONS_DIR = DATA_DIR / "wrong-questions"
WRONG_QUESTIONS_DIR.mkdir(exist_ok=True)

# 错误类型定义
ERROR_TYPES = {
    "concept_error": "概念理解错误",
    "calculation_error": "计算错误",
    "formula_error": "公式记错",
    "misunderstanding": "审题错误",
    "careless": "粗心大意",
    "wrong_approach": "思路错误",
    "confusion": "知识点混淆",
    "other": "其他"
}

# 艾宾浩斯复习间隔（天）
REVIEW_INTERVALS = [1, 3, 7, 14, 30]

# ===== 数据模型 =====

class QuestionInfo(BaseModel):
    """题目信息"""
    content: str
    type: str = "calculation"  # calculation, choice, fill_blank, etc.
    difficulty: int = 5
    source: str = "daily_lesson"

class ReviewSchedule(BaseModel):
    """复习计划"""
    stage: int = 1  # 1-5
    next_review: str = ""
    review_count: int = 0
    mastered: bool = False
    last_review: Optional[str] = None

class WrongQuestionCreate(BaseModel):
    """创建错题请求"""
    node_id: str
    question: QuestionInfo
    wrong_answer: str
    correct_answer: str
    error_type: str = "other"
    error_analysis: Optional[str] = None
    tags: List[str] = []
    related_concepts: List[str] = []

class WrongQuestionUpdate(BaseModel):
    """更新错题请求"""
    error_analysis: Optional[str] = None
    tags: Optional[List[str]] = None
    error_type: Optional[str] = None

class ReviewResult(BaseModel):
    """复习结果"""
    correct: bool
    notes: Optional[str] = None

class MasterMark(BaseModel):
    """标记掌握"""
    notes: Optional[str] = None

# ===== 数据操作函数 =====

def get_user_wrong_questions_file(user_id: str) -> Path:
    """获取用户错题文件路径"""
    return WRONG_QUESTIONS_DIR / f"{user_id}.json"

def load_user_wrong_questions(user_id: str) -> Dict:
    """加载用户错题数据"""
    file_path = get_user_wrong_questions_file(user_id)
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading wrong questions: {e}")
    return {
        "user_id": user_id,
        "total_count": 0,
        "active_count": 0,
        "mastered_count": 0,
        "wrong_questions": [],
        "updated_at": datetime.now().isoformat()
    }

def save_user_wrong_questions(user_id: str, data: Dict):
    """保存用户错题数据"""
    file_path = get_user_wrong_questions_file(user_id)
    data["updated_at"] = datetime.now().isoformat()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving wrong questions: {e}")

def calculate_next_review(stage: int) -> str:
    """计算下次复习时间"""
    if stage <= 0 or stage > len(REVIEW_INTERVALS):
        stage = 1
    
    days = REVIEW_INTERVALS[stage - 1]
    next_date = datetime.now() + timedelta(days=days)
    return next_date.isoformat()

def create_wrong_question(user_id: str, data: WrongQuestionCreate) -> Dict:
    """创建错题记录"""
    wq_id = f"wq_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    wrong_question = {
        "id": wq_id,
        "user_id": user_id,
        "node_id": data.node_id,
        "question": data.question.dict(),
        "wrong_answer": data.wrong_answer,
        "correct_answer": data.correct_answer,
        "error_type": data.error_type,
        "error_analysis": data.error_analysis or "",
        "tags": data.tags,
        "related_concepts": data.related_concepts,
        "created_at": now,
        "review_schedule": {
            "stage": 1,
            "next_review": calculate_next_review(1),
            "review_count": 0,
            "mastered": False,
            "last_review": None
        },
        "history": [
            {
                "date": now,
                "action": "created",
                "notes": "首次记录"
            }
        ]
    }
    
    # 加载并更新数据
    user_data = load_user_wrong_questions(user_id)
    user_data["wrong_questions"].append(wrong_question)
    user_data["total_count"] = len(user_data["wrong_questions"])
    user_data["active_count"] = sum(
        1 for wq in user_data["wrong_questions"] 
        if not wq["review_schedule"]["mastered"]
    )
    
    save_user_wrong_questions(user_id, user_data)
    
    return wrong_question

def get_wrong_question(user_id: str, wq_id: str) -> Optional[Dict]:
    """获取单个错题"""
    user_data = load_user_wrong_questions(user_id)
    for wq in user_data["wrong_questions"]:
        if wq["id"] == wq_id:
            return wq
    return None

def update_wrong_question(user_id: str, wq_id: str, update: WrongQuestionUpdate) -> Optional[Dict]:
    """更新错题"""
    user_data = load_user_wrong_questions(user_id)
    
    for wq in user_data["wrong_questions"]:
        if wq["id"] == wq_id:
            if update.error_analysis is not None:
                wq["error_analysis"] = update.error_analysis
            if update.tags is not None:
                wq["tags"] = update.tags
            if update.error_type is not None:
                wq["error_type"] = update.error_type
            
            wq["history"].append({
                "date": datetime.now().isoformat(),
                "action": "updated",
                "notes": "更新错题信息"
            })
            
            save_user_wrong_questions(user_id, user_data)
            return wq
    
    return None

def delete_wrong_question(user_id: str, wq_id: str) -> bool:
    """删除错题"""
    user_data = load_user_wrong_questions(user_id)
    
    original_len = len(user_data["wrong_questions"])
    user_data["wrong_questions"] = [
        wq for wq in user_data["wrong_questions"] 
        if wq["id"] != wq_id
    ]
    
    if len(user_data["wrong_questions"]) < original_len:
        user_data["total_count"] = len(user_data["wrong_questions"])
        user_data["active_count"] = sum(
            1 for wq in user_data["wrong_questions"] 
            if not wq["review_schedule"]["mastered"]
        )
        user_data["mastered_count"] = sum(
            1 for wq in user_data["wrong_questions"] 
            if wq["review_schedule"]["mastered"]
        )
        save_user_wrong_questions(user_id, user_data)
        return True
    
    return False

def record_review(user_id: str, wq_id: str, result: ReviewResult) -> Optional[Dict]:
    """记录复习结果"""
    user_data = load_user_wrong_questions(user_id)
    now = datetime.now().isoformat()
    
    for wq in user_data["wrong_questions"]:
        if wq["id"] == wq_id:
            schedule = wq["review_schedule"]
            schedule["review_count"] += 1
            schedule["last_review"] = now
            
            if result.correct:
                # 做对了，进入下一阶段
                schedule["stage"] += 1
                
                # 如果完成所有阶段，标记为掌握
                if schedule["stage"] > len(REVIEW_INTERVALS):
                    schedule["mastered"] = True
                    schedule["next_review"] = None
                else:
                    schedule["next_review"] = calculate_next_review(schedule["stage"])
            else:
                # 又错了，重置阶段
                schedule["stage"] = 1
                schedule["next_review"] = calculate_next_review(1)
            
            wq["history"].append({
                "date": now,
                "action": "reviewed",
                "correct": result.correct,
                "notes": result.notes or ""
            })
            
            # 更新统计
            user_data["active_count"] = sum(
                1 for w in user_data["wrong_questions"] 
                if not w["review_schedule"]["mastered"]
            )
            user_data["mastered_count"] = sum(
                1 for w in user_data["wrong_questions"] 
                if w["review_schedule"]["mastered"]
            )
            
            save_user_wrong_questions(user_id, user_data)
            return wq
    
    return None

def mark_as_mastered(user_id: str, wq_id: str, mark: MasterMark) -> Optional[Dict]:
    """标记错题为已掌握"""
    user_data = load_user_wrong_questions(user_id)
    now = datetime.now().isoformat()
    
    for wq in user_data["wrong_questions"]:
        if wq["id"] == wq_id:
            wq["review_schedule"]["mastered"] = True
            wq["review_schedule"]["next_review"] = None
            
            wq["history"].append({
                "date": now,
                "action": "mastered",
                "notes": mark.notes or "手动标记为已掌握"
            })
            
            # 更新统计
            user_data["active_count"] = sum(
                1 for w in user_data["wrong_questions"] 
                if not w["review_schedule"]["mastered"]
            )
            user_data["mastered_count"] = sum(
                1 for w in user_data["wrong_questions"] 
                if w["review_schedule"]["mastered"]
            )
            
            save_user_wrong_questions(user_id, user_data)
            return wq
    
    return None

def get_today_review_list(user_id: str) -> List[Dict]:
    """获取今日需要复习的错题"""
    user_data = load_user_wrong_questions(user_id)
    today = datetime.now()
    
    review_list = []
    for wq in user_data["wrong_questions"]:
        schedule = wq["review_schedule"]
        if schedule["mastered"]:
            continue
        
        next_review = schedule.get("next_review")
        if not next_review:
            continue
        
        try:
            next_date = datetime.fromisoformat(next_review)
            if next_date.date() <= today.date():
                review_list.append(wq)
        except:
            continue
    
    # 按阶段排序（先复习早期的）
    review_list.sort(key=lambda x: x["review_schedule"]["stage"])
    
    return review_list

def get_wrong_questions_list(
    user_id: str, 
    status: str = "all",
    node_id: Optional[str] = None,
    error_type: Optional[str] = None,
    needs_review: bool = False,
    limit: int = 50
) -> Dict:
    """获取错题列表"""
    user_data = load_user_wrong_questions(user_id)
    questions = user_data["wrong_questions"]
    
    # 按状态筛选
    if status == "active":
        questions = [q for q in questions if not q["review_schedule"]["mastered"]]
    elif status == "mastered":
        questions = [q for q in questions if q["review_schedule"]["mastered"]]
    
    # 按知识点筛选
    if node_id:
        questions = [q for q in questions if q["node_id"] == node_id]
    
    # 按错误类型筛选
    if error_type:
        questions = [q for q in questions if q["error_type"] == error_type]
    
    # 按需要复习筛选
    if needs_review:
        today = datetime.now()
        filtered = []
        for q in questions:
            next_review = q["review_schedule"].get("next_review")
            if next_review:
                try:
                    next_date = datetime.fromisoformat(next_review)
                    if next_date.date() <= today.date():
                        filtered.append(q)
                except:
                    pass
        questions = filtered
    
    # 限制数量
    questions = questions[:limit]
    
    # 计算今日需要复习的数量
    today_count = len(get_today_review_list(user_id))
    
    return {
        "user_id": user_id,
        "total": user_data["total_count"],
        "active": user_data["active_count"],
        "mastered": user_data["mastered_count"],
        "needs_review_today": today_count,
        "returned": len(questions),
        "wrong_questions": questions
    }

def get_wrong_question_stats(user_id: str) -> Dict:
    """获取错题统计"""
    user_data = load_user_wrong_questions(user_id)
    questions = user_data["wrong_questions"]
    
    # 按错误类型统计
    by_error_type = {}
    for q in questions:
        et = q.get("error_type", "other")
        by_error_type[et] = by_error_type.get(et, 0) + 1
    
    # 按知识点统计
    by_node = {}
    for q in questions:
        node = q.get("node_id", "unknown")
        by_node[node] = by_node.get(node, 0) + 1
    
    # 计算掌握率
    total = len(questions)
    mastered = sum(1 for q in questions if q["review_schedule"]["mastered"])
    mastery_rate = mastered / total if total > 0 else 0
    
    # 本周趋势
    weekly_trend = {}
    now = datetime.now()
    for i in range(4):
        week_start = now - timedelta(days=now.weekday() + i * 7)
        week_key = week_start.strftime("%Y-W%W")
        weekly_trend[week_key] = 0
    
    for q in questions:
        try:
            created = datetime.fromisoformat(q["created_at"])
            week_key = created.strftime("%Y-W%W")
            if week_key in weekly_trend:
                weekly_trend[week_key] += 1
        except:
            pass
    
    return {
        "user_id": user_id,
        "total_wrong": total,
        "active": user_data["active_count"],
        "mastered": user_data["mastered_count"],
        "by_error_type": by_error_type,
        "by_node": by_node,
        "weekly_trend": [{"week": k, "count": v} for k, v in sorted(weekly_trend.items())],
        "mastery_rate": round(mastery_rate, 2),
        "needs_review_today": len(get_today_review_list(user_id))
    }

# ===== API 路由处理函数 =====

@router.post("/{user_id}/wrong-questions")
async def create_wrong_question_handler(user_id: str, data: WrongQuestionCreate):
    """处理创建错题请求"""
    wrong_question = create_wrong_question(user_id, data)
    return {
        "success": True,
        "wrong_question_id": wrong_question["id"],
        "next_review": wrong_question["review_schedule"]["next_review"],
        "message": f"错题已记录，将在{REVIEW_INTERVALS[0]}天后提醒复习"
    }

@router.get("/debug-routes")
async def debug_routes():
    """调试路由"""
    # app will be imported at runtime if needed
    routes = []
    for r in main_app.routes:
        if hasattr(r, 'path'):
            methods = getattr(r, 'methods', {'?'})
            routes.append(f"{list(methods)} {r.path}")
    return {"total": len(routes), "routes": routes}

@router.get("/{user_id}/wrong-questions")
async def get_wrong_questions_handler(
    user_id: str,
    status: str = "all",
    node_id: Optional[str] = None,
    error_type: Optional[str] = None,
    needs_review: bool = False,
    limit: int = 50
):
    """处理获取错题列表请求"""
    return get_wrong_questions_list(user_id, status, node_id, error_type, needs_review, limit)

@router.get("/{user_id}/wrong-questions/today-review")
async def get_today_review_handler(user_id: str):
    """处理获取今日复习列表请求"""
    review_list = get_today_review_list(user_id)
    return {
        "user_id": user_id,
        "total": len(review_list),
        "estimated_time": len(review_list) * 5,  # 假设每题5分钟
        "wrong_questions": review_list
    }

@router.post("/{user_id}/wrong-questions/{wq_id}/review")
async def record_review_handler(user_id: str, wq_id: str, result: ReviewResult):
    """处理记录复习请求"""
    wq = record_review(user_id, wq_id, result)
    if not wq:
        raise HTTPException(status_code=404, detail="Wrong question not found")
    
    schedule = wq["review_schedule"]
    if schedule["mastered"]:
        message = "恭喜！此错题已完全掌握"
    else:
        days = REVIEW_INTERVALS[min(schedule["stage"] - 1, len(REVIEW_INTERVALS) - 1)]
        message = f"复习记录已保存，将在{days}天后再次提醒"
    
    return {
        "success": True,
        "mastered": schedule["mastered"],
        "stage": schedule["stage"],
        "next_review": schedule["next_review"],
        "message": message
    }

@router.post("/{user_id}/wrong-questions/{wq_id}/master")
async def mark_mastered_handler(user_id: str, wq_id: str, mark: MasterMark):
    """处理标记掌握请求"""
    wq = mark_as_mastered(user_id, wq_id, mark)
    if not wq:
        raise HTTPException(status_code=404, detail="Wrong question not found")
    
    return {
        "success": True,
        "mastered": True,
        "message": "已标记为已掌握"
    }

@router.get("/{user_id}/wrong-questions/stats")
async def get_stats_handler(user_id: str):
    """处理获取统计请求"""
    return get_wrong_question_stats(user_id)

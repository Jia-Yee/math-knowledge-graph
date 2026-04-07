from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Set
import json
import os
from pathlib import Path

app = FastAPI(title="Math Knowledge Graph API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加静态文件服务
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 提供前端静态文件
WEB_DIR = Path(__file__).parent.parent / "web"

@app.get("/web")
async def web_index():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/admin")
async def admin_index():
    return FileResponse(WEB_DIR / "admin.html")

# 根路由重定向到 Web 页面
@app.get("/")
async def root():
    return FileResponse(WEB_DIR / "index.html")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# 数据路径
DATA_DIR = Path(__file__).parent.parent.parent / "data"
NODES_FILE = DATA_DIR / "core-nodes.json"

# 数据模型
class KnowledgeNode(BaseModel):
    id: str
    type: str
    name: Dict[str, str]
    description: Dict[str, str]
    level: str
    branch: str
    tags: List[str]
    prerequisites: List[str]
    difficulty: int
    importance: int
    estimated_minutes: int

class UserAssessment(BaseModel):
    node_id: str
    known: bool

class UserProfile(BaseModel):
    user_id: str
    known_nodes: Set[str] = set()
    unknown_nodes: Set[str] = set()
    current_level: str = "primary"

class AssessmentRequest(BaseModel):
    user_id: str
    assessments: List[UserAssessment]

class LearningPathRequest(BaseModel):
    user_id: str
    target_node_id: Optional[str] = None
    max_nodes: int = 10

# 全局数据存储
knowledge_graph: Dict[str, dict] = {}
user_profiles: Dict[str, UserProfile] = {}

# 用户数据文件路径
USER_DATA_FILE = DATA_DIR / "user-profiles.json"

# 学习阶段顺序
LEVEL_ORDER = ["primary", "junior", "senior", "undergrad", "master", "phd", "research"]

def get_node_level(node: dict) -> str:
    """从节点数据中获取学习阶段级别"""
    # 1. 优先使用 education_level 字段
    level = node.get('education_level', '')
    if level and level in LEVEL_ORDER:
        return level
    
    # 2. 检查 level 字段（可能是字符串如 'primary' 或数字 1-18）
    level_val = node.get('level', 0)
    
    # 如果是字符串
    if isinstance(level_val, str):
        level_lower = level_val.lower()
        if level_lower in LEVEL_ORDER:
            return level_lower
        # 处理特殊格式如 '小学primary', '初中junior', 'j8b', 'h10b'
        for lo in LEVEL_ORDER:
            if lo in level_lower:
                return lo
        # 小学/初中/高中 关键词
        if '小学' in level_val:
            return 'primary'
        elif '初中' in level_val or '初' in level_val:
            return 'junior'
        elif '高中' in level_val or '高' in level_val:
            return 'senior'
        elif '大学' in level_val or '本科' in level_val:
            return 'undergrad'
        elif '硕士' in level_val or '研究' in level_val:
            return 'master'
        elif '博士' in level_val:
            return 'phd'
    
    # 3. 如果是数字，根据年级判断
    if isinstance(level_val, (int, float)):
        if level_val <= 6:
            return 'primary'
        elif level_val <= 9:
            return 'junior'
        elif level_val <= 12:
            return 'senior'
        elif level_val <= 16:
            return 'undergrad'
        elif level_val <= 18:
            return 'master'
        else:
            return 'phd'
    
    # 4. 从 grade 或 level_str 推断
    grade = node.get('grade', '') or ''
    level_str = node.get('level_str', '') or ''
    
    for text in [grade, level_str]:
        if not text:
            continue
        if '小学' in text or 'primary' in text.lower():
            return 'primary'
        elif '初中' in text or 'junior' in text.lower() or 'j' in text[:2].lower():
            return 'junior'
        elif '高中' in text or 'senior' in text.lower() or 's' in text[:2].lower():
            return 'senior'
        elif '大学' in text or 'undergrad' in text.lower() or '本科' in text:
            return 'undergrad'
        elif '硕士' in text or 'master' in text.lower():
            return 'master'
        elif '博士' in text or 'phd' in text.lower():
            return 'phd'
    
    # 5. 从 branch 推断
    branch = node.get('branch', '').lower()
    if branch in LEVEL_ORDER:
        return branch
    
    # 6. 默认返回 primary
    return 'primary'

# 全局边数据
knowledge_graph_edges = []

def load_data():
    """加载知识图谱数据"""
    global knowledge_graph, knowledge_graph_edges
    if NODES_FILE.exists():
        with open(NODES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                knowledge_graph[node['id']] = node
            # 加载边数据
            knowledge_graph_edges = data.get('edges', [])
    print(f"Loaded {len(knowledge_graph)} knowledge nodes")
    print(f"Loaded {len(knowledge_graph_edges)} knowledge edges")
    load_user_profiles()

def load_user_profiles():
    """加载用户数据"""
    global user_profiles
    if USER_DATA_FILE.exists():
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_id, profile_data in data.items():
                    user_profiles[user_id] = UserProfile(
                        user_id=user_id,
                        known_nodes=set(profile_data.get('known_nodes', [])),
                        unknown_nodes=set(profile_data.get('unknown_nodes', [])),
                        current_level=profile_data.get('current_level', 'primary')
                    )
            print(f"Loaded {len(user_profiles)} user profiles")
        except Exception as e:
            print(f"Failed to load user profiles: {e}")

def save_user_profiles():
    """保存用户数据"""
    try:
        data = {}
        for user_id, profile in user_profiles.items():
            data[user_id] = {
                'known_nodes': list(profile.known_nodes),
                'unknown_nodes': list(profile.unknown_nodes),
                'current_level': profile.current_level
            }
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(user_profiles)} user profiles")
    except Exception as e:
        print(f"Failed to save user profiles: {e}")

def get_nodes_by_level(level: str) -> List[dict]:
    """获取指定级别的所有节点"""
    return [node for node in knowledge_graph.values() if get_node_level(node) == level]

def get_node_prerequisites(node_id: str) -> List[str]:
    """获取节点的所有前置依赖（递归）"""
    prereqs = set()
    node = knowledge_graph.get(node_id)
    if not node:
        return []
    
    def collect_prereqs(nid: str, visited: Set[str]):
        if nid in visited:
            return
        visited.add(nid)
        n = knowledge_graph.get(nid)
        if n:
            for prereq in n.get('prerequisites', []):
                prereqs.add(prereq)
                collect_prereqs(prereq, visited)
    
    collect_prereqs(node_id, set())
    return list(prereqs)

def can_learn_node(node_id: str, known_nodes: Set[str]) -> bool:
    """检查用户是否可以学习某个节点（所有前置知识已掌握）"""
    node = knowledge_graph.get(node_id)
    if not node:
        return False
    prereqs = set(node.get('prerequisites', []))
    return prereqs.issubset(known_nodes)

def get_recommended_nodes(user_profile: UserProfile, max_nodes: int = 10) -> List[dict]:
    """基于用户知识掌握情况推荐学习节点"""
    known = user_profile.known_nodes
    recommendations = []
    
    # 找到所有可以学习的节点（前置知识已满足）
    learnable = []
    for node_id, node in knowledge_graph.items():
        if node_id in known or node_id in user_profile.unknown_nodes:
            continue
        if can_learn_node(node_id, known):
            learnable.append(node)
    
    # 按难度和重要性排序
    learnable.sort(key=lambda x: (x['difficulty'], -x['importance']))
    
    # 优先推荐当前级别及相邻级别的内容
    current_idx = LEVEL_ORDER.index(user_profile.current_level) if user_profile.current_level in LEVEL_ORDER else 0
    
    for node in learnable:
        node_level_idx = LEVEL_ORDER.index(get_node_level(node)) if get_node_level(node) in LEVEL_ORDER else 0
        level_distance = abs(node_level_idx - current_idx)
        
        # 添加级别距离信息用于排序
        node['_level_distance'] = level_distance
    
    # 重新排序：优先推荐当前级别附近的内容
    learnable.sort(key=lambda x: (x['_level_distance'], x['difficulty'], -x['importance']))
    
    return learnable[:max_nodes]

def get_learning_path_to_target(user_profile: UserProfile, target_node_id: str) -> List[dict]:
    """生成到达目标节点的学习路径"""
    if target_node_id not in knowledge_graph:
        return []
    
    known = user_profile.known_nodes
    
    # 获取目标节点的所有前置依赖
    prereqs = get_node_prerequisites(target_node_id)
    
    # 找出还未掌握的前置知识
    missing_prereqs = [p for p in prereqs if p not in known]
    
    # 按依赖关系排序（拓扑排序简化版）
    path_nodes = []
    for prereq_id in missing_prereqs:
        node = knowledge_graph.get(prereq_id)
        if node:
            path_nodes.append(node)
    
    # 最后加上目标节点
    if target_node_id not in known:
        path_nodes.append(knowledge_graph[target_node_id])
    
    # 按难度排序
    path_nodes.sort(key=lambda x: (LEVEL_ORDER.index(x['level']) if x['level'] in LEVEL_ORDER else 0, x['difficulty']))
    
    return path_nodes

@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/")
async def root():
    return {"message": "Math Knowledge Graph API", "version": "1.0.0"}

@app.get("/levels")
async def get_levels():
    """获取所有学习阶段"""
    return {
        "levels": [
            {"id": "primary", "name": "小学", "order": 0},
            {"id": "junior", "name": "初中", "order": 1},
            {"id": "senior", "name": "高中", "order": 2},
            {"id": "undergrad", "name": "本科", "order": 3},
            {"id": "master", "name": "硕士", "order": 4},
            {"id": "phd", "name": "博士", "order": 5},
            {"id": "research", "name": "研究", "order": 6}
        ]
    }

@app.get("/edges")
async def get_edges(type: str = None, from_node: str = None, to_node: str = None, limit: int = 1000):
    """获取所有边/关系"""
    global knowledge_graph_edges
    
    edges = knowledge_graph_edges
    
    # 按类型筛选
    if type:
        edges = [e for e in edges if e.get('type') == type]
    
    # 按起始节点筛选
    if from_node:
        edges = [e for e in edges if e.get('from') == from_node]
    
    # 按目标节点筛选
    if to_node:
        edges = [e for e in edges if e.get('to') == to_node]
    
    # 限制数量
    edges = edges[:limit]
    
    return {
        "edges": edges,
        "total": len(edges)
    }

@app.get("/nodes/{node_id}/edges")
async def get_node_edges(node_id: str):
    """获取某个节点的所有边"""
    global knowledge_graph_edges
    
    edges = [e for e in knowledge_graph_edges 
             if e.get('from') == node_id or e.get('to') == node_id]
    
    return {
        "node_id": node_id,
        "edges": edges,
        "total": len(edges)
    }

@app.get("/nodes")
async def get_nodes(level: Optional[str] = None, branch: Optional[str] = None, limit: Optional[int] = 50000, for_graph: bool = False):
    """获取知识节点列表"""
    nodes = list(knowledge_graph.values())
    
    if level:
        nodes = [n for n in nodes if get_node_level(n) == level]
    if branch:
        nodes = [n for n in nodes if n['branch'] == branch]
    
    # 知识图谱视图需要更多节点（至少50个）
    if for_graph:
        limit = max(limit, 50)
    
    # 限制返回数量
    nodes = nodes[:limit]
    
    return {"nodes": nodes, "total": len(nodes)}

@app.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """获取单个知识节点详情"""
    if node_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = knowledge_graph[node_id]
    
    # 获取前置知识详情
    prereq_details = []
    for prereq_id in node.get('prerequisites', []):
        if prereq_id in knowledge_graph:
            prereq_details.append({
                "id": prereq_id,
                "name": knowledge_graph[prereq_id]['name']
            })
    
    # 获取后续知识（哪些节点依赖这个）
    next_nodes = []
    for nid, n in knowledge_graph.items():
        if node_id in n.get('prerequisites', []):
            next_nodes.append({
                "id": nid,
                "name": n['name']
            })
    
    return {
        "node": node,
        "prerequisites": prereq_details,
        "next_nodes": next_nodes
    }

@app.get("/branches")
async def get_branches():
    """获取所有数学分支"""
    branches = {}
    for node in knowledge_graph.values():
        branch = node['branch']
        if branch not in branches:
            branches[branch] = {"id": branch, "count": 0}
        branches[branch]["count"] += 1
    
    return {"branches": list(branches.values())}

@app.post("/users/{user_id}/assess")
async def assess_knowledge(user_id: str, request: AssessmentRequest):
    """评估用户知识掌握情况"""
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile(user_id=user_id)
    
    profile = user_profiles[user_id]
    
    for assessment in request.assessments:
        if assessment.known:
            profile.known_nodes.add(assessment.node_id)
            profile.unknown_nodes.discard(assessment.node_id)
        else:
            profile.unknown_nodes.add(assessment.node_id)
            profile.known_nodes.discard(assessment.node_id)
    
    # 更新用户当前级别（基于已掌握的最高级别）
    max_level_idx = 0
    for node_id in profile.known_nodes:
        node = knowledge_graph.get(node_id)
        if node:
            # 使用 education_level 或 grade 字段映射到 LEVEL_ORDER
            node_level = node.get('education_level', '')
            if not node_level:
                # 从 grade 字段推断
                grade = node.get('grade', '') or ''
                if '小学' in grade:
                    node_level = 'primary'
                elif '初中' in grade:
                    node_level = 'junior'
                elif '高中' in grade:
                    node_level = 'senior'
                elif '大学' in grade or '本科' in grade:
                    node_level = 'undergrad'
                else:
                    node_level = 'primary'
            level_idx = LEVEL_ORDER.index(node_level) if node_level in LEVEL_ORDER else 0
            max_level_idx = max(max_level_idx, level_idx)
    
    # 如果掌握了当前级别 60% 以上内容，提升到下一级别
    current_level = LEVEL_ORDER[max_level_idx]
    
    # 计算当前级别的节点
    current_level_nodes = []
    for n in knowledge_graph.values():
        n_level = n.get('education_level', '')
        if not n_level:
            grade = n.get('grade', '') or ''
            if '小学' in grade:
                n_level = 'primary'
            elif '初中' in grade:
                n_level = 'junior'
            elif '高中' in grade:
                n_level = 'senior'
            elif '大学' in grade or '本科' in grade:
                n_level = 'undergrad'
            else:
                n_level = 'primary'
        if n_level == current_level:
            current_level_nodes.append(n)
    
    known_in_level = len([n for n in current_level_nodes if n['id'] in profile.known_nodes])
    
    if current_level_nodes and known_in_level / len(current_level_nodes) >= 0.6:
        if max_level_idx + 1 < len(LEVEL_ORDER):
            profile.current_level = LEVEL_ORDER[max_level_idx + 1]
        else:
            profile.current_level = current_level
    else:
        profile.current_level = current_level
    
    # 保存用户数据
    save_user_profiles()
    
    return {
        "user_id": user_id,
        "known_count": len(profile.known_nodes),
        "unknown_count": len(profile.unknown_nodes),
        "current_level": profile.current_level
    }

@app.get("/users")
async def list_users(limit: int = 10):
    """获取用户列表（测试用）"""
    users = list(user_profiles.values())
    
    # 限制返回数量
    users = users[:limit]
    
    return {
        "users": [
            {
                "user_id": u.user_id,
                "current_level": u.current_level,
                "known_count": len(u.known_nodes),
                "unknown_count": len(u.unknown_nodes)
            }
            for u in users
        ],
        "total": len(user_profiles),
        "returned": len(users)
    }

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """获取用户知识画像"""
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile(user_id=user_id)
    
    profile = user_profiles[user_id]
    
    # 统计各阶段掌握情况
    level_stats = {}
    for level in LEVEL_ORDER:
        level_nodes = [n for n in knowledge_graph.values() if get_node_level(n) == level]
        known_in_level = len([n for n in level_nodes if n['id'] in profile.known_nodes])
        level_stats[level] = {
            "total": len(level_nodes),
            "known": known_in_level,
            "percentage": round(known_in_level / len(level_nodes) * 100, 1) if level_nodes else 0
        }
    
    return {
        "user_id": user_id,
        "current_level": profile.current_level,
        "known_nodes_count": len(profile.known_nodes),
        "unknown_nodes_count": len(profile.unknown_nodes),
        "level_progress": level_stats,
        "known_nodes": list(profile.known_nodes)
    }

@app.post("/users/{user_id}/recommend")
async def recommend_learning(user_id: str, request: LearningPathRequest):
    """推荐学习内容"""
    if user_id not in user_profiles:
        user_profiles[user_id] = UserProfile(user_id=user_id)
    
    profile = user_profiles[user_id]
    
    if request.target_node_id:
        # 生成到达目标的学习路径
        path = get_learning_path_to_target(profile, request.target_node_id)
        return {
            "type": "path_to_target",
            "target": knowledge_graph.get(request.target_node_id, {}).get('name', {}),
            "nodes": path,
            "total_steps": len(path)
        }
    else:
        # 推荐下一步学习内容
        recommendations = get_recommended_nodes(profile, request.max_nodes)
        return {
            "type": "next_learning",
            "current_level": profile.current_level,
            "recommendations": recommendations,
            "total": len(recommendations)
        }

@app.get("/assessment/questions")
async def get_assessment_questions(level: str, limit: int = 10):
    """获取评估问题（指定级别的知识点）"""
    nodes = get_nodes_by_level(level)
    
    # 按重要性排序，优先评估重要知识点
    nodes.sort(key=lambda x: -x['importance'])
    
    selected = nodes[:limit]
    
    return {
        "level": level,
        "questions": [
            {
                "node_id": n['id'],
                "name": n['name'],
                "description": n['description'],
                "difficulty": n['difficulty'],
                "branch": n['branch'],
                "level": get_node_level(n)
            }
            for n in selected
        ],
        "total": len(selected)
    }

# ===== 后台管理 API =====

# 数据模型
class NodeCreate(BaseModel):
    id: str
    name: Dict[str, str]
    type: str = "concept"
    branch: str
    education_level: Optional[str] = None
    grade: Optional[str] = None
    description: Dict[str, str] = {}
    tags: List[str] = []
    prerequisites: List[str] = []
    difficulty: int = 5
    importance: int = 5
    estimated_minutes: int = 60

class NodeUpdate(BaseModel):
    name: Optional[Dict[str, str]] = None
    type: Optional[str] = None
    branch: Optional[str] = None
    education_level: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    difficulty: Optional[int] = None
    importance: Optional[int] = None
    estimated_minutes: Optional[int] = None

class RelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = "prerequisite"

@app.post("/admin/nodes")
async def create_node(node: NodeCreate):
    """创建新节点"""
    if node.id in knowledge_graph:
        raise HTTPException(status_code=400, detail="Node ID already exists")
    
    # 构建新节点
    new_node = {
        "id": node.id,
        "name": node.name,
        "type": node.type,
        "branch": node.branch,
        "description": node.description,
        "tags": node.tags or [],
        "prerequisites": node.prerequisites or [],
        "difficulty": node.difficulty,
        "importance": node.importance,
        "estimated_minutes": node.estimated_minutes
    }
    
    if node.education_level:
        new_node["education_level"] = node.education_level
    if node.grade:
        new_node["grade"] = node.grade
    
    knowledge_graph[node.id] = new_node
    
    # 保存到文件
    save_nodes()
    
    return {"success": True, "node": new_node}

@app.put("/admin/nodes/{node_id}")
async def update_node(node_id: str, update: NodeUpdate):
    """更新节点"""
    if node_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = knowledge_graph[node_id]
    
    # 更新字段
    if update.name is not None:
        node["name"] = update.name
    if update.type is not None:
        node["type"] = update.type
    if update.branch is not None:
        node["branch"] = update.branch
    if update.education_level is not None:
        node["education_level"] = update.education_level
    if update.grade is not None:
        node["grade"] = update.grade
    if update.description is not None:
        node["description"] = update.description
    if update.tags is not None:
        node["tags"] = update.tags
    if update.prerequisites is not None:
        node["prerequisites"] = update.prerequisites
    if update.difficulty is not None:
        node["difficulty"] = update.difficulty
    if update.importance is not None:
        node["importance"] = update.importance
    if update.estimated_minutes is not None:
        node["estimated_minutes"] = update.estimated_minutes
    
    # 保存到文件
    save_nodes()
    
    return {"success": True, "node": node}

@app.delete("/admin/nodes/{node_id}")
async def delete_node(node_id: str):
    """删除节点"""
    if node_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # 删除节点
    del knowledge_graph[node_id]
    
    # 清理其他节点的引用
    for nid, node in knowledge_graph.items():
        if node_id in node.get("prerequisites", []):
            node["prerequisites"].remove(node_id)
    
    # 保存到文件
    save_nodes()
    
    return {"success": True, "message": f"Node {node_id} deleted"}

@app.post("/admin/relations")
async def create_relation(relation: RelationCreate):
    """创建节点关系"""
    if relation.source_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Source node not found")
    if relation.target_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Target node not found")
    
    source_node = knowledge_graph[relation.source_id]
    
    if relation.relation_type == "prerequisite":
        if relation.target_id not in source_node.get("prerequisites", []):
            source_node.setdefault("prerequisites", []).append(relation.target_id)
    
    # 保存到文件
    save_nodes()
    
    return {"success": True, "message": f"Added {relation.relation_type} relation"}

@app.delete("/admin/relations")
async def delete_relation(source_id: str, target_id: str, relation_type: str = "prerequisite"):
    """删除节点关系"""
    if source_id not in knowledge_graph:
        raise HTTPException(status_code=404, detail="Source node not found")
    
    source_node = knowledge_graph[source_id]
    
    if relation_type == "prerequisite" and target_id in source_node.get("prerequisites", []):
        source_node["prerequisites"].remove(target_id)
    
    # 保存到文件
    save_nodes()
    
    return {"success": True, "message": f"Removed {relation_type} relation"}

@app.get("/admin/stats")
async def get_admin_stats():
    """获取知识图谱统计"""
    # 按年级统计（优先使用grade字段）
    grade_counts = {}
    for node in knowledge_graph.values():
        grade = node.get("grade", "")
        if grade:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        else:
            # 兼容：从tags中提取年级
            for tag in node.get("tags", []):
                if "小学" in tag or "初中" in tag or "高中" in tag or "大学" in tag:
                    grade_counts[tag] = grade_counts.get(tag, 0) + 1
    
    # 按分支统计
    branch_counts = {}
    for node in knowledge_graph.values():
        branch = node.get("branch", "other")
        branch_counts[branch] = branch_counts.get(branch, 0) + 1
    
    # 关系统计
    total_prereqs = sum(len(n.get("prerequisites", [])) for n in knowledge_graph.values())
    
    return {
        "total_nodes": len(knowledge_graph),
        "grade_distribution": grade_counts,
        "branch_distribution": branch_counts,
        "total_relations": total_prereqs
    }

@app.get("/admin/search")
async def search_nodes(q: str, limit: int = 20):
    """搜索节点"""
    q_lower = q.lower()
    results = []
    
    for node in knowledge_graph.values():
        # 搜索名称
        name_zh = node.get("name", {}).get("zh", "").lower()
        name_en = node.get("name", {}).get("en", "").lower()
        desc_zh = node.get("description", {}).get("zh", "").lower()
        
        if q_lower in name_zh or q_lower in name_en or q_lower in desc_zh:
            results.append({
                "id": node["id"],
                "name": node["name"],
                "branch": node.get("branch"),
                "type": node.get("type")
            })
    
    return {"results": results[:limit], "total": len(results)}

def save_nodes():
    """保存节点到文件"""
    nodes_list = list(knowledge_graph.values())
    with open(NODES_FILE, 'w', encoding='utf-8') as f:
        json.dump({"nodes": nodes_list}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(nodes_list)} nodes to file")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)

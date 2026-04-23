"""
学习路径推荐 API
基于用户已掌握的知识，推荐下一步学习内容
"""

import sys
sys.path.insert(0, '/Users/jia/.qclaw/workspace/math-knowledge-graph')

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path
import json

from app.api.database import get_db
from app.api.models_user import User, UserKnowledge
from app.api.auth_api import get_current_user

router = APIRouter(prefix="/learning-path", tags=["learning-path"])

# 加载知识图谱数据
DATA_DIR = Path('/Users/jia/.qclaw/workspace/math-knowledge-graph/data')
NODES_FILE = DATA_DIR / 'nodes-index.json'  # 轻量索引文件

# 全局缓存
_nodes_cache = None

def load_nodes():
    """加载知识图谱节点索引"""
    global _nodes_cache
    if _nodes_cache is None:
        with open(NODES_FILE, 'r', encoding='utf-8') as f:
            _nodes_cache = json.load(f)
    return _nodes_cache

def get_prereq_ids(node: dict) -> List[str]:
    """获取节点的前置知识 ID"""
    prereqs = node.get('prerequisites', [])
    if isinstance(prereqs, list):
        return [p for p in prereqs if p]
    return []

def get_suitable_nodes(user_known_ids: set, target_level: str, limit: int = 10) -> List[dict]:
    """
    找出适合用户学习的节点
    条件：
    1. 用户尚未掌握
    2. 所有前置知识都已掌握
    3. 难度在用户当前水平范围内
    """
    nodes = load_nodes()
    
    recommendations = []
    
    for node in nodes:
        node_id = node.get('id', '')
        
        # 跳过已掌握的
        if node_id in user_known_ids:
            continue
        
        # 获取前置知识
        prereq_ids = get_prereq_ids(node)
        
        # 检查前置知识是否都已掌握
        missing_prereqs = [p for p in prereq_ids if p and p not in user_known_ids]
        
        if missing_prereqs:
            # 有未掌握的前置知识
            # 找到这些前置知识的节点
            prereq_nodes = [n for n in nodes if n.get('id') in missing_prereqs]
            recommendations.append({
                'node': node,
                'status': 'blocked',
                'missing_prerequisites': [
                    {'id': p.get('id'), 'name': p.get('name', {}).get('zh', p.get('id'))}
                    for p in prereq_nodes
                ],
                'block_reason': f"需要先学习 {len(missing_prereqs)} 个前置知识"
            })
        else:
            # 可以学习
            recommendations.append({
                'node': node,
                'status': 'ready',
                'missing_prerequisites': []
            })
    
    # 排序
    # 1. ready 状态的优先
    # 2. 按难度排序
    ready = [r for r in recommendations if r['status'] == 'ready']
    blocked = [r for r in recommendations if r['status'] == 'blocked']
    
    ready.sort(key=lambda x: (
        -x['node'].get('importance', 5),  # 重要性高的优先
        x['node'].get('difficulty', 3)     # 难度低的优先
    ))
    
    blocked.sort(key=lambda x: len(x['missing_prerequisites']))  # 前置知识少的优先
    
    return ready[:limit] + blocked[:limit]

# ==================== API 模型 ====================

class RecommendedNode(BaseModel):
    node_id: str
    name: str
    type: str
    level: str
    branch: str
    difficulty: int
    importance: int
    estimated_minutes: int
    status: str  # ready / blocked
    block_reason: Optional[str] = None
    missing_prerequisites: List[Dict[str, str]] = []

class LearningPathResponse(BaseModel):
    ready_to_learn: List[RecommendedNode]
    next_challenges: List[RecommendedNode]
    current_level: str
    total_ready: int
    total_blocked: int

class PrerequisiteChain(BaseModel):
    node_id: str
    name: str
    chain: List[str]  # 完整的学习链

# ==================== API 端点 ====================

@router.get("/recommendations", response_model=LearningPathResponse)
async def get_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取学习推荐
    
    - ready_to_learn: 可以直接学习的节点
    - next_challenges: 有挑战的节点（需要先学前置知识）
    """
    # 获取用户已掌握的知识点
    known_records = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.status == 'known'
    ).all()
    
    user_known_ids = {r.node_id for r in known_records}
    
    # 获取推荐
    recommendations = get_suitable_nodes(user_known_ids, current_user.current_level or 'primary', limit)
    
    ready = [r for r in recommendations if r['status'] == 'ready']
    blocked = [r for r in recommendations if r['status'] == 'blocked']
    
    def format_node(r: dict) -> RecommendedNode:
        node = r['node']
        return RecommendedNode(
            node_id=node.get('id', ''),
            name=node.get('name_zh', node.get('id', '')),
            type=node.get('type', 'concept'),
            level=node.get('grade', '未知'),
            branch=node.get('branch', 'other'),
            difficulty=node.get('difficulty', 3),
            importance=node.get('importance', 5),
            estimated_minutes=node.get('estimated_minutes', 30),
            status=r['status'],
            block_reason=r.get('block_reason'),
            missing_prerequisites=r.get('missing_prerequisites', [])
        )
    
    return LearningPathResponse(
        ready_to_learn=[format_node(r) for r in ready],
        next_challenges=[format_node(r) for r in blocked],
        current_level=current_user.current_level or 'primary',
        total_ready=len(ready),
        total_blocked=len(blocked)
    )

@router.get("/prerequisites/{node_id}")
async def get_prerequisite_chain(
    node_id: str,
    depth: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取某个节点的完整前置知识链
    
    返回学习该节点需要先掌握的所有知识点的链式结构
    """
    nodes = load_nodes()
    node_map = {n.get('id'): n for n in nodes}
    
    # 获取用户已掌握的知识点
    known_records = db.query(UserKnowledge).filter(
        UserKnowledge.user_id == current_user.id,
        UserKnowledge.status == 'known'
    ).all()
    
    user_known_ids = {r.node_id for r in known_records}
    
    def build_chain(node_id: str, visited: set, current_depth: int) -> Dict:
        if node_id in visited or current_depth <= 0:
            return None
        
        visited.add(node_id)
        node = node_map.get(node_id)
        if not node:
            return None
        
        prereqs = get_prereq_ids(node)
        
        result = {
            'id': node_id,
            'name': node.get('name_zh', node_id),
            'is_known': node_id in user_known_ids,
            'children': []
        }
        
        for prereq_id in prereqs:
            if prereq_id and prereq_id not in visited:
                child = build_chain(prereq_id, visited.copy(), current_depth - 1)
                if child:
                    result['children'].append(child)
        
        return result
    
    chain = build_chain(node_id, set(), depth)
    
    if not chain:
        return {'error': f'节点 {node_id} 不存在', 'chain': None}
    
    return {'chain': chain}

@router.get("/mastery-overview")
async def get_mastery_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户在各个分支、年级的掌握概览
    """
    nodes = load_nodes()
    
    # 按分支和年级统计
    branch_stats = {}
    level_stats = {}
    type_stats = {}
    
    for node in nodes:
        branch = node.get('branch', 'other')
        grade = node.get('grade', '未知')
        node_type = node.get('type', 'concept')
        
        # 初始化
        if branch not in branch_stats:
            branch_stats[branch] = {'total': 0, 'known': 0}
        if grade not in level_stats:
            level_stats[grade] = {'total': 0, 'known': 0}
        if node_type not in type_stats:
            type_stats[node_type] = {'total': 0, 'known': 0}
        
        # 统计总数
        branch_stats[branch]['total'] += 1
        level_stats[grade]['total'] += 1
        type_stats[node_type]['total'] += 1
        
        # 获取用户掌握状态
        known_records = db.query(UserKnowledge).filter(
            UserKnowledge.user_id == current_user.id,
            UserKnowledge.status == 'known',
            UserKnowledge.node_id == node.get('id')
        ).first()
        
        if known_records:
            branch_stats[branch]['known'] += 1
            level_stats[grade]['known'] += 1
            type_stats[node_type]['known'] += 1
    
    # 计算百分比
    def calc_percent(stats):
        return {
            k: {
                'total': v['total'],
                'known': v['known'],
                'percent': round(v['known'] / v['total'] * 100, 1) if v['total'] > 0 else 0
            }
            for k, v in stats.items()
        }
    
    return {
        'by_branch': calc_percent(branch_stats),
        'by_level': calc_percent(level_stats),
        'by_type': calc_percent(type_stats),
        'total_nodes': len(nodes)
    }

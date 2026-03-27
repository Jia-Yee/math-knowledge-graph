#!/usr/bin/env python3
"""
为数学知识图谱生成详细定义和描述
"""
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
NODES_FILE = DATA_DIR / "core-nodes.json"
OUTPUT_FILE = DATA_DIR / "descriptions.json"

# 知识点详细定义模板
DEFINITIONS = {}

def load_nodes():
    """加载知识点"""
    with open(NODES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('nodes', [])

def generate_definition(node):
    """为单个知识点生成详细定义"""
    name_zh = node['name'].get('zh', '')
    name_en = node['name'].get('en', '')
    node_type = node.get('type', 'concept')
    level = node.get('level', '')
    branch = node.get('branch', '')
    tags = node.get('tags', [])
    
    # 基于节点类型和分支生成描述
    definition = {
        "id": node['id'],
        "name": node['name'],
        "type": node_type,
        "level": level,
        "branch": branch,
        "tags": tags,
        "definition": {
            "zh": generate_zh_definition(node),
            "en": generate_en_definition(node)
        },
        "example": generate_example(node),
        "related_concepts": node.get('prerequisites', [])
    }
    
    return definition

def generate_zh_definition(node):
    """生成中文定义"""
    name = node['name'].get('zh', '')
    node_type = node.get('type', 'concept')
    branch = node['branch']
    level = node['level']
    difficulty = node.get('difficulty', 1)
    
    # 根据不同类型和分支生成不同的描述
    definitions = {
        ("concept", "arithmetic"): f"{name}是数学中最基本的概念之一，是进行算术运算的基础。",
        ("concept", "algebra"): f"{name}是代数中的基本概念，用于描述数和变量之间的关系。",
        ("concept", "geometry"): f"{name}是几何学中的基础概念，是研究空间形状和大小的重要工具。",
        ("concept", "analysis"): f"{name}是分析数学的核心概念，是理解微积分的基础。",
        ("concept", "probability"): f"{name}是概率论的基本概念，用于描述随机现象的可能性。",
        ("concept", "statistics"): f"{name}统计学的基本概念，用于数据的收集、整理和分析。",
        ("concept", "discrete"): f"{name}是离散数学的重要概念，在计算机科学中有广泛应用。",
        ("concept", "number_theory"): f"{name}是数论研究的基本概念，涉及整数的性质和关系。",
        ("theorem", "any"): f"{name}是一个重要的数学定理，具有严格的数学证明。",
        ("formula", "any"): f"{name}是一个重要的数学公式，反映了数学中的基本规律。",
    }
    
    key = (node_type, branch)
    if key in definitions:
        return definitions[key]
    if node_type in ['theorem', 'formula']:
        return definitions.get((node_type, "any"), f"{name}是数学中的重要知识点。")
    
    return f"{name}是数学学习中的重要概念，在{get_level_name(level)}阶段需要掌握。"

def generate_en_definition(node):
    """生成英文定义"""
    name = node['name'].get('en', '')
    node_type = node.get('type', 'concept')
    branch = node['branch']
    
    # 英文定义模板
    en_defs = {
        "arithmetic": f"{name} is a fundamental concept in arithmetic, essential for mathematical operations.",
        "algebra": f"{name} is a basic concept in algebra, describing relationships between numbers and variables.",
        "geometry": f"{name} is a fundamental concept in geometry, important for understanding spatial relationships.",
        "analysis": f"{name} is a core concept in mathematical analysis, foundational for calculus.",
        "probability": f"{name} is a basic concept in probability theory, describing the likelihood of random events.",
        "statistics": f"{name} is a fundamental concept in statistics, used for data analysis and interpretation.",
        "discrete": f"{name} is an important concept in discrete mathematics, widely used in computer science.",
        "number_theory": f"{name} is a fundamental concept in number theory, involving properties of integers.",
    }
    
    return en_defs.get(branch, f"{name} is an important mathematical concept.")

def generate_example(node):
    """生成示例"""
    name_zh = node['name'].get('zh', '')
    examples = {
        "自然数": "1, 2, 3, 4, 5, ...",
        "加法": "2 + 3 = 5",
        "减法": "5 - 3 = 2",
        "乘法": "3 × 4 = 12",
        "除法": "12 ÷ 3 = 4",
        "分数": "1/2, 3/4, 5/8",
        "小数": "0.5, 3.14, 2.718",
    }
    
    for key, example in examples.items():
        if key in name_zh:
            return example
    
    return None

def get_level_name(level):
    """获取级别名称"""
    names = {
        "primary": "小学",
        "junior": "初中", 
        "senior": "高中",
        "undergrad": "本科",
        "master": "硕士",
        "phd": "博士",
        "research": "研究"
    }
    return names.get(level, level)

def main():
    """主函数"""
    print("正在加载知识点...")
    nodes = load_nodes()
    print(f"共加载 {len(nodes)} 个知识点")
    
    definitions = {}
    
    for i, node in enumerate(nodes):
        if (i + 1) % 100 == 0:
            print(f"已处理 {i + 1}/{len(nodes)} 个知识点...")
        
        node_id = node['id']
        definitions[node_id] = generate_definition(node)
    
    # 保存结果
    output = {
        "metadata": {
            "version": "1.0",
            "description": "数学知识图谱详细定义与描述",
            "total_nodes": len(definitions),
            "generated": "auto"
        },
        "definitions": definitions
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 {len(definitions)} 个知识点的详细描述")
    print(f"📁 保存到: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

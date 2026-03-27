#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加 Logic 和 Combinatorics 分支的新节点"""

import json

# 读取现有数据
with open('data/core-nodes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    nodes = data.get('nodes', [])

# 获取现有ID列表
existing_ids = [n['id'] for n in nodes]

# 新的 Logic 节点（本科到研究生级别）
new_logic_nodes = [
    {
        'id': 'logic_propositional_advanced',
        'type': 'concept',
        'name': {'zh': '命题逻辑进阶', 'en': 'Advanced Propositional Logic'},
        'description': {'zh': '深入学习命题逻辑的完备性、可满足性问题(SAT)、命题逻辑的算法复杂度分析。包含DPLL算法、CDCL算法等。', 'en': ''},
        'level': 'undergrad',
        'branch': 'logic',
        'tags': ['本科', '数学', '计算机科学'],
        'prerequisites': ['s_sen12'],
        'difficulty': 6,
        'importance': 8,
        'estimated_minutes': 180
    },
    {
        'id': 'logic_predicate_calculus',
        'type': 'concept',
        'name': {'zh': '谓词逻辑', 'en': 'Predicate Calculus'},
        'description': {'zh': '一阶谓词逻辑的基本理论，包括语法、语义、一阶理论、完备性定理（哥德尔完备性定理）。', 'en': ''},
        'level': 'undergrad',
        'branch': 'logic',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen13', 's_sen14'],
        'difficulty': 7,
        'importance': 9,
        'estimated_minutes': 240
    },
    {
        'id': 'logic_set_theory',
        'type': 'concept',
        'name': {'zh': '集合论基础', 'en': 'Set Theory Fundamentals'},
        'description': {'zh': '朴素集合论与公理化集合论(ZF公理系统)，包括：外延公理、空集公理、配对公理、并集公理、幂集公理、无穷公理、替换公理、正则公理。', 'en': ''},
        'level': 'undergrad',
        'branch': 'logic',
        'tags': ['本科', '数学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 7,
        'importance': 10,
        'estimated_minutes': 300
    },
    {
        'id': 'logic_ordinal_cardinal',
        'type': 'concept',
        'name': {'zh': '序数与基数', 'en': 'Ordinal and Cardinal Numbers'},
        'description': {'zh': '序数的定义与运算、基数的定义、康托尔-伯恩斯坦-施罗德定理、连续统假设、基数运算。', 'en': ''},
        'level': 'master',
        'branch': 'logic',
        'tags': ['硕士', '数学'],
        'prerequisites': ['logic_set_theory'],
        'difficulty': 9,
        'importance': 8,
        'estimated_minutes': 360
    },
    {
        'id': 'logic_godel_incompleteness',
        'type': 'theorem',
        'name': {'zh': '哥德尔不完备定理', 'en': "Godel's Incompleteness Theorems"},
        'description': {'zh': '哥德尔第一不完备定理：任何足够强的递归可枚举公理系统，若是一致的，则不完备。哥德尔第二不完备定理：系统的一致性不能在系统内部证明。', 'en': ''},
        'level': 'master',
        'branch': 'logic',
        'tags': ['硕士', '数学', '前沿'],
        'prerequisites': ['logic_predicate_calculus', 'logic_recursion'],
        'difficulty': 10,
        'importance': 10,
        'estimated_minutes': 480
    },
    {
        'id': 'logic_recursion',
        'type': 'concept',
        'name': {'zh': '递归论', 'en': 'Recursion Theory'},
        'description': {'zh': '可计算性理论，研究可计算函数、图灵机、丘奇-图灵论题、停机问题、复杂度类(P, NP, PSPACE等)。', 'en': ''},
        'level': 'master',
        'branch': 'logic',
        'tags': ['硕士', '数学', '计算机科学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 9,
        'importance': 9,
        'estimated_minutes': 420
    },
    {
        'id': 'logic_model_theory',
        'type': 'concept',
        'name': {'zh': '模型论', 'en': 'Model Theory'},
        'description': {'zh': '形式语言与结构的解释理论研究，包括完备理论、范畴性、紧致性定理、Lowenheim-Skolem定理。', 'en': ''},
        'level': 'phd',
        'branch': 'logic',
        'tags': ['博士', '数学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 10,
        'importance': 8,
        'estimated_minutes': 540
    },
    {
        'id': 'logic_proof_theory',
        'type': 'concept',
        'name': {'zh': '证明论', 'en': 'Proof Theory'},
        'description': {'zh': '研究形式证明的结构和性质，包括自然演绎、希尔伯特系统、 sequent演算、cut-elimination定理。', 'en': ''},
        'level': 'phd',
        'branch': 'logic',
        'tags': ['博士', '数学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 10,
        'importance': 8,
        'estimated_minutes': 480
    },
    {
        'id': 'logic_axiom_choice',
        'type': 'axiom',
        'name': {'zh': '选择公理', 'en': 'Axiom of Choice'},
        'description': {'zh': '选择公理(Axiom of Choice)及其等价形式：佐恩引理、良序定理、图基引理。在数学各领域的重要应用。', 'en': ''},
        'level': 'master',
        'branch': 'logic',
        'tags': ['硕士', '数学'],
        'prerequisites': ['logic_set_theory'],
        'difficulty': 8,
        'importance': 9,
        'estimated_minutes': 300
    },
    {
        'id': 'logic_modal',
        'type': 'concept',
        'name': {'zh': '模态逻辑', 'en': 'Modal Logic'},
        'description': {'zh': '模态逻辑研究必然、可能性等模态概念，包括可能世界语义学、K系统、时态逻辑、认知逻辑。', 'en': ''},
        'level': 'master',
        'branch': 'logic',
        'tags': ['硕士', '数学', '哲学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 8,
        'importance': 7,
        'estimated_minutes': 360
    },
    {
        'id': 'logic_category_theory',
        'type': 'concept',
        'name': {'zh': '范畴论基础', 'en': 'Category Theory Basics'},
        'description': {'zh': '范畴论是研究数学结构及其关系的抽象框架，包括对象、态射、函子、自然变换、极限、余极限。', 'en': ''},
        'level': 'phd',
        'branch': 'logic',
        'tags': ['博士', '数学'],
        'prerequisites': ['logic_set_theory'],
        'difficulty': 10,
        'importance': 9,
        'estimated_minutes': 600
    },
    {
        'id': 'logic_type_theory',
        'type': 'concept',
        'name': {'zh': '类型论', 'en': 'Type Theory'},
        'description': {'zh': '类型论是构造性数学和计算机科学的基础，包括简单类型lambda演算、依赖类型、Martin-Lof类型论。', 'en': ''},
        'level': 'phd',
        'branch': 'logic',
        'tags': ['博士', '数学', '计算机科学'],
        'prerequisites': ['logic_predicate_calculus'],
        'difficulty': 10,
        'importance': 9,
        'estimated_minutes': 540
    }
]

# 新的 Combinatorics 节点
new_combinatorics_nodes = [
    {
        'id': 'combo_generating_function',
        'type': 'method',
        'name': {'zh': '生成函数', 'en': 'Generating Functions'},
        'description': {'zh': '利用生成函数解决计数问题，包括普通生成函数、指数生成函数、常系数线性递推关系的解法。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen59', 's_sen60'],
        'difficulty': 6,
        'importance': 9,
        'estimated_minutes': 240
    },
    {
        'id': 'combo_recurrence',
        'type': 'concept',
        'name': {'zh': '递推关系', 'en': 'Recurrence Relations'},
        'description': {'zh': '线性递推关系、常系数齐次和非齐次递推方程、特征根方法、迭代法、斐波那契数列。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['combo_generating_function'],
        'difficulty': 6,
        'importance': 8,
        'estimated_minutes': 180
    },
    {
        'id': 'combo_pigeonhole_advanced',
        'type': 'theorem',
        'name': {'zh': '鸽巢原理进阶', 'en': 'Advanced Pigeonhole Principle'},
        'description': {'zh': '鸽巢原理的深入应用，包括Dirichlet抽屉原理、Ramsey定理、Van der Waerden定理。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen58'],
        'difficulty': 7,
        'importance': 8,
        'estimated_minutes': 180
    },
    {
        'id': 'combo_ramsey_theory',
        'type': 'theory',
        'name': {'zh': '拉姆齐理论', 'en': 'Ramsey Theory'},
        'description': {'zh': '研究在足够大的结构中必然出现某种特定子结构，包括Ramsey数、图的Ramsey理论、组合几何中的Ramsey问题。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['combo_pigeonhole_advanced'],
        'difficulty': 9,
        'importance': 8,
        'estimated_minutes': 360
    },
    {
        'id': 'combo_polya_counting',
        'type': 'theorem',
        'name': {'zh': '波利亚计数定理', 'en': "Polya's Counting Theorem"},
        'description': {'zh': '利用群作用对称性进行计数，包含Burnside引理、置换群、颜色配置计数。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['combo_group_action'],
        'difficulty': 8,
        'importance': 8,
        'estimated_minutes': 300
    },
    {
        'id': 'combo_group_action',
        'type': 'concept',
        'name': {'zh': '群作用与计数', 'en': 'Group Actions and Counting'},
        'description': {'zh': '群在集合上的作用、轨道、稳定子群、轨道-稳定子定理，与波利亚计数定理的关系。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['s_sen58'],
        'difficulty': 8,
        'importance': 7,
        'estimated_minutes': 240
    },
    {
        'id': 'combo_inclusion_exclusion',
        'type': 'method',
        'name': {'zh': '容斥原理', 'en': 'Inclusion-Exclusion Principle'},
        'description': {'zh': '计算有限集合并集基数的通用方法，包括容斥原理、广义容斥原理、错排问题应用。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen58'],
        'difficulty': 5,
        'importance': 8,
        'estimated_minutes': 120
    },
    {
        'id': 'combo_partitions',
        'type': 'concept',
        'name': {'zh': '整数分拆', 'en': 'Integer Partitions'},
        'description': {'zh': '整数的分拆理论，包括Ferrers图、生成函数、分拆的同余性质、猜想现在已被证明的分拆数同余。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['combo_generating_function'],
        'difficulty': 9,
        'importance': 7,
        'estimated_minutes': 300
    },
    {
        'id': 'combo_stirling_numbers',
        'type': 'concept',
        'name': {'zh': '斯特林数', 'en': 'Stirling Numbers'},
        'description': {'zh': '第一类斯特林数（轮换）和第二类斯特林数（集合划分），递推关系、生成函数、组合解释。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen57', 's_sen58'],
        'difficulty': 6,
        'importance': 7,
        'estimated_minutes': 180
    },
    {
        'id': 'combo_catalan',
        'type': 'concept',
        'name': {'zh': '卡塔兰数', 'en': 'Catalan Numbers'},
        'description': {'zh': '卡塔兰数的定义、应用、递推关系、生成函数，包括二叉树、合法括号序列、凸多边形剖分等经典应用。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['combo_recurrence'],
        'difficulty': 6,
        'importance': 8,
        'estimated_minutes': 180
    },
    {
        'id': 'combo_design_theory',
        'type': 'theory',
        'name': {'zh': '组合设计理论', 'en': 'Combinatorial Design Theory'},
        'description': {'zh': '区组设计、平衡不完全区组设计(BIBD)、有限几何、Steiner三元系、拉丁方、Hanani条件。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['combo_polya_counting'],
        'difficulty': 9,
        'importance': 7,
        'estimated_minutes': 360
    },
    {
        'id': 'combo_extremal',
        'type': 'theory',
        'name': {'zh': '极值组合学', 'en': 'Extremal Combinatorics'},
        'description': {'zh': '研究给定约束下集合或图的极值问题，包括Turán定理、Erdos-Szekeres定理、图论极值问题。', 'en': ''},
        'level': 'phd',
        'branch': 'combinatorics',
        'tags': ['博士', '数学'],
        'prerequisites': ['combo_ramsey_theory'],
        'difficulty': 10,
        'importance': 8,
        'estimated_minutes': 420
    },
    {
        'id': 'combo_probabilistic',
        'type': 'method',
        'name': {'zh': '概率方法', 'en': 'Probabilistic Method'},
        'description': {'zh': 'Erdos创立的概率方法，用于证明存在性问题，包括线性期望法、概率不等式（Lovasz局部引理）。', 'en': ''},
        'level': 'master',
        'branch': 'combinatorics',
        'tags': ['硕士', '数学'],
        'prerequisites': ['combo_ramsey_theory'],
        'difficulty': 9,
        'importance': 8,
        'estimated_minutes': 300
    },
    {
        'id': 'combo_additive',
        'type': 'theory',
        'name': {'zh': '加性组合学', 'en': 'Additive Combinatorics'},
        'description': {'zh': '研究整数集合的加性结构，包括Cauchy-Davenport定理、Freiman定理、AP(Sumset)、和集与积集的关系。', 'en': ''},
        'level': 'phd',
        'branch': 'combinatorics',
        'tags': ['博士', '数学'],
        'prerequisites': ['combo_extremal'],
        'difficulty': 10,
        'importance': 8,
        'estimated_minutes': 480
    },
    {
        'id': 'combo_enumerative',
        'type': 'theory',
        'name': {'zh': '枚举组合学', 'en': 'Enumerative Combinatorics'},
        'description': {'zh': '系统研究有限集合的计数问题，包括各种计数技术、特殊计数序列、组合解释。', 'en': ''},
        'level': 'undergrad',
        'branch': 'combinatorics',
        'tags': ['本科', '数学'],
        'prerequisites': ['s_sen57', 's_sen58'],
        'difficulty': 6,
        'importance': 9,
        'estimated_minutes': 240
    }
]

# 添加新节点
all_new_nodes = new_logic_nodes + new_combinatorics_nodes

added_count = 0
for new_node in all_new_nodes:
    if new_node['id'] in existing_ids:
        print(f'警告: ID {new_node["id"]} 已存在，跳过')
    else:
        nodes.append(new_node)
        existing_ids.append(new_node['id'])
        added_count += 1

# 保存
data['nodes'] = nodes
with open('data/core-nodes.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'添加完成!')
print(f'  - Logic 新增: {len(new_logic_nodes)} 个节点')
print(f'  - Combinatorics 新增: {len(new_combinatorics_nodes)} 个节点')
print(f'  - 实际新增: {added_count} 个节点')
print(f'  - 总节点数: {len(nodes)}')

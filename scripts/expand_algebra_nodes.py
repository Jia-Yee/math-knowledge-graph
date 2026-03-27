#!/usr/bin/env python3
"""代数分支节点扩张脚本 - 数据分离版"""
import json

DATA_FILE = "data/core-nodes.json"

ANCHOR = {"group_theory","subgroup","normal_subgroup","coset","quotient_group","homomorphism","isomorphism","kernel","lagrange_theorem","cauchy_theorem","cyclic_group","permutation_group","abelian_group","sylow_theorems","simple_group","solvable_group","free_group","presentation","group_action","orbit_stabilizer","polya_enumeration","burnside_lemma","ring_theory","ideal_ring","quotient_ring","field_theory","field_extension","algebraic_extension","galois_theory","galois","galois_group","galois_correspondence","insolubility_of_quintic","abstract_algebra","vector_space","la_vector_space","linear_transform","la_linear_map","module","module_theory","linear_algebra_new","tensor_product","commutative_algebra","category","functor","natural_transformation","homological","chain_complex","homology_group","lie_algebra","lie_group","hopf_algebra","quantum_group"}

def mk(id_, zh, en, level, diff, imp, pre):
    return {"id": id_, "type": "concept", "name": {"zh": zh, "en": en}, "description": {"zh": zh, "en": en}, "level": level, "branch": "algebra", "tags": ["代数", "数学"], "prerequisites": [p for p in pre if p in ANCHOR], "difficulty": diff, "importance": imp, "estimated_minutes": 60}

with open(DATA_FILE) as f:
    data = json.load(f)
existing = {n["id"] for n in data["nodes"]}
alg_count = sum(1 for n in data["nodes"] if n.get("branch") == "algebra")
print(f"现有代数节点: {alg_count} 个")

done = set()
new_count = 0

def g(id_, zh, en, level, diff, imp, pre):
    global new_count
    if id_ not in existing and id_ not in done:
        done.add(id_)
        data["nodes"].append(mk(id_, zh, en, level, diff, imp, pre))
        new_count += 1

# ================================================================
# 节点数据加载 (分文件存储)
# ================================================================
import os, glob

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "algebra_nodes_data")

loaded = 0
if os.path.isdir(data_dir):
    for fpath in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        with open(fpath) as f:
            chunk = json.load(f)
        for d in chunk:
            g(d["id"], d["zh"], d["en"], d["level"], d["diff"], d["imp"], d["pre"])
            loaded += 1

# ================================================================
# 统计与保存
# ================================================================
total_alg = sum(1 for n in data["nodes"] if n.get("branch") == "algebra")
print(f"新增代数节点: {new_count} 个")
print(f"总代数节点: {total_alg} 个")

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"已保存到: {DATA_FILE}")

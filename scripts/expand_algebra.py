#!/usr/bin/env python3
"""
数学知识图谱扩张脚本 — 代数分支
目标: 群论/环论/域论/模论/表示论/范畴论/同调代数/线性代数
"""
import json, re, sys, os

DATA_FILE = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"

# ─────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────
def sid(name):
    s = name.lower().replace(' ', '_').replace('-', '_')
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:80]

def node_exists(nodes, nid):
    return any(n['id'] == nid for n in nodes)

def get_or_create(nodes, nid, defaults):
    for n in nodes:
        if n['id'] == nid:
            return n
    n = {"id": nid, "prerequisites": [], **defaults}
    nodes.append(n)
    return n

def add_prereq(n, pre_id):
    if pre_id not in (n.get('prerequisites') or []):
        n.setdefault('prerequisites', []).append(pre_id)

def ch(branch):
    """返回分支章节ID（新版）"""
    m = {
        "algebra": "ch_zhengshi_yu_yinshi_fenjie",
        "topology": "ch_tuopuxue",
        "analysis": "ch_shibian_fubian_hanshu",
        "number_theory": "ch_chudeng_shulun",
        "discrete": "ch_lisan_shuxue",
        "probability": "ch_gailvlun",
        "dynamics": "ch_dongli_xitong",
        "numerical": "ch_shuzhi_fenxi",
        "statistics": "ch_shuli_tongji",
        "pde": "ch_pianweifen_fangcheng",
        "physics": "ch_shuxue_wuli",
    }
    return m.get(branch, "ch_shuyu_yunsuan")

# ─────────────────────────────────────────────────
# 节点模板
# ─────────────────────────────────────────────────
def make_node(nid, name_zh, name_en, branch, level, tags,
              prereqs=None, difficulty=4, importance=7,
              desc_zh="", desc_en="", minutes=60):
    return {
        "id": nid,
        "type": "concept",
        "name": {"zh": name_zh, "en": name_en},
        "description": {
            "zh": desc_zh or f"{name_zh}是{branch}中的重要概念",
            "en": desc_en or name_en
        },
        "level": level,
        "branch": branch,
        "tags": tags,
        "prerequisites": list(prereqs) if prereqs else [],
        "difficulty": difficulty,
        "importance": importance,
        "estimated_minutes": minutes
    }

# ─────────────────────────────────────────────────
# Ⅰ. 群论 (Group Theory)
# ─────────────────────────────────────────────────
def expand_group_theory(nodes):
    """群论扩张"""
    added = 0
    b = "algebra"

    # 基础群概念
    base_concepts = [
        ("group_definition", "群的定义", "group definition",
         ["group","binary operation","associativity","identity","inverse","closure",
          "commutativity","abelian","non-abelian","magma","semigroup","monoid"]),
        ("group_axioms", "群公理", "group axioms",
         ["closure","associativity","identity","inverse","left identity","right identity"]),
        ("subgroup_definition", "子群的定义", "subgroup definition",
         ["subgroup","subgroup test","closed under operation","closed under inverse"]),
        ("subgroup_test", "子群判别法", "subgroup test",
         ["subgroup test","one-step test","two-step test","non-empty","closed","inverse"]),
        ("trivial_subgroup", "平凡子群", "trivial subgroup",
         ["trivial subgroup","improper subgroup","trivial group","trivial"]),
        ("center_of_group", "群的中心", "center of a group",
         ["center","commutative subgroup","centralizer","central element"]),
        ("centralizer", "中心化子", "centralizer",
         ["centralizer","commuting element","conjugacy class"]),
        ("normalizer", "正规化子", "normalizer",
         ["normalizer","largest subgroup","conjugation"]),
    ]

    for sid_, zhn, enn, kws in base_concepts:
        nid = f"group_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","抽象代数"], kws, difficulty=3, importance=8,
                desc_zh=f"{zhn}是群论的基础内容"))
            added += 1

    # 循环群
    cyclic_concepts = [
        ("cyclic_group", "循环群", "cyclic group",
         ["cyclic group","generator","order of group","infinite cyclic","finite cyclic",
          "Z_n","Z","additive group modulo n"]),
        ("generator_cyclic", "生成元", "generator of cyclic group",
         ["generator","cyclic generator","primitive root modulo n","order of element",
          "exponent of group"]),
        ("cyclic_subgroup", "循环子群", "cyclic subgroup",
         ["cyclic subgroup","subgroup of cyclic","order of element","lagrange cyclic"]),
        ("subgroup_cyclic_cyclic", "循环群的子群", "subgroups of cyclic groups",
         ["cyclic subgroup theorem","unique subgroup of each order","subgroup lattice cyclic"]),
        ("order_of_element", "元素的阶", "order of element",
         ["order of element","finite order","infinite order","identity order 1",
          "a^k = e","order divides group order"]),
        ("lagrange_theorem", "拉格朗日定理", "Lagrange theorem",
         ["Lagrange theorem","order of subgroup divides order of group","coset decomposition",
          "index of subgroup","product of order and index"]),
        ("index_of_subgroup", "子群的指数", "index of subgroup",
         ["index of subgroup","left coset","right coset","coset counting",
          "Lagrange index formula"]),
        ("euler_phi_function", "欧拉函数", "Euler phi function",
         ["Euler phi","phi(n)","number of generators of cyclic group order n",
          "multiplicative function","totient function"]),
        ("fermat_little_group", "费马小定理（群论版本）", "Fermat little theorem group form",
         ["Fermat little theorem","a^{phi(p)} = 1 mod p","Euler theorem group form",
          "multiplicative group modulo n","reduced residue system"]),
    ]

    for sid_, zhn, enn, kws in cyclic_concepts:
        nid = f"group_cyclic_{sid_}"
        if not node_exists(nodes, nid):
            n = make_node(nid, zhn, enn, b, "undergrad",
                ["群论","抽象代数"], kws, difficulty=3, importance=8,
                desc_zh=f"{zhn}是循环群理论的核心内容")
            nodes.append(n); added += 1

    # 典型群实例
    classic_groups = [
        ("symmetric_group_s_n", "对称群S_n", "symmetric group S_n",
         ["symmetric group","S_n","permutation group","n! elements","non-abelian for n>=3",
          "alternating group","An","simple group","A_n for n>=5"]),
        ("alternating_group", "交错群A_n", "alternating group",
         ["alternating group","A_n","even permutations","simple group","A_5 simple",
          "A_n simple for n>=5","normal subgroup of S_n","index 2"]),
        ("dihedral_group", "二面体群D_n", "dihedral group",
         ["dihedral group","D_n","symmetries of n-gon","rotation","reflection",
          "order 2n","presentation","D_n = <r,s | r^n=s^2=e, srs=r^{-1}>"]),
        ("quaternion_group", "四元数群Q_8", "quaternion group",
         ["quaternion group","Q_8","non-abelian group order 8","Hamilton",
          "i^2=j^2=k^2=ijk=-1","center {1,-1}","quaternions"]),
        ("general_linear_group", "一般线性群GL_n", "general linear group",
         ["GL_n","general linear group","invertible matrices","determinant non-zero",
          "group under multiplication","dimension n^2","SL_n subgroup"]),
        ("special_linear_group", "特殊线性群SL_n", "special linear group",
         ["SL_n","special linear group","determinant 1","normal subgroup of GL_n",
          "matrix group","volume preserving"]),
        ("orthogonal_group", "正交群O_n", "orthogonal group",
         ["orthogonal group","O_n","orthogonal matrices","O^T O = I","determinant +-1",
          "SO_n subgroup","rotations and reflections","O(3)"]),
        ("special_orthogonal_group", "特殊正交群SO_n", "special orthogonal group",
         ["SO_n","special orthogonal","rotations only","SO(3)","SO(2)",
          "determinant 1","orientation preserving"]),
        ("unitary_group", "酉群U_n", "unitary group",
         ["unitary group","U_n","unitary matrices","U^* = U^{-1}","U(1)",
          "U(n)","complex matrices","Hermitian"]),
        ("heisenberg_group", "Heisenberg群", "Heisenberg group",
         ["Heisenberg group","unitriangular matrices","nilpotent group",
          "3x3 matrices","upper triangular 1s","non-abelian nilpotent"]),
        ("affine_group", "仿射群Aff_n", "affine group",
         ["affine group","Aff_n","affine transformations","linear+translation",
          "semidirect product","GL_n semi R^n"]),
        ("semidirect_product", "半直积", "semidirect product",
         ["semidirect product","N rt H","internal semidirect product","external semidirect product",
          "semi-direct product","normal subgroup","action"]),
    ]

    for sid_, zhn, enn, kws in classic_groups:
        nid = f"group_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","典型群"], kws, difficulty=4, importance=7))
            added += 1

    # 陪集与商群
    coset_concepts = [
        ("left_coset", "左陪集", "left coset",
         ["left coset","aH","partition of group","coset representative",
          "same left coset iff a^{-1}b in H"]),
        ("right_coset", "右陪集", "right coset",
         ["right coset","Ha","partition of group","right coset decomposition",
          "double coset"]),
        ("coset_lagrange", "拉格朗日定理的应用", "applications of Lagrange theorem",
         ["Lagrange corollary","order of element divides group order",
          "no subgroup of order not dividing group","prime order implies cyclic",
          "group of prime order"]),
        ("index_theorem", "指数定理", "index theorem",
         ["index theorem","[G:H]=[G:K][K:H]","product of indices",
          "double coset formula","orbit-stabilizer index"]),
        ("normal_subgroup", "正规子群", "normal subgroup",
         ["normal subgroup","N ◁ G","left coset equals right coset",
          "kernel of homomorphism","conjugate of subgroup","N = ker phi"]),
        ("normal_subgroup_test", "正规子群判别", "tests for normality",
         ["normal subgroup test","conjugate always in subgroup",
          "aNa^{-1} subseteq N","index 2 implies normal"]),
        ("simple_group", "单群", "simple group",
         ["simple group","no non-trivial normal subgroup","abelian simple",
          "Z_p prime order","A_n simple for n>=5","classification of finite simple groups"]),
        ("composition_series", "合成列", "composition series",
         ["composition series","composition factors","Jordan-Hölder theorem",
          "simple factors","length of group","refinement"]),
        ("jordan_holder_theorem", "若尔当-赫尔德定理", "Jordan-Hölder theorem",
         ["Jordan-Hölder theorem","uniqueness of composition factors",
          "equivalent composition series","isomorphism classes of factors",
          "Schreier refinement"]),
        ("quotient_group", "商群", "quotient group",
         ["quotient group","G/N","coset multiplication","normal subgroup required",
          "order |G|/|N|","natural projection","factor group"]),
        ("fundamental_homomorphism_theorem", "基本同态定理", "fundamental homomorphism theorem",
         ["fundamental theorem on homomorphisms","first isomorphism theorem",
          "G/ker phi ~= im phi","kernel is normal","image"]),
        ("correspondence_theorem", "对应定理", "correspondence theorem",
         ["correspondence theorem","subgroups of quotient","N <= H <= G",
          "H/N corresponds to subgroup of G/N","bijection"]),
        ("isomorphism_theorems", "同构定理", "isomorphism theorems",
         ["first isomorphism theorem","second isomorphism theorem",
          "third isomorphism theorem","N/(N∩H) ~= NH/H","diamond isomorphism"]),
    ]

    for sid_, zhn, enn, kws in coset_concepts:
        nid = f"group_coset_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","商群与同构"], kws, difficulty=4, importance=8))
            added += 1

    # 同构与同态
    homo_concepts = [
        ("group_homomorphism", "群同态", "group homomorphism",
         ["group homomorphism","phi(ab)=phi(a)phi(b)","kernel","image",
          "preserves identity","preserves inverses","natural projection"]),
        ("group_isomorphism", "群同构", "group isomorphism",
         ["group isomorphism","bijective homomorphism","phi:a->b",
          "isomorphic groups"," Cayley theorem","isomorphism type"]),
        ("kernel_of_homomorphism", "同态核", "kernel of homomorphism",
         ["kernel","ker phi","normal subgroup","phi(g)=e iff g in ker",
          "kernel is normal","first isomorphism theorem"]),
        ("cayley_theorem", "凯莱定理", "Cayley theorem",
         ["Cayley theorem","every group isomorphic to subgroup of S_n",
          "regular representation","permutation representation","n<=|G|"]),
        ("automorphism_group", "自同构群", "automorphism group",
         ["automorphism","automorphism group","Aut(G)","inner automorphism",
          "Inn(G) normal in Aut(G)","phi:g->aga^{-1}"]),
        ("aut_z_n", "Z_n的自同构群", "automorphisms of cyclic groups",
         ["Aut(Z_n)","automorphisms of cyclic group","phi(k)=ak mod n",
          "(a,n)=1","phi(n) = phi(n)","multiplicative group modulo n"]),
        ("inner_automorphisms", "内自同构", "inner automorphisms",
         ["inner automorphism","Inn(G)","conjugation","normal subgroup",
          "G/Z(G) ~= Inn(G)","automorphism group structure"]),
        ("outer_automorphisms", "外自同构", "outer automorphisms",
         ["outer automorphism","Out(G)","Aut(G)/Inn(G)",
          "outer automorphism of simple groups","S_n outer automorphisms"]),
    ]

    for sid_, zhn, enn, kws in homo_concepts:
        nid = f"group_homo_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","同态与同构"], kws, difficulty=4, importance=8))
            added += 1

    # 群作用
    action_concepts = [
        ("group_action_definition", "群作用的定义", "group action definition",
         ["group action","G × X -> X","g·x","associativity","identity action",
          "permutation representation","faithful action","free action","regular action"]),
        ("orbit_and_stabilizer", "轨道与稳定子", "orbit and stabilizer",
         ["orbit","stabilizer","orbit-stabilizer theorem","|Orbit|·|Stabilizer|=|G|",
          "transitive action","orbit decomposition","equivalence relation"]),
        ("orbit_stabilizer_theorem", "轨道-稳定子定理", "orbit-stabilizer theorem",
         ["orbit-stabilizer","|G/G_x|=|Orbit(x)|","applications",
          "Cayley theorem proof","counting arguments","Burnside"]),
        ("transitive_action", "传递作用", "transitive action",
         ["transitive action","single orbit","G-space","simply transitive",
          "regular action","free and transitive"]),
        ("固定子群_稳定子", "稳定子群", "stabilizer subgroup",
         ["stabilizer","G_x","elements fixing x","subgroup of G",
          "orbit size = index of stabilizer"]),
        ("conjugation_action", "共轭作用", "conjugation action",
         ["conjugation","g·x = gxg^{-1}","class equation","conjugacy class",
          "centralizer size","class equation formula"]),
        ("class_equation", "类方程", "class equation",
         ["class equation","sum of class sizes","central element","|G|=|Z(G)|+sum|G:C_G(a_i)|",
          "centralizers","class size divides group order","conjugacy"]),
        ("cauchys_theorem", "柯西定理", "Cauchy theorem for groups",
         ["Cauchy theorem","order p divides |G| implies element of order p",
          "prime order element","finite abelian group","Sylow basis"]),
        ("p_group", "p群", "p-group",
         ["p-group","order power of p","center non-trivial","class equation p divides",
          "nilpotent","p-group of order p^n","Burnside"]),
        ("burnside_lemma", "伯恩赛德引理", "Burnside lemma",
         ["Burnside lemma","Burnside counting","average number of fixed points",
          "orbit counting","group action on set","coloring problems"]),
        ("polya_enumeration", "波利亚计数", "Polya enumeration theorem",
         ["Polya counting","Polya theorem","cycle index","cycle structure",
          "Burnside to Polya","pattern inventory","necklace counting"]),
        ("orbits_on_sets", "集合上的群作用", "orbits on sets",
         ["set G-set","G-set","orbit decomposition theorem","disjoint orbits",
          "transitive G-set","isotropy subgroup","homogeneous space"]),
        ("permutation_group_action", "置换群作用", "permutation group actions",
         ["permutation group","action on points","action on pairs","action on subsets",
          "primitive action","imprimitive action","block systems"]),
        ("primitive_action", "本原作用", "primitive action",
         ["primitive group action","no nontrivial block","maximal block",
          "transitive action","primitive permutation group","O'Nan-Scott"]),
        ("frobenius_group", "弗罗贝尼乌斯群", "Frobenius group",
         ["Frobenius group","Frobenius kernel","Frobenius complement",
          "Frobenius reciprocity","Frobenius theorem","complement"]),
        ("rank_action", "群的秩与作用", "rank of group action",
         ["rank of permutation group","subdegree","primitive","double transitive",
          "strongly regular","ranking of groups","Klein four-group"]),
    ]

    for sid_, zhn, enn, kws in action_concepts:
        nid = f"group_action_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","群作用"], kws, difficulty=4, importance=8))
            added += 1

    # Sylow定理
    sylow_concepts = [
        ("sylow_first_theorem", "第一Sylow定理", "Sylow first theorem",
         ["Sylow theorem","Sylow p-subgroup","order p^n","maximal p-subgroup",
          "Sylow p-subgroup exists","p-power subgroup","Hall subgroup"]),
        ("sylow_second_theorem", "第二Sylow定理", "Sylow second theorem",
         ["Sylow second theorem","all Sylow p-subgroups conjugate",
          "unique up to conjugacy","number of Sylow subgroups"]),
        ("sylow_third_theorem", "第三Sylow定理", "Sylow third theorem",
         ["Sylow third theorem","n_p | |G|","n_p ≡ 1 mod p",
          "number of Sylow p-subgroups divides |G|/p^n","applications"]),
        ("number_of_sylow_subgroups", "Sylow子群的数量", "number of Sylow subgroups",
         ["n_p divides m","n_p ≡ 1 mod p","applications","constraining n_p",
          "groups with one Sylow","normal Sylow"]),
        ("normal_sylow", "正规Sylow子群", "normal Sylow subgroup",
         ["normal Sylow","n_p=1","characterization","G has normal Sylow iff n_p=1",
          "product of all Sylow","all p-Sylow"]),
        ("hall_theorem", "Hall定理", "Hall theorem",
         ["Hall theorem","Hall subgroups","solvable groups","Hall existence",
          "pi-subgroup","pi-separable","Hall reciprocity"]),
        ("hall_subgroup", "Hall子群", "Hall subgroup",
         ["Hall subgroup","pi-subgroup","index coprime to p",
          "solvable group","Burnside paqb theorem"]),
        ("burnside_pa_qb", "Burnside定理", "Burnside theorem",
         ["Burnside p^aq^b theorem","order p^a q^b","solvable",
          "Frobenius theorem","solvable by prime power orders",
          "character theory proof"]),
        ("frobenius_theorem_pq", "Frobenius定理", "Frobenius theorem on groups of order pq",
         ["Frobenius theorem","order pq","p<q","cyclic if p does not divide q-1",
          "non-abelian exists when p|q-1","dihedral group"]),
    ]

    for sid_, zhn, enn, kws in sylow_concepts:
        nid = f"group_sylow_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","Sylow理论"], kws, difficulty=5, importance=9,
                desc_zh=f"{zhn}是有限群论的核心定理"))
            added += 1

    # 可解群与幂零群
    solvable_concepts = [
        ("commutator", "换位子", "commutator",
         ["commutator","[g,h]=ghg^{-1}h^{-1}","commutes iff [g,h]=e",
          "commutator subgroup","G' generated by commutators"]),
        ("commutator_subgroup", "换位子群", "commutator subgroup",
         ["commutator subgroup","derived subgroup","G'","abelianization",
          "G/G' abelian","abelianization map","minimal normal"]),
        ("solvable_group", "可解群", "solvable group",
         ["solvable group","derived series","G^{(n)}={e}","subnormal series",
          "normal series with abelian quotients","solvable by p-groups"]),
        ("nilpotent_group", "幂零群", "nilpotent group",
         ["nilpotent group","lower central series","upper central series",
          "Z(G)","Z_2(G)","finite p-group nilpotent","product of Sylow"]),
        ("derived_series", "导出列", "derived series",
         ["derived series","commutator iteration","G^{(0)}=G","G^{(1)}=G'",
          "G^{(n+1)}=(G^{(n)})'","solvable iff G^{(n)}={e}"]),
        ("lower_central_series", "下中心列", "lower central series",
         ["lower central series","gamma_1=G","gamma_{n+1}=[G,gamma_n]",
          "nilpotent iff gamma_{c+1}={e}","nilpotency class"]),
        ("upper_central_series", "上中心列", "upper central series",
         ["upper central series","Z_1=Z(G)","Z_{n+1}/Z_n = Z(G/Z_n)",
          "nilpotent iff Z_c=G","center"]),
        ("nilpotency_class", "幂零类", "nilpotency class",
         ["nilpotency class","class c","gamma_{c+1}={e}","Z_c=G",
          "c=1 abelian","c=2 nilpotent of class 2"]),
        ("solvable_by_pq", "可解群的判别", "solvable group criteria",
         ["solvable criteria","Hall subgroups","Burnside","order p^a q^b",
          "Sylow","finite solvable groups characterization"]),
        ("insolubility_of_s_5", "S_5的不可解性", "insolubility of S_5",
         ["A_5 simple","solvability test","S_5 not solvable","A_n simple n>=5",
          "non-solvable groups","composition factors"]),
        ("hall_solvable", "Hall可解群定理", "Hall theorem for solvable groups",
         ["Hall theorem solvable","Hall subgroups exist","pi-subgroups",
          "solvable group","Hall-Cater theorem"]),
    ]

    for sid_, zhn, enn, kws in solvable_concepts:
        nid = f"group_solvable_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "undergrad",
                ["群论","可解群与幂零群"], kws, difficulty=5, importance=8))
            added += 1

    # 有限单群
    finite_simple_concepts = [
        ("simple_group_classification", "有限单群分类定理", "classification of finite simple groups",
         ["classification of finite simple groups","CFSG","sporadic groups",
          "18 infinite families","26 sporadic groups","Feit-Thompson","odd order theorem"]),
        ("abelian_simple", "循环单群", "cyclic simple groups",
         ["abelian simple","Z_p simple","prime order","no non-trivial proper subgroup",
          "only cyclic simple groups"]),
        ("alternating_simple", "交错群单性", "simplicity of alternating groups",
         ["A_n simple for n>=5","A_5 simple","simplicity proof","normal subgroup of A_n",
          "even permutations","non-simplicity criteria"]),
        ("psl_2_f_q", "PSL_2(F_q)群", "PSL_2 over finite fields",
         ["PSL_2(q)","projective special linear"," PSL_2(F_q)","simple for q>=4",
          "order q(q^2-1)","dihedral subgroups","Borne"]),
        ("chevalley_groups", "谢瓦莱群", "Chevalley groups",
         ["Chevalley groups","simple Lie type groups","SL_n(q)","Sp_n(q)","SO_n(q)",
          "exceptional types","finite analogues of Lie groups"]),
        ("sporadic_groups", "零散单群", "sporadic simple groups",
         ["sporadic groups","26 sporadic"," Mathieu groups","M11 M12 M22 M23 M24",
          "J_1 J_2","Fi_22 Fi_23 Fi_24","Monster M","Baby Monster B"]),
        ("mathieu_groups", "马蒂厄群", "Mathieu groups",
         ["Mathieu groups","M11 M12 M22 M23 M24","multiply transitive","sporadic",
          "Steiner systems","Witt design","sharply transitive"]),
        ("monster_group", "大魔群", "Monster group",
         ["Monster","largest sporadic","order 808017424794512875886459904961710757005754368000000000",
          "Fischer-Griess","modular forms","monstrous moonshine","vertex operator algebra"]),
        ("baby_monster", "小魔群", "Baby Monster",
         ["Baby Monster","B","second largest sporadic","order 4154781481226426191177580544000000",
          "Held","Bender-Gutschwager","comprehension"]),
        ("janko_groups", "扬科群", "Janko groups",
         ["Janko groups","J_1 J_2 J_3 J_4","first new sporadic",
          "J_1 first discovered","Hall-Janko","J_4 largest Janko"]),
    ]

    for sid_, zhn, enn, kws in finite_simple_concepts:
        nid = f"group_simple_{sid_}"
        if not node_exists(nodes, nid):
            nodes.append(make_node(nid, zhn, enn, b, "master",
                ["群论","有限单群"], kws, difficulty=5, importance=9))
            added += 1

    # 有限生成群
    finitely_generated_concepts = [
        ("finitely_generated_group", "有限生成群", "finitely generated group",
         ["finitely generated group","fg group","generator set","word",
          "word length","Cayley graph","growth of group","GS(G,S)"]),
        ("free_group", "自由群", "free group",
         ["free group","F_n","rank","universal property","reduced word",
          "Nielsen-Schreier theorem","subgroup of free group free"]),
        ("nielsen_schreier",
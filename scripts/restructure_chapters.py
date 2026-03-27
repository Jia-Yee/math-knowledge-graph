#!/usr/bin/env python3
"""
数学知识图谱章节层次建模重构脚本

目标：
1. 消除名字里的年级（ch_一年级_数与运算 → ch_数与运算）
2. 年级作为独立属性 grade 存在
3. 学期作为独立属性 semester 存在
4. ID = name_zh 的合法英文ID
5. 去重（同名章节只保留一条）
6. 重建章节间的先修链
"""
import json, re, sys

DATA_FILE = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"

# ─────────────────────────────────────────────────
# 年级 → 年级中文名 + 年级序号
# ─────────────────────────────────────────────────
GRADE_MAP = {
    "primary":  {
        "1": ("一年级", "上"),
        "2": ("二年级", "上"),
        "3": ("三年级", "上"),
        "4": ("四年级", "上"),
        "5": ("五年级", "上"),
        "6": ("六年级", "上"),
    },
    "junior": {
        "7": ("七年级", "上"),
        "8": ("八年级", "上"),
        "9": ("九年级", "上"),
    },
    "senior": {
        "10": ("高一", "上"),
        "11": ("高二", "上"),
        "12": ("高三", "上"),
    },
    "undergrad": {
        "1": ("大一", "上"),
        "2": ("大二", "上"),
    },
}

def grade_info(level, suffix=None):
    """根据level推断默认年级，suffix用来区分同名章节"""
    # suffix模式: _1=一年级,_2=二年级,..._6=六年级,_7=七年级,_8=八年级,_9=九年级,_10=高一
    suffix_to_grade = {
        "_1": ("一年级", "上"), "_2": ("二年级", "上"), "_3": ("三年级", "上"),
        "_4": ("四年级", "上"), "_5": ("五年级", "上"), "_6": ("六年级", "上"),
        "_7": ("七年级", "上"), "_8": ("八年级", "上"), "_9": ("九年级", "上"),
        "_10": ("高一", "上"), "_11": ("高二", "上"), "_12": ("高三", "上"),
    }
    if suffix and suffix in suffix_to_grade:
        return suffix_to_grade[suffix]
    if level == "primary":
        return ("一年级", "上")  # 默认一年级
    if level == "junior":
        return ("七年级", "上")
    if level == "senior":
        return ("高一", "上")
    if level == "undergrad":
        return ("大一", "上")
    return ("未知", "上")

def sanitize_id(text):
    """中文→拼音片段，不保证完美但保证唯一可读"""
    mapping = {
        "数与运算":"shu_yu_yunsuan","时间与货币":"shijian_yu_huobi",
        "分类与统计":"fenlei_yu_tongji","图形与长度":"tuxiang_yu_changdu",
        "时间":"shijian","分数初步":"fenshu_chubu","面积测量":"mianji_celiang",
        "图形认识":"tuxiang_renshi","时间与方向":"shijian_yu_fangxiang",
        "角与四边形":"jiao_yu_sibianxing","统计与面积":"tongji_yu_mianji",
        "小数":"xiaoshu","因数与倍数":"yinshu_yu_beishu","图形变换与坐标":"tuxiang_bianhuan_yu_zuobiao",
        "圆":"yuan","百分数与比例":"baifenshu_yu_bili","负数与有理数":"fushu_yu_youlishu",
        "统计与概率":"tongji_yu_gailv","整式与方程":"zhengshi_yu_fangcheng",
        "几何基础":"jihe_jichu","统计初步":"tongji_chubu","整式与因式分解":"zhengshi_yu_yinshi_fenjie",
        "方程与不等式":"fangcheng_yu_budengshi","四边形":"sibianxing",
        "数据的波动":"shuju_de_bodong","二次根式与方程":"erci_genshi_yu_fangcheng",
        "锐角三角函数":"rui jiao_sanjiao_hanshu","集合与函数":"jihe_yu_hanshu",
        "不等式与逻辑":"budengshi_yu_luoji","向量与空间几何":"xiangliang_yu_kongjian_jihe",
        "常微分方程":"changweifen_fangcheng","偏微分方程":"pianweifen_fangcheng",
        "实变与复变函数":"shibian_yu_fubian_hanshu","初等数论":"chudeng_shulun",
        "动力系统":"dongli_xitong","数值分析":"shuzhi_fenxi","概率论":"gailvlun",
        "数理统计":"shuli_tongji","拓扑学":"tuopuxue","离散数学":"lisan_shuxue",
        "数学物理":"shuxue_wuli","球面三角与非欧几何":"qiumian_sanjiao_yu_feiou_jihe",
    }
    for zh, en in mapping.items():
        text = text.replace(zh, en)
    # 剩余中文转拼音首字母
    def pyinit(c):
        m = {'一':'yi','二':'er','三':'san','四':'si','五':'wu','六':'liu',
             '七':'qi','八':'ba','九':'jiu','十':'shi','零':'ling'}
        return m.get(c, c)
    result = ""
    for c in text:
        if '\u4e00' <= c <= '\u9fff':
            result += pyinit(c)
        elif c.isalnum():
            result += c.lower()
        elif c in " _-":
            result += "_"
    result = re.sub(r'_+', '_', result).strip('_')
    return result

# ─────────────────────────────────────────────────
# 章节定义：原始名 → (level, 默认学期)
# ─────────────────────────────────────────────────
CHAPTER_DEFS = [
    # primary
    ("数与运算",       "primary",   "上", "ch_shuyu_yunsuan",    "一年级", "上"),
    ("时间与货币",     "primary",   "上", "ch_shijian_yu_huobi",  "一年级", "上"),
    ("分类与统计",     "primary",   "上", "ch_fenlei_yu_tongji",  "一年级", "上"),
    ("图形与长度",     "primary",   "上", "ch_tuxiang_yu_changdu","三年级", "上"),
    ("时间",           "primary",   "上", "ch_shijian",            "二年级", "上"),
    ("分数初步",       "primary",   "上", "ch_fenshu_chubu",       "三年级", "上"),
    ("面积测量",       "primary",   "上", "ch_mianji_celiang",     "五年级", "上"),
    ("图形认识",       "primary",   "上", "ch_tuxiang_renshi",     "一年级", "上"),
    ("时间与方向",     "primary",   "上", "ch_shijian_yu_fangxiang","二年级","上"),
    ("角与四边形",     "primary",   "上", "ch_jiao_yu_sibianxing", "四年级", "上"),
    ("统计与面积",     "primary",   "上", "ch_tongji_yu_mianji",   "三年级", "上"),
    ("小数",           "primary",   "上", "ch_xiaoshu",            "四年级", "上"),
    ("因数与倍数",     "primary",   "上", "ch_yinshu_yu_beishu",   "五年级", "上"),
    ("图形变换与坐标", "primary",   "上", "ch_tuxiang_bianhuan_zuobiao","五年级","上"),
    ("圆",             "primary",   "上", "ch_yuan",               "六年级", "上"),
    ("百分数与比例",   "primary",   "上", "ch_baifenshu_yu_bili",   "六年级", "上"),
    ("负数与有理数",   "primary",   "上", "ch_fushu_yu_youlishu",  "六年级", "上"),
    ("统计与概率",     "primary",   "上", "ch_tongji_yu_gailv",    "六年级", "上"),
    # junior
    ("整式与方程",     "junior",    "上", "ch_zhengshi_yu_fangcheng",  "七年级","上"),
    ("几何基础",       "junior",    "上", "ch_jihe_jichu",              "七年级","上"),
    ("统计初步",       "junior",    "上", "ch_tongji_chubu",            "七年级","上"),
    ("方程与不等式",   "junior",    "上", "ch_fangcheng_yu_budengshi",  "七年级","上"),
    ("四边形",         "junior",    "上", "ch_sibianxing",              "七年级","上"),
    ("整式与因式分解", "junior",    "上", "ch_zhengshi_yu_yinshi_fenjie","八年级","上"),
    ("数据的波动",     "junior",    "上", "ch_shuju_de_bodong",         "八年级","上"),
    ("二次根式与方程", "junior",    "上", "ch_erci_genshi_yu_fangcheng","九年级","上"),
    ("锐角三角函数",   "junior",    "上", "ch_ruijiao_sanjiao_hanshu",  "九年级","上"),
    # senior
    ("集合与函数",     "senior",    "上", "ch_jihe_yu_hanshu",    "高一", "上"),
    ("不等式与逻辑",   "senior",    "上", "ch_budengshi_yu_luoji", "高一", "上"),
    ("向量与空间几何", "senior",    "上", "ch_xiangliang_yu_kongjian","高一","上"),
    # undergrad
    ("常微分方程",     "undergrad", "上", "ch_changweifen_fangcheng","大一","上"),
    ("偏微分方程",     "undergrad", "上", "ch_pianweifen_fangcheng",   "大一","上"),
    ("实变与复变函数", "undergrad", "上", "ch_shibian_fubian_hanshu",  "大一","上"),
    ("初等数论",       "undergrad", "上", "ch_chudeng_shulun",         "大一","上"),
    ("动力系统",       "undergrad", "上", "ch_dongli_xitong",           "大二","上"),
    ("数值分析",       "undergrad", "上", "ch_shuzhi_fenxi",            "大二","上"),
    ("概率论",         "undergrad", "上", "ch_gailvlun",                "大一","上"),
    ("数理统计",       "undergrad", "上", "ch_shuli_tongji",            "大二","上"),
    ("拓扑学",         "undergrad", "上", "ch_tuopuxue",                "大二","上"),
    ("离散数学",       "undergrad", "上", "ch_lisan_shuxue",            "大一","上"),
    ("数学物理",       "undergrad", "上", "ch_shuxue_wuli",             "大三","上"),
    ("球面三角与非欧几何","undergrad","上","ch_qiumian_feiou_jihe",      "大三","上"),
]

# ─────────────────────────────────────────────────
# 章节先修链（年级内、年级间）
# ─────────────────────────────────────────────────
CHAPTER_PREREQS = [
    # primary 一年级 → 二年级
    ("ch_shijiande", "ch_shijian"),
    ("ch_tuxiang_renshi", "ch_shuyu_yunsuan"),
    ("ch_shijian", "ch_shijian_yu_fangxiang"),
    # primary 二年级 → 三年级
    ("ch_shijian_yu_fangxiang", "ch_fenshu_chubu"),
    ("ch_shijian_yu_fangxiang", "ch_tongji_yu_mianji"),
    ("ch_shuyu_yunsuan", "ch_fenshu_chubu"),
    ("ch_tuxiang_yu_changdu", "ch_fenshu_chubu"),
    ("ch_tuxiang_yu_changdu", "ch_tongji_yu_mianji"),
    # primary 三年级 → 四年级
    ("ch_fenshu_chubu", "ch_xiaoshu"),
    ("ch_jiao_yu_sibianxing", "ch_xiaoshu"),
    ("ch_tongji_yu_mianji", "ch_tuxiang_bianhuan_zuobiao"),
    # primary 四年级 → 五年级
    ("ch_xiaoshu", "ch_yinshu_yu_beishu"),
    ("ch_jiao_yu_sibianxing", "ch_mianji_celiang"),
    # primary 五年级 → 六年级
    ("ch_yinshu_yu_beishu", "ch_baifenshu_yu_bili"),
    ("ch_mianji_celiang", "ch_baifenshu_yu_bili"),
    ("ch_tuxiang_bianhuan_zuobiao", "ch_yuan"),
    ("ch_xiaoshu", "ch_baifenshu_yu_bili"),
    # primary 六年级 → junior 七年级
    ("ch_fushu_yu_youlishu", "ch_zhengshi_yu_fangcheng"),
    ("ch_baifenshu_yu_bili", "ch_fangcheng_yu_budengshi"),
    ("ch_tongji_yu_gailv", "ch_tongji_chubu"),
    # junior 七年级 → 八年级
    ("ch_zhengshi_yu_fangcheng", "ch_zhengshi_yu_yinshi_fenjie"),
    ("ch_jihe_jichu", "ch_sibianxing"),
    ("ch_fangcheng_yu_budengshi", "ch_sibianxing"),
    ("ch_tongji_chubu", "ch_shuju_de_bodong"),
    # junior 八年级 → 九年级
    ("ch_zhengshi_yu_yinshi_fenjie", "ch_erci_genshi_yu_fangcheng"),
    ("ch_erci_genshi_yu_fangcheng", "ch_ruijiao_sanjiao_hanshu"),
    ("ch_sibianxing", "ch_ruijiao_sanjiao_hanshu"),
    # junior 九年级 → senior 高一
    ("ch_fangcheng_yu_budengshi", "ch_jihe_yu_hanshu"),
    ("ch_ruijiao_sanjiao_hanshu", "ch_jihe_yu_hanshu"),
    ("ch_jihe_jichu", "ch_budengshi_yu_luoji"),
    ("ch_shuju_de_bodong", "ch_xiangliang_yu_kongjian"),
    # senior 高一 → 高二
    ("ch_jihe_yu_hanshu", "ch_budengshi_yu_luoji"),
    ("ch_xiangliang_yu_kongjian", "ch_budengshi_yu_luoji"),
    # senior 高二 → 高三 (无具体章节，用 undergrad 入口)
    ("ch_budengshi_yu_luoji", "ch_changweifen_fangcheng"),
    # undergrad
    ("ch_changweifen_fangcheng", "ch_pianweifen_fangcheng"),
    ("ch_shibian_fubian_hanshu", "ch_changweifen_fangcheng"),
    ("ch_shibian_fubian_hanshu", "ch_pianweifen_fangcheng"),
    ("ch_changweifen_fangcheng", "ch_dongli_xitong"),
    ("ch_shuzhi_fenxi", "ch_pianweifen_fangcheng"),
    ("ch_changweifen_fangcheng", "ch_gailvlun"),
    ("ch_gailvlun", "ch_shuli_tongji"),
    ("ch_shuzhi_fenxi", "ch_shuli_tongji"),
    ("ch_chudeng_shulun", "ch_tuopuxue"),
    ("ch_chudeng_shulun", "ch_lisan_shuxue"),
    ("ch_lisan_shuxue", "ch_tuopuxue"),
    ("ch_pianweifen_fangcheng", "ch_shuxue_wuli"),
    ("ch_shibian_fubian_hanshu", "ch_qiumian_feiou_jihe"),
    ("ch_pianweifen_fangcheng", "ch_qiumian_feiou_jihe"),
]

# ─────────────────────────────────────────────────
# 主逻辑
# ─────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  章节层次建模重构脚本")
    print("=" * 60)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data['nodes']
    existing_ids = {n['id'] for n in nodes}
    id_to_node = {n['id']: n for n in nodes}

    # ── 第0步: 收集现有章节节点，看它们prerequisites里引用了什么 ──
    # 先修边里引用旧章节ID → 新章节ID 的映射
    # 我们还不知道新ID，所以先收集旧ID对应的新ID
    old_to_new = {}
    dedup_map = {}  # (name_zh, level) → canonical_id

    for name_zh, level, semester, new_id, grade, sem in CHAPTER_DEFS:
        dedup_map[(name_zh, level)] = new_id

    # 从CHAPTER_DEFS构建: 原始名+level → 新ID
    name_level_to_newid = {}
    for name_zh, level, semester, new_id, grade, sem in CHAPTER_DEFS:
        name_level_to_newid[(name_zh, level)] = new_id

    # 分析现有chapter节点，推断其grade
    old_chapters = [n for n in nodes if n.get('type') == 'chapter']
    print(f"\n📊 现有章节: {len(old_chapters)} 个（含重复）")

    # ── 第1步: 构建 old_id → new_id 映射 ──
    # 从现有chapter节点，从ID里解析suffix推断grade
    for ch in old_chapters:
        old_id = ch['id']
        name_zh = ch.get('name', {}).get('zh', '')
        level = ch.get('level', '')
        # 找对应的CHAPTER_DEF
        matched_new_id = None
        for (def_name, def_level, def_sem, def_newid, def_grade, def_sem2) in CHAPTER_DEFS:
            if def_name == name_zh and def_level == level:
                matched_new_id = def_newid
                break
        if matched_new_id:
            old_to_new[old_id] = matched_new_id

    print(f"\n📦 旧章节 → 新章节映射:")
    seen = set()
    for old_id, new_id in sorted(old_to_new.items()):
        if new_id not in seen:
            print(f"   {old_id} → {new_id}")
            seen.add(new_id)

    # ── 第2步: 删除旧章节节点 ──
    print("\n🗑️  第2步: 删除旧章节节点")
    old_ids_to_remove = set(old_to_new.keys())
    new_chapter_ids = set(old_to_new.values())  # 这些是新章节ID
    nodes_before = len(nodes)
    nodes = [n for n in nodes if n['id'] not in old_ids_to_remove]
    print(f"   删除 {nodes_before - len(nodes)} 个旧章节节点")

    # ── 第3步: 创建新的规范章节节点 ──
    print("\n🏗️  第3步: 创建规范章节节点")
    new_chapters = []
    for name_zh, level, semester, new_id, grade, sem in CHAPTER_DEFS:
        node = {
            "id": new_id,
            "type": "chapter",
            "name": {"zh": name_zh, "en": name_zh},
            "description": {
                "zh": f"{grade}{sem}学期 — {name_zh}",
                "en": f"Grade {grade}, Semester {sem} — {name_zh}"
            },
            "level": level,
            "grade": grade,
            "semester": sem,
            "tags": ["chapter"],
            "prerequisites": [],
            "difficulty": 3,
            "importance": 9,
            "estimated_minutes": 180
        }
        new_chapters.append(node)
    print(f"   新建 {len(new_chapters)} 个章节节点")
    nodes.extend(new_chapters)

    # ── 第4步: 修复知识点节点中的旧章节引用 ──
    print("\n🔧 第4步: 修复知识点中的旧章节引用")
    fix_count = 0
    id_to_node = {n['id']: n for n in nodes}
    for n in nodes:
        if n.get('type') == 'chapter':
            continue
        old_pre = list(n.get('prerequisites', []))
        new_pre = []
        for p in old_pre:
            if p in old_to_new:
                new_p = old_to_new[p]
                if new_p not in new_pre:
                    new_pre.append(new_p)
                fix_count += 1
            elif p in existing_ids and p not in old_ids_to_remove:
                new_pre.append(p)
        n['prerequisites'] = new_pre

    # 清理不存在的prerequisite引用
    all_ids = {n['id'] for n in nodes}
    for n in nodes:
        valid = [p for p in n.get('prerequisites', []) if p in all_ids]
        removed = len(n.get('prerequisites', [])) - len(valid)
        if removed:
            n['prerequisites'] = valid
    print(f"   修复引用: {fix_count} 条 → 新章节ID")

    # ── 第5步: 构建章节先修链 ──
    print("\n🔗 第5步: 构建章节先修链")
    id_to_node = {n['id']: n for n in nodes}
    cp_count = 0
    for (fid, tid) in CHAPTER_PREREQS:
        if fid not in id_to_node or tid not in id_to_node:
            continue
        tn = id_to_node.get(tid)
        if tn and fid not in tn.get('prerequisites', []):
            tn.setdefault('prerequisites', []).append(fid)
            cp_count += 1
    print(f"   章节先修链: {cp_count} 条")

    # ── 第6步: 为知识点节点建立归属星形边 ──
    print("\n⭐ 第6步: 建立知识点归属星形边")
    assign_count = 0
    for n in nodes:
        if n.get('type') == 'chapter':
            continue
        # 已有prerequisite（知识点→章节）则跳过
        ch_ids = [p for p in n.get('prerequisites', []) if p.startswith('ch_')]
        if ch_ids:
            continue
        # 根据level推断章节
        level = n.get('level', '')
        grade = n.get('grade', '')
        # 找最近的章节
        # 年级→章节映射
        grade_to_ch = {}
        for (def_name, def_level, def_sem, def_newid, def_grade, def_sem2) in CHAPTER_DEFS:
            grade_to_ch[(def_level, def_grade)] = def_newid
        # 同级节点已有章节的用那个
        ch_candidate = None
        for ch in new_chapters:
            if ch['level'] == level:
                ch_candidate = ch['id']
                break
        if ch_candidate and ch_candidate not in n.get('prerequisites', []):
            n.setdefault('prerequisites', []).append(ch_candidate)
            assign_count += 1
    print(f"   新增归属边: {assign_count} 条")

    # ── 第7步: 统计 ──
    all_ids = {n['id'] for n in nodes}
    total_edges = sum(len(n.get('prerequisites', [])) for n in nodes)
    iso = sum(1 for n in nodes
        if n.get('type') != 'chapter'
        and not n.get('prerequisites', [])
        and not any(n['id'] in p.get('prerequisites', []) for p in nodes))

    k12_iso = sum(1 for n in nodes
        if n.get('type') != 'chapter'
        and n.get('level', '') in ('primary', 'junior', 'senior')
        and not n.get('prerequisites', [])
        and not any(n['id'] in p.get('prerequisites', []) for p in nodes))

    print(f"\n📈 重构后统计:")
    print(f"   总节点: {len(nodes)}")
    print(f"   总边数: {total_edges}")
    print(f"   平均边数: {total_edges/len(nodes):.1f}")
    print(f"   章节节点: {len(new_chapters)}")
    print(f"   K12孤立: {k12_iso}")

    # ── 第8步: 保存 ──
    data['nodes'] = nodes
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 数据已保存到: {DATA_FILE}")

if __name__ == '__main__':
    main()

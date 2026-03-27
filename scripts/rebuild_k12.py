#!/usr/bin/env python3
"""重建K12章节和知识点"""
import json, os

FP = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"
BACKUP = f"/tmp/kg_backup_{os.popen('date +%s').read().strip()}.json"

# 加载现有数据
try:
    with open(FP) as f:
        data = json.load(f)
    with open(BACKUP, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"备份到 {BACKUP}")
except Exception as e:
    print(f"加载失败: {e}")
    data = {"nodes": []}

nodes = data.get("nodes", [])
node_ids = {n["id"] for n in nodes}

def add_node(n):
    if n["id"] not in node_ids:
        nodes.append(n)
        node_ids.add(n["id"])
        return True
    return False

# ===== 章节 =====
CHAPTERS = [
    ("ch_p1_numbers","数与运算","小学一年级","上",[]),
    ("ch_p1_shapes","图形与几何","小学一年级","上",["ch_p1_numbers"]),
    ("ch_p1_classify","分类与整理","小学一年级","上",[]),
    ("ch_p1b_numbers","数与运算","小学一年级","下",["ch_p1_numbers"]),
    ("ch_p1b_shapes","图形与几何","小学一年级","下",["ch_p1_shapes"]),
    ("ch_p2_mul","表内乘法","小学二年级","上",["ch_p1b_numbers"]),
    ("ch_p2_angle","角的认识","小学二年级","上",["ch_p1_shapes"]),
    ("ch_p2_time","时间","小学二年级","上",[]),
    ("ch_p2b_div","表内除法","小学二年级","下",["ch_p2_mul"]),
    ("ch_p2b_money","认识人民币","小学二年级","下",[]),
    ("ch_p2b_measure","测量","小学二年级","下",["ch_p2_angle"]),
    ("ch_p3_mul","多位数乘一位数","小学三年级","上",["ch_p2_mul"]),
    ("ch_p3_frac","分数的初步","小学三年级","上",["ch_p1b_numbers"]),
    ("ch_p3_measure","测量","小学三年级","上",["ch_p2b_measure"]),
    ("ch_p3b_div","两位数除一位数","小学三年级","下",["ch_p3_mul"]),
    ("ch_p3b_area","面积","小学三年级","下",["ch_p3_measure"]),
    ("ch_p3b_frac","同分母分数加减","小学三年级","下",["ch_p3_frac"]),
    ("ch_p4_bignum","大数的认识","小学四年级","上",["ch_p3_mul"]),
    ("ch_p4_angle","角的度量","小学四年级","上",["ch_p2_angle"]),
    ("ch_p4_decimal","小数的意义","小学四年级","下",["ch_p3_frac"]),
    ("ch_p4b_div","三位数除两位数","小学四年级","下",["ch_p4_bignum"]),
    ("ch_p4b_tri","三角形","小学四年级","下",["ch_p4_angle"]),
    ("ch_p5_factor","因数与倍数","小学五年级","上",["ch_p4_bignum"]),
    ("ch_p5_frac","分数加减","小学五年级","上",["ch_p3b_frac"]),
    ("ch_p5_decimal","小数乘除","小学五年级","下",["ch_p4_decimal"]),
    ("ch_p5_frac_mul","分数乘法","小学五年级","下",["ch_p5_frac"]),
    ("ch_p5_frac_div","分数除法","小学五年级","下",["ch_p5_frac_mul"]),
    ("ch_p6_ratio","比","小学六年级","上",["ch_p5_frac_mul"]),
    ("ch_p6_percent","百分数","小学六年级","上",["ch_p5_frac_mul"]),
    ("ch_p6_circle","圆","小学六年级","上",["ch_p3b_area"]),
    ("ch_p6b_equ","比例与方程","小学六年级","下",["ch_p6_ratio"]),
    ("ch_p6b_neg","负数","小学六年级","下",["ch_p4_bignum"]),
    ("ch_p6b_cyl","圆柱与圆锥","小学六年级","下",["ch_p6_circle"]),
    ("ch_j7_rat","有理数","初中一年级","上",["ch_p6b_neg"]),
    ("ch_j7_exp","整式","初中一年级","上",["ch_j7_rat"]),
    ("ch_j7_eq","一元一次方程","初中一年级","上",["ch_j7_exp"]),
    ("ch_j7_geo","几何图形初步","初中一年级","上",["ch_p4_angle"]),
    ("ch_j7b_sys","二元一次方程组","初中一年级","下",["ch_j7_eq"]),
    ("ch_j7b_ineq","不等式","初中一年级","下",["ch_j7_eq"]),
    ("ch_j7b_para","相交线与平行线","初中一年级","下",["ch_j7_geo"]),
    ("ch_j8_cong","全等三角形","初中二年级","上",["ch_j7_geo"]),
    ("ch_j8_axis","轴对称","初中二年级","上",["ch_j8_cong"]),
    ("ch_j8_fact","因式分解","初中二年级","上",["ch_j7_exp"]),
    ("ch_j8b_func","一次函数","初中二年级","下",["ch_j7_eq"]),
    ("ch_j8b_quad","一元二次方程","初中二年级","下",["ch_j8_fact"]),
    ("ch_j8b_para4","平行四边形","初中二年级","下",["ch_j8_cong"]),
    ("ch_j9_qf","二次函数","初中三年级","上",["ch_j8b_func"]),
    ("ch_j9_circ","圆","初中三年级","上",["ch_j8_cong"]),
    ("ch_j9_simi","相似","初中三年级","上",["ch_j9_circ"]),
    ("ch_j9b_trig","锐角三角函数","初中三年级","下",["ch_j9_simi"]),
    ("ch_j9b_prob","概率","初中三年级","下",["ch_j7b_ineq"]),
    ("ch_h10_set","集合","高中一年级","上",["ch_j7_rat"]),
    ("ch_h10_func","函数","高中一年级","上",["ch_h10_set"]),
    ("ch_h10_el","指数函数与对数函数","高中一年级","上",["ch_h10_func"]),
    ("ch_h10_trig","三角函数","高中一年级","上",["ch_j9b_trig"]),
    ("ch_h10b_vec","平面向量","高中一年级","下",["ch_h10_func"]),
    ("ch_h10b_seq","数列","高中一年级","下",["ch_h10_func"]),
    ("ch_h11_ineq","不等式","高中二年级","上",["ch_h10_func"]),
    ("ch_h11_der","导数","高中二年级","上",["ch_h10_func"]),
    ("ch_h11_prob","概率统计","高中二年级","上",["ch_j9b_prob"]),
    ("ch_h11b_an","平面解析几何","高中二年级","下",["ch_h11_ineq"]),
    ("ch_h11b_comp","复数","高中二年级","下",["ch_h11_ineq"]),
    ("ch_h12_space","空间向量","高中三年级","上",["ch_h10b_vec"]),
    ("ch_h12_conic","圆锥曲线","高中三年级","上",["ch_h11b_an"]),
    ("ch_h12b_rev","高考综合复习","高中三年级","下",["ch_h12_space","ch_h12_conic"]),
]

# 添加章节
ch_added = 0
chapter_ids = set()
for chid, name, grade, sem, prereqs in CHAPTERS:
    if add_node({
        "id": chid, "type": "chapter",
        "name": {"zh": name, "en": name},
        "description": {"zh": f"{name}（{grade}{sem}学期）", "en": name},
        "level": grade, "branch": "chapters",
        "tags": [grade, "数学", "章节"],
        "prerequisites": prereqs,
        "difficulty": 2, "importance": 9,
        "grade": grade, "semester": sem,
        "estimated_minutes": 60,
    }):
        ch_added += 1
    chapter_ids.add(chid)

print(f"添加章节: {ch_added} 个")

# ===== 知识节点 =====
def kn(chid, kid, zh, en, prereqs, grade):
    if kid in node_ids:
        return
    add_node({
        "id": kid, "type": "concept",
        "name": {"zh": zh, "en": en},
        "description": {"zh": zh, "en": en},
        "level": grade, "branch": "math",
        "tags": [grade, "数学"],
        "prerequisites": prereqs,
        "difficulty": 3, "importance": 8,
        "chapter": chid, "estimated_minutes": 60,
    })

# 一年级上：数
kn("ch_p1_numbers","k_p1n1","1-5的认识","numbers 1-5",[],"小学一年级")
kn("ch_p1_numbers","k_p1n2","6-10的认识","numbers 6-10",["k_p1n1"],"小学一年级")
kn("ch_p1_numbers","k_p1n3","11-20的认识","numbers 11-20",["k_p1n2"],"小学一年级")
kn("ch_p1_numbers","k_p1n4","比大小","compare sizes",[],"小学一年级")
kn("ch_p1_numbers","k_p1n5","5以内加法","addition within 5",[],"小学一年级")
kn("ch_p1_numbers","k_p1n6","5以内减法","subtraction within 5",["k_p1n5"],"小学一年级")
kn("ch_p1_numbers","k_p1n7","10以内加法","addition within 10",["k_p1n5","k_p1n6"],"小学一年级")
kn("ch_p1_numbers","k_p1n8","10以内减法","subtraction within 10",["k_p1n6","k_p1n7"],"小学一年级")
kn("ch_p1_numbers","k_p1n9","0的认识","understanding zero",["k_p1n1"],"小学一年级")
kn("ch_p1_numbers","k_p1n10","加减法的关系","addition subtraction relation",["k_p1n7","k_p1n8"],"小学一年级")
kn("ch_p1_numbers","k_p1n11","一图四式","one picture four expressions",["k_p1n7","k_p1n8"],"小学一年级")
kn("ch_p1_numbers","k_p1n12","用加法解决问题（合并）","solve merge problems",["k_p1n7"],"小学一年级")
kn("ch_p1_numbers","k_p1n13","用减法解决问题（拿走）","solve take away problems",["k_p1n8"],"小学一年级")
kn("ch_p1_numbers","k_p1n14","序数和基数","ordinals cardinals",["k_p1n3"],"小学一年级")
kn("ch_p1_numbers","k_p1n15","排队问题","queue problems",["k_p1n14"],"小学一年级")
# 一年级上：图形
kn("ch_p1_shapes","k_p1s1","认识正方形","recognize square",[],"小学一年级")
kn("ch_p1_shapes","k_p1s2","认识长方形","recognize rectangle",[],"小学一年级")
kn("ch_p1_shapes","k_p1s3","认识三角形","recognize triangle",["k_p1s1"],"小学一年级")
kn("ch_p1_shapes","k_p1s4","认识圆形","recognize circle",[],"小学一年级")
kn("ch_p1_shapes","k_p1s5","认识立体图形","recognize solid figures",["k_p1s1","k_p1s2","k_p1s3","k_p1s4"],"小学一年级")
kn("ch_p1_shapes","k_p1s6","用方块堆物体","stack blocks",["k_p1s5"],"小学一年级")
kn("ch_p1_shapes","k_p1s7","用方块画图形","draw shapes with blocks",["k_p1s5"],"小学一年级")
kn("ch_p1_shapes","k_p1s8","认识前后上下","front back up down",[],"小学一年级")
kn("ch_p1_shapes","k_p1s9","认识左右","left right",["k_p1s8"],"小学一年级")
# 一年级上：分类
kn("ch_p1_classify","k_p1c1","按颜色分类","classify by color",[],"小学一年级")
kn("ch_p1_classify","k_p1c2","按形状分类","classify by shape",[],"小学一年级")
kn("ch_p1_classify","k_p1c3","按大小分类","classify by size",[],"小学一年级")
kn("ch_p1_classify","k_p1c4","简单统计表","simple tally",["k_p1c1","k_p1c2","k_p1c3"],"小学一年级")
kn("ch_p1_classify","k_p1c5","可能性的大小","probability",["k_p1c3"],"小学一年级")
# 一年级下：数
kn("ch_p1b_numbers","k_p1bn1","20以内进位加法","carry addition 20",["k_p1n7"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn2","20以内退位减法","borrow subtraction 20",["k_p1n8"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn3","解决问题（求和）","solve sum problems",["k_p1bn1"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn4","解决问题（求剩余）","solve remainder problems",["k_p1bn2"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn5","连加连减","consecutive add subtract",["k_p1bn1","k_p1bn2"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn6","加减混合运算","mixed add subtract",["k_p1bn5"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn7","认识括号","understand brackets",["k_p1bn5"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn8","100以内数的认识","numbers within 100",["k_p1n3"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn9","数的组成","composition of number",["k_p1bn8"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn10","比较数的大小","compare numbers",["k_p1bn8"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn11","认识个位和十位","ones tens",["k_p1bn8"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn12","整十数加一位数","tens plus ones",["k_p1bn11"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn13","整十数加减整十数","tens add subtract tens",["k_p1bn12"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn14","两位数加一位数","2-digit plus 1-digit",["k_p1bn11","k_p1bn1"],"小学一年级")
kn("ch_p1b_numbers","k_p1bn15","两位数加两位数","2-digit plus 2-digit",["k_p1bn14"],"小学一年级")

# 二年级上：乘法
kn("ch_p2_mul","k_p2m1","乘法的意义","meaning of multiplication",["k_p1n5","k_p1n6"],"小学二年级")
kn("ch_p2_mul","k_p2m2","乘号","multiplication sign",["k_p2m1"],"小学二年级")
kn("ch_p2_mul","k_p2m3","1的乘法口诀","1 times table",["k_p2m2"],"小学二年级")
kn("ch_p2_mul","k_p2m4","2的乘法口诀","2 times table",["k_p2m3"],"小学二年级")
kn("ch_p2_mul","k_p2m5","3的乘法口诀","3 times table",["k_p2m4"],"小学二年级")
kn("ch_p2_mul","k_p2m6","4的乘法口诀","4 times table",["k_p2m5"],"小学二年级")
kn("ch_p2_mul","k_p2m7","5的乘法口诀","5 times table",["k_p2m6"],"小学二年级")
kn("ch_p2_mul","k_p2m8","乘加乘减","multiply then add subtract",["k_p2m7"],"小学二年级")
kn("ch_p2_mul","k_p2m9","6的乘法口诀","6 times table",["k_p2m7","k_p2m8"],"小学二年级")
kn("ch_p2_mul","k_p2m10","7的乘法口诀","7 times table",["k_p2m9"],"小学二年级")
kn("ch_p2_mul","k_p2m11","8的乘法口诀","8 times table",["k_p2m10"],"小学二年级")
kn("ch_p2_mul","k_p2m12","9的乘法口诀","9 times table",["k_p2m11"],"小学二年级")
kn("ch_p2_mul","k_p2m13","用乘法解决问题","word problems multiplication",["k_p2m7"],"小学二年级")
# 二年级上：角
kn("ch_p2_angle","k_p2a1","角的认识","understanding angle",["k_p1s1"],"小学二年级")
kn("ch_p2_angle","k_p2a2","画角","draw angle",["k_p2a1"],"小学二年级")
kn("ch_p2_angle","k_p2a3","认识直角","recognize right angle",["k_p2a1"],"小学二年级")
kn("ch_p2_angle","k_p2a4","认识锐角和钝角","acute obtuse angles",["k_p2a3"],"小学二年级")
kn("ch_p2_angle","k_p2a5","比角的大小","compare angles",["k_p2a3","k_p2a4"],"小学二年级")
# 二年级上：时间
kn("ch_p2_time","k_p2t1","认识整时","recognize o clock",[],"小学二年级")
kn("ch_p2_time","k_p2t2","认识半时","recognize half hour",["k_p2t1"],"小学二年级")
kn("ch_p2_time","k_p2t3","认识几时几分","recognize time",["k_p2t2"],"小学二年级")
kn("ch_p2_time","k_p2t4","24时计时法","24 hour clock",["k_p2t1"],"小学二年级")
kn("ch_p2_time","k_p2t5","计算经过时间","elapsed time",["k_p2t3","k_p2t4"],"小学二年级")
# 二年级下：除法
kn("ch_p2b_div","k_p2d1","除法的意义","meaning of division",["k_p2m1"],"小学二年级")
kn("ch_p2b_div","k_p2d2","除号","division sign",["k_p2d1"],"小学二年级")
kn("ch_p2b_div","k_p2d3","平均分","divide equally",["k_p2d1"],"小学二年级")
kn("ch_p2b_div","k_p2d4","除法看图列式","division from pictures",["k_p2d3"],"小学二年级")
kn("ch_p2b_div","k_p2d5","用乘法想除法","use multiplication for division",["k_p2d4","k_p2m1"],"小学二年级")
kn("ch_p2b_div","k_p2d6","2-5的除法","division by 2-5",["k_p2d5"],"小学二年级")
kn("ch_p2b_div","k_p2d7","6的除法","division by 6",["k_p2d6","k_p2m9"],"小学二年级")
kn("ch_p2b_div","k_p2d8","7的除法","division by 7",["k_p2d7","k_p2m10"],"小学二年级")
kn("ch_p2b_div","k_p2d9","8的除法","division by 8",["k_p2d8","k_p2m11"],"小学二年级")
kn("ch_p2b_div","k_p2d10","9的除法","division by 9",["k_p2d9","k_p2m12"],"小学二年级")
kn("ch_p2b_div","k_p2d11","用除法解决问题","word problems division",["k_p2d10"],"小学二年级")
kn("ch_p2b_div","k_p2d12","有余数的除法","division with remainder",["k_p2d11"],"小学二年级")
kn("ch_p2b_div","k_p2d13","余数比除数小","remainder less than divisor",["k_p2d12"],"小学二年级")
kn("ch_p2b_div","k_p2d14","用有余数除法解决问题","solve remainder problems",["k_p2d13"],"小学二年级")
# 二年级下：人民币
kn("ch_p2b_money","k_p2rm1","认识人民币","recognize RMB",[],"小学二年级")
kn("ch_p2b_money","k_p2rm2","人民币换算","RMB exchange",["k_p2rm1"],"小学二年级")
kn("ch_p2b_money","k_p2rm3","元角分的计算","yuan jiao fen calculation",["k_p2rm2"],"小学二年级")
kn("ch_p2b_money","k_p2rm4","简单的计算","simple calculation",["k_p2rm3"],"小学二年级")
# 二年级下：测量
kn("ch_p2b_measure","k_p2me1","认识分米和毫米","decimeter millimeter",["k_p2a1"],"小学二年级")
kn("ch_p2b_measure","k_p2me2","长度单位换算","length unit conversion",["k_p2me1"],"小学二年级")
kn("ch_p2b_measure","k_p2me3","千米","kilometer",["k_p2me2"],"小学二年级")
kn("ch_p2b_measure","k_p2me4","认识吨","ton",["k_p2me1"],"小学二年级")
kn("ch_p2b_measure","k_p2me5","解决问题","solve measurement problems",["k_p2me2","k_p2me4"],"小学二年级")

# 三年级上：乘法
kn("ch_p3_mul","k_p3m1","整十数乘一位数","tens times 1-digit",["k_p2m7"],"小学三年级")
kn("ch_p3_mul","k_p3m2","两位数乘一位数不进位","2-digit times 1-digit no carry",["k_p3m1"],"小学三年级")
kn("ch_p3_mul","k_p3m3","两位数乘一位数进位","2-digit times 1-digit carry",["k_p3m2"],"小学三年级")
kn("ch_p3_mul","k_p3m4","三位数乘一位数","3-digit times 1-digit",["k_p3m3"],"小学三年级")
kn("ch_p3_mul","k_p3m5","有关0的乘法","multiplication with 0",["k_p3m4"],"小学三年级")
kn("ch_p3_mul","k_p3m6","中间有0的乘法","multiplication with 0 in middle",["k_p3m5"],"小学三年级")
kn("ch_p3_mul","k_p3m7","末尾有0的乘法","multiplication trailing 0",["k_p3m4"],"小学三年级")
kn("ch_p3_mul","k_p3m8","连乘","sequential multiplication",["k_p3m4"],"小学三年级")
kn("ch_p3_mul","k_p3m9","乘法估算","estimate multiplication",["k_p3m3"],"小学三年级")
kn("ch_p3_mul","k_p3m10","用乘法解决问题","word problems multiplication",["k_p3m4"],"小学三年级")
# 三年级上：分数
kn("ch_p3_frac","k_p3f1","几分之一的含义","meaning of unit fraction",["k_p1n5"],"小学三年级")
kn("ch_p3_frac","k_p3f2","几分之几","several over n",["k_p3f1"],"小学三年级")
kn("ch_p3_frac","k_p3f3","比较分数大小","compare fractions",["k_p3f2"],"小学三年级")
kn("ch_p3_frac","k_p3f4","同分母分数加法","same denominator addition",["k_p3f2"],"小学三年级")
kn("ch_p3_frac","k_p3f5","同分母分数减法","same denominator subtraction",["k_p3f4"],"小学三年级")
kn("ch_p3_frac","k_p3f6","1减几分之几","1 minus fraction",["k_p3f5"],"小学三年级")
kn("ch_p3_frac","k_p3f7","分数的简单应用","simple fraction applications",["k_p3f4","k_p3f5"],"小学三年级")
# 三年级上：测量
kn("ch_p3_measure","k_p3me1","毫米的认识","millimeter",["k_p2me1"],"小学三年级")
kn("ch_p3_measure","k_p3me2","分米的认识","decimeter",["k_p3me1"],"小学三年级")
kn("ch_p3_measure","k_p3me3","千米的认识","kilometer",["k_p3me2"],"小学三年级")
kn("ch_p3_measure","k_p3me4","长度单位换算","length unit conversion",["k_p3me1","k_p3me2","k_p3me3"],"小学三年级")
kn("ch_p3_measure","k_p3me5","估计长度","estimate length",["k_p3me4"],"小学三年级")
kn("ch_p3_measure","k_p3me6","吨和千克","ton kilogram",["k_p2me4"],"小学三年级")
# 三年级下：除法
kn("ch_p3b_div","k_p3d1","一位数除两位数商一位数","1-digit divisor 2-digit 1-quotient",["k_p2d11"],"小学三年级")
kn("ch_p3b_div","k_p3d2","一位数除三位数","1-digit divisor 3-digit",["k_p3d1"],"小学三年级")
kn("ch_p3b_div","k_p3d3","除法的验算","verify division",["k_p3d2"],"小学三年级")
kn("ch_p3b_div","k_p3d4","商中间有0的除法","division with 0 in quotient",["k_p3d3"],"小学三年级")
kn("ch_p3b_div","k_p3d5","商末尾有0的除法","division trailing 0 quotient",["k_p3d4"],"小学三年级")
kn("ch_p3b_div","k_p3d6","用除法解决问题","word problems division",["k_p3d5"],"小学三年级")
# 三年级下：面积
kn("ch_p3b_area","k_p3a1","面积的含义","meaning of area",["ch_p3_measure"],"小学三年级")
kn("ch_p3_area","k_p3a2","平方厘米","square centimeter",["k_p3a1"],"小学三年级")
kn("ch_p3_area","k_p3a3","平方分米","square decimeter",["k_p3a2"],"小学三年级")
kn("ch_p3_area","k_p3a4","平方米","square meter",["k_p3a3"],"小学三年级")
kn("ch_p3_area","k_p3a5","面积单位换算","area unit conversion",["k_p3a2","k_p3a3","k_p3a4"],"小学三年级")
kn("ch_p3_area","k_p3a6","长方形面积公式","rectangle area formula",["k_p3a5"],"小学三年级")
kn("ch_p3_area","k_p3a7","正方形面积公式","square area formula",["k_p3a6"],"小学三年级")
kn("ch_p3_area","k_p3a8","组合图形面积","combined figure area",["k_p3a6","k_p3a7"],"小学三年级")
# 三年级下：分数
kn("ch_p3b_frac","k_p3ff1","同分母分数比较大小","compare same denom fractions",["k_p3f3"],"小学三年级")
kn("ch_p3b_frac","k_p3ff2","异分母分数比较大小","compare diff denom fractions",["k_p3ff1"],"小学三年级")
kn("ch_p3b_frac","k_p3ff3","通分","common denominator",["k_p3ff2"],"小学三年级")
kn("ch_p3b_frac","k_p3ff4","异分母分数加法","different denominator addition",["k_p3ff3"],"小学三年级")
kn("ch_p3b_frac","k_p3ff5","异分母分数减法","different denominator subtraction",["k_p3ff4"],"小学三年级")
kn("ch_p3b_frac","k_p3ff6","分数加减混合运算","mixed fraction operations",["k_p3ff4","k_p3ff5"],"小学三年级")
kn("ch_p3b_frac","k_p3ff7","分数加减简便运算","fraction efficient operations",["k_p3ff6"],"小学三年级")

# 三年级下：除法
kn("ch_p3b_div","k_p3d_b1","一位数除两位数","1-digit divisor 2-digit",["k_p2d11"],"小学三年级")
kn("ch_p3b_div","k_p3d_b2","一位数除三位数","1-digit divisor 3-digit",["k_p3d_b1"],"小学三年级")
kn("ch_p3b_div","k_p3d_b3","商中间有0","division with 0",["k_p3d_b2"],"小学三年级")
kn("ch_p3b_div","k_p3d_b4","解决问题","solve problems",["k_p3d_b3"],"小学三年级")

# 四年级上
kn("ch_p4_bignum","k_p4b1","万以内数的认识","numbers within 10000",["k_p3_mul"],"小学四年级")
kn("ch_p4_bignum","k_p4b2","万以内数的大小比较","compare within 10000",["k_p4b1"],"小学四年级")
kn("ch_p4_bignum","k_p4b3","近似数","approximate number",["k_p4b1"],"小学四年级")
kn("ch_p4_bignum","k_p4b4","亿以内数的认识","numbers within 100 million",["k_p4b1"],"小学四年级")
kn("ch_p4_bignum","k_p4b5","亿以内数的读写","read write 100 million",["k_p4b4"],"小学四年级")
kn("ch_p4_bignum","k_p4b6","亿以内数的大小比较","compare 100 million",["k_p4b5"],"小学四年级")
kn("ch_p4_bignum","k_p4b7","亿以内数的近似数","approximate 100 million",["k_p4b6"],"小学四年级")

# 四年级上：角
kn("ch_p4_angle","k_p4a1","直线","straight line",["k_p2a1"],"小学四年级")
kn("ch_p4_angle","k_p4a2","射线","ray",["k_p4a1"],"小学四年级")
kn("ch_p4_angle","k_p4a3","线段","line segment",["k_p4a2"],"小学四年级")
kn("ch_p4_angle","k_p4a4","角的度量","measure angles",["k_p2a4"],"小学四年级")
kn("ch_p4_angle","k_p4a5","角的分类","classify angles",["k_p4a4"],"小学四年级")
kn("ch_p4_angle","k_p4a6","画角","draw angles",["k_p4a5"],"小学四年级")
kn("ch_p4_angle","k_p4a7","用量角器画角","draw with protractor",["k_p4a6"],"小学四年级")

# 四年级下：小数
kn("ch_p4_decimal","k_p4d1","小数的意义","meaning of decimal",["ch_p3_frac"],"小学四年级")
kn("ch_p4_decimal","k_p4d2","小数的计数单位","decimal place value",["k_p4d1"],"小学四年级")
kn("ch_p4_decimal","k_p4d3","小数的读写","read write decimals",["k_p4d2"],"小学四年级")
kn("ch_p4_decimal","k_p4d4","小数的大小比较","compare decimals",["k_p4d3"],"小学四年级")
kn("ch_p4_decimal","k_p4d5","小数的性质","properties of decimals",["k_p4d4"],"小学四年级")
kn("ch_p4_decimal","k_p4d6","小数点移动规律","decimal point movement",["k_p4d5"],"小学四年级")
kn("ch_p4_decimal","k_p4d7","单位换算","unit conversion",["k_p4d6"],"小学四年级")
kn("ch_p4_decimal","k_p4d8","小数的近似数","approximate decimals",["k_p4d3"],"小学四年级")
# 四年级下：除法
kn("ch_p4b_div","k_p4bd1","除数是整十数的除法","division by tens",["ch_p4_bignum"],"小学四年级")
kn("ch_p4b_div","k_p4bd2","除数是两位数的除法","division by 2-digit",["k_p4bd1"],"小学四年级")
kn("ch_p4b_div","k_p4bd3","试商","trial quotient",["k_p4bd2"],"小学四年级")
kn("ch_p4b_div","k_p4bd4","商的变化规律","quotient change pattern",["k_p4bd3"],"小学四年级")
kn("ch_p4b_div","k_p4bd5","商不变规律","quotient invariance",["k_p4bd4"],"小学四年级")
kn("ch_p4b_div","k_p4bd6","连除运算","consecutive division",["k_p4bd5"],"小学四年级")
kn("ch_p4b_div","k_p4bd7","用除法解决问题","solve division problems",["k_p4bd6"],"小学四年级")
# 四年级下：三角形
kn("ch_p4b_tri","k_p4bt1","三角形的认识","recognize triangle",["ch_p4_angle"],"小学四年级")
kn("ch_p4b_tri","k_p4bt2","三角形的分类","classify triangles",["k_p4bt1"],"小学四年级")
kn("ch_p4b_tri","k_p4bt3","三角形三边关系","triangle inequality",["k_p4bt1"],"小学四年级")
kn("ch_p4b_tri","k_p4bt4","三角形的内角和","triangle angle sum",["k_p4bt1"],"小学四年级")
kn("ch_p4b_tri","k_p4bt5","图形的密铺","tiling",
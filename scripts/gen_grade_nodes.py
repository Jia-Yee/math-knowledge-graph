#!/usr/bin/env python3
"""生成K12数学知识节点 - 按年级分布"""
import json, os
FP = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"
data = json.load(open(FP))
nodes = data["nodes"]
existing = {n["id"] for n in nodes}
node_map = {n["id"]: n for n in nodes}

def node(**kw):
    return kw

def add(n):
    if n["id"] not in existing:
        nodes.append(n); existing.add(n["id"]); node_map[n["id"]] = n

# 小学一年级：数
for kid,zh,en,prereqs in [
    ("k_p1n1","1-5的认识","numbers 1-5",[]),
    ("k_p1n2","6-10的认识","numbers 6-10",["k_p1n1"]),
    ("k_p1n3","11-20的认识","numbers 11-20",["k_p1n2"]),
    ("k_p1n4","比大小","compare sizes",["k_p1n1","k_p1n2","k_p1n3"]),
    ("k_p1n5","5以内加法","addition within 5",[]),
    ("k_p1n6","5以内减法","subtraction within 5",["k_p1n5"]),
    ("k_p1n7","10以内加法","addition within 10",["k_p1n5","k_p1n6"]),
    ("k_p1n8","10以内减法","subtraction within 10",["k_p1n6","k_p1n7"]),
    ("k_p1n9","0的认识","understanding zero",["k_p1n1"]),
    ("k_p1n10","加减法的关系","addition subtraction relation",["k_p1n7","k_p1n8"]),
    ("k_p1n11","一图四式","one picture four expressions",["k_p1n7","k_p1n8"]),
    ("k_p1n12","用加法解决问题（合并）","solve merge problems",["k_p1n7"]),
    ("k_p1n13","用减法解决问题（拿走）","solve take away problems",["k_p1n8"]),
    ("k_p1n14","序数和基数","ordinals cardinals",["k_p1n3"]),
    ("k_p1n15","用数学解决排队问题","solve queue problems",["k_p1n14"]),
    ("k_p1bn1","20以内进位加法","carry addition within 20",["k_p1n7"]),
    ("k_p1bn2","20以内退位减法","borrow subtraction within 20",["k_p1n8"]),
    ("k_p1bn3","解决问题（求和）","solve sum problems",["k_p1bn1"]),
    ("k_p1bn4","解决问题（求剩余）","solve remainder problems",["k_p1bn2"]),
    ("k_p1bn5","连加连减","consecutive add subtract",["k_p1bn1","k_p1bn2"]),
    ("k_p1bn6","加减混合运算","mixed add subtract",["k_p1bn5"]),
    ("k_p1bn7","认识括号","understand brackets",["k_p1bn5"]),
    ("k_p1bn8","100以内数的认识","numbers within 100",["k_p1n3"]),
    ("k_p1bn9","数的组成","composition of number",["k_p1bn8"]),
    ("k_p1bn10","比较数的大小","compare numbers",["k_p1bn8"]),
    ("k_p1bn11","认识个位和十位","ones and tens",["k_p1bn8"]),
    ("k_p1bn12","整十数加一位数","tens plus ones",["k_p1bn11"]),
    ("k_p1bn13","整十数加减整十数","tens add subtract",["k_p1bn12"]),
    ("k_p1bn14","两位数加一位数","2-digit plus 1-digit",["k_p1bn11","k_p1bn1"]),
    ("k_p1bn15","两位数加两位数","2-digit plus 2-digit",["k_p1bn14"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学一年级", branch="math", tags=["小学一年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p1_numbers", estimated_minutes=60))

# 一年级：图形
for kid,zh,en,prereqs in [
    ("k_p1s1","认识正方形","recognize square",[]),
    ("k_p1s2","认识长方形","recognize rectangle",[]),
    ("k_p1s3","认识三角形","recognize triangle",["k_p1s1"]),
    ("k_p1s4","认识圆形","recognize circle",[]),
    ("k_p1s5","认识立体图形","recognize solid figures",["k_p1s1","k_p1s2","k_p1s3","k_p1s4"]),
    ("k_p1s6","用方块堆物体","stack blocks",["k_p1s5"]),
    ("k_p1s7","用方块画图形","draw shapes with blocks",["k_p1s5"]),
    ("k_p1s8","认识前后上下","front back up down",[]),
    ("k_p1s9","认识左右","left and right",["k_p1s8"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学一年级", branch="math", tags=["小学一年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p1_shapes", estimated_minutes=60))

# 一年级：分类
for kid,zh,en,prereqs in [
    ("k_p1c1","按颜色分类","classify by color",[]),
    ("k_p1c2","按形状分类","classify by shape",["k_p1s1","k_p1s2","k_p1s3","k_p1s4"]),
    ("k_p1c3","按大小分类","classify by size",[]),
    ("k_p1c4","简单统计表","simple tally",["k_p1c1","k_p1c2","k_p1c3"]),
    ("k_p1c5","可能性的大小","probability",["k_p1c3"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学一年级", branch="math", tags=["小学一年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p1_classify", estimated_minutes=60))

# 二年级上：乘法
P2M_PRS = {
    "k_p2m1":[], "k_p2m2":["k_p2m1"], "k_p2m3":["k_p2m2"],
    "k_p2m4":["k_p2m3"], "k_p2m5":["k_p2m4"], "k_p2m6":["k_p2m5"],
    "k_p2m7":["k_p2m6"], "k_p2m8":["k_p2m7"], "k_p2m9":["k_p2m7","k_p2m8"],
    "k_p2m10":["k_p2m9"], "k_p2m11":["k_p2m10"],
    "k_p2m12":["k_p2m11"], "k_p2m13":["k_p2m7"]
}
P2M = {
    "k_p2m1":"乘法的意义", "k_p2m2":"乘号", "k_p2m3":"1的乘法口诀",
    "k_p2m4":"2的乘法口诀", "k_p2m5":"3的乘法口诀",
    "k_p2m6":"4的乘法口诀", "k_p2m7":"5的乘法口诀",
    "k_p2m8":"乘加乘减", "k_p2m9":"6的乘法口诀",
    "k_p2m10":"7的乘法口诀", "k_p2m11":"8的乘法口诀",
    "k_p2m12":"9的乘法口诀", "k_p2m13":"用乘法解决问题",
}
for kid,zh,prereqs in [
    ("k_p2m1","乘法的意义","meaning of multiplication",P2M_PRS["k_p2m1"]),
    ("k_p2m2","乘号","multiplication sign",P2M_PRS["k_p2m2"]),
    ("k_p2m3","1的乘法口诀","1 times table",P2M_PRS["k_p2m3"]),
    ("k_p2m4","2的乘法口诀","2 times table",P2M_PRS["k_p2m4"]),
    ("k_p2m5","3的乘法口诀","3 times table",P2M_PRS["k_p2m5"]),
    ("k_p2m6","4的乘法口诀","4 times table",P2M_PRS["k_p2m6"]),
    ("k_p2m7","5的乘法口诀","5 times table",P2M_PRS["k_p2m7"]),
    ("k_p2m8","乘加乘减","multiply then add subtract",P2M_PRS["k_p2m8"]),
    ("k_p2m9","6的乘法口诀","6 times table",P2M_PRS["k_p2m9"]),
    ("k_p2m10","7的乘法口诀","7 times table",P2M_PRS["k_p2m10"]),
    ("k_p2m11","8的乘法口诀","8 times table",P2M_PRS["k_p2m11"]),
    ("k_p2m12","9的乘法口诀","9 times table",P2M_PRS["k_p2m12"]),
    ("k_p2m13","用乘法解决问题","word problems multiplication",P2M_PRS["k_p2m13"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2_mul", estimated_minutes=60))

# 角
P2A_PRS = {"k_p2a1":[], "k_p2a2":["k_p2a1"], "k_p2a3":["k_p2a1"],
             "k_p2a4":["k_p2a3"], "k_p2a5":["k_p2a4"], "k_p2a6":["k_p2a3","k_p2a4","k_p2a5"]}
for kid,zh,en,prereqs in [
    ("k_p2a1","角的认识","understanding angle",P2A_PRS["k_p2a1"]),
    ("k_p2a2","画角","draw angle",P2A_PRS["k_p2a2"]),
    ("k_p2a3","认识直角","recognize right angle",P2A_PRS["k_p2a3"]),
    ("k_p2a4","认识锐角和钝角","acute obtuse angles",P2A_PRS["k_p2a4"]),
    ("k_p2a5","比角的大小","compare angles",P2A_PRS["k_p2a5"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2_angle", estimated_minutes=60))

# 时间
for kid,zh,en,prereqs in [
    ("k_p2t1","认识整时","recognize o clock",[]),
    ("k_p2t2","认识半时","recognize half hour",["k_p2t1"]),
    ("k_p2t3","认识几时几分","recognize time",["k_p2t2"]),
    ("k_p2t4","24时计时法","24 hour clock",["k_p2t1"]),
    ("k_p2t5","计算经过时间","elapsed time",["k_p2t3","k_p2t4"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2_time", estimated_minutes=60))

# 除法
P2D_PRS = {
    "k_p2d1":["k_p2m1"],"k_p2d2":["k_p2d1"],"k_p2d3":["k_p2d1"],
    "k_p2d4":["k_p2d3"],"k_p2d5":["k_p2d4","k_p2m1"],
    "k_p2d6":["k_p2d5"],"k_p2d7":["k_p2d6","k_p2m9"],
    "k_p2d8":["k_p2d7"],"k_p2d9":["k_p2d8"],
    "k_p2d10":["k_p2d9"],"k_p2d11":["k_p2d10"],
    "k_p2d12":["k_p2d11"],"k_p2d13":["k_p2d12"],
    "k_p2d14":["k_p2d13"]
}
for kid,zh,en,prereqs in [
    ("k_p2d1","除法的意义","meaning of division",P2D_PRS["k_p2d1"]),
    ("k_p2d2","除号","division sign",P2D_PRS["k_p2d2"]),
    ("k_p2d3","平均分","divide equally",P2D_PRS["k_p2d3"]),
    ("k_p2d4","除法看图列式","division from pictures",P2D_PRS["k_p2d4"]),
    ("k_p2d5","用乘法想除法","use multiplication for division",P2D_PRS["k_p2d5"]),
    ("k_p2d6","2-5的除法","division by 2-5",P2D_PRS["k_p2d6"]),
    ("k_p2d7","6的除法","division by 6",P2D_PRS["k_p2d7"]),
    ("k_p2d8","7的除法","division by 7",P2D_PRS["k_p2d8"]),
    ("k_p2d9","8的除法","division by 8",P2D_PRS["k_p2d9"]),
    ("k_p2d10","9的除法","division by 9",P2D_PRS["k_p2d10"]),
    ("k_p2d11","用除法解决问题","word problems division",P2D_PRS["k_p2d11"]),
    ("k_p2d12","有余数的除法","division with remainder",P2D_PRS["k_p2d12"]),
    ("k_p2d13","余数比除数小","remainder less than divisor",P2D_PRS["k_p2d13"]),
    ("k_p2d14","用有余数除法解决问题","solve remainder problems",P2D_PRS["k_p2d14"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2b_div", estimated_minutes=60))

# 人民币
for kid,zh,en,prereqs in [
    ("k_p2rm1","认识人民币","recognize RMB",[]),
    ("k_p2rm2","人民币换算","RMB exchange",["k_p2rm1"]),
    ("k_p2rm3","元角分的计算","yuan jiao fen calculation",["k_p2rm2"]),
    ("k_p2rm4","简单的计算","simple calculation",["k_p2rm3"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2b_money", estimated_minutes=60))

# 测量
for kid,zh,en,prereqs in [
    ("k_p2me1","认识分米和毫米","decimeter and millimeter",["k_p2a1"]),
    ("k_p2me2","长度单位换算","length unit conversion",["k_p2me1"]),
    ("k_p2me3","千米","kilometer",["k_p2me2"]),
    ("k_p2me4","认识吨","ton",["k_p2me1"]),
    ("k_p2me5","解决问题","solve measurement problems",["k_p2me2","k_p2me4"]),
]:
    add(node(id=kid, type="concept", name={"zh":zh,"en":en}, description={"zh":zh,"en":en}, level="小学二年级", branch="math", tags=["小学二年级","数学"], prerequisites=prereqs, difficulty=3, importance=8, chapter="ch_p2b_measure", estimated_minutes=60))

print(f"添加: {len(nodes)} 节点")
with open(FP,"w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
print("已保存")

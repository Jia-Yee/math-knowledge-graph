#!/usr/bin/env python3
"""重建正确的知识图谱数据 - 修正年级分配"""
import json
from pathlib import Path

DATA_FILE = Path("/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json")

# 正确的年级分配
GRADE_DISTRIBUTION = {
    # ===== 小学一年级 =====
    "小学一年级": {
        "arithmetic": [
            ("number_1_to_5", "1-5的认识", "Numbers 1 to 5", 1),
            ("number_6_to_10", "6-10的认识", "Numbers 6 to 10", 1),
            ("number_11_to_20", "11-20的认识", "Numbers 11 to 20", 1),
            ("number_composition", "数的组成", "Composition of Numbers", 1),
            ("counting_by_group", "数数", "Counting by Grouping", 1),
            ("compare_within_20", "20以内数的大小比较", "Comparing Numbers Within 20", 1),
            ("addition_within_10", "10以内加减法", "Addition and Subtraction Within 10", 2),
            ("addition_within_20", "20以内进位加法", "Carry Addition Within 20", 2),
            ("subtraction_within_20", "20以内退位减法", "Borrow Subtraction Within 20", 2),
            ("number_order_position", "数的顺序和大小", "Number Order and Magnitude", 1),
            ("cardinal_number", "基数", "Cardinal Number", 1),
            ("ordinal_number", "序数", "Ordinal Number", 1),
        ],
        "geometry": [
            ("recognize_square", "认识正方形", "Recognizing Squares", 1),
            ("recognize_rectangle", "认识长方形", "Recognizing Rectangles", 1),
            ("recognize_triangle_p1", "认识三角形", "Recognizing Triangles", 1),
            ("recognize_circle", "认识圆形", "Recognizing Circles", 1),
            ("distinguish_2d_3d", "立体图形和平面图形", "2D and 3D Shapes", 2),
            ("position_left_right", "认识左右", "Left and Right", 1),
            ("position_up_down", "认识上下", "Up and Down", 1),
            ("position_front_back", "认识前后", "Front and Back", 1),
            ("row_column_position", "行与列", "Rows and Columns", 2),
            ("relative_position", "相对位置", "Relative Position", 2),
        ],
        "statistics": [
            ("classify_objects", "分类", "Classification", 1),
            ("sort_and_count", "整理数据", "Sorting and Counting", 1),
            ("tally_mark", "象形统计图", "Pictograph", 1),
        ],
    },
    
    # ===== 小学二年级 =====
    "小学二年级": {
        "arithmetic": [
            ("number_100", "100以内数的认识", "Numbers Within 100", 2),
            ("hundreds_place", "百位", "Hundreds Place", 2),
            ("compare_100", "100以内数的大小比较", "Comparing Numbers Within 100", 2),
            ("estimate_count", "估计数量", "Estimation", 2),
            ("multiplication_meaning_p2", "乘法的意义", "Meaning of Multiplication", 2),
            ("multiplication_table_2_5", "2-5的乘法口诀", "Multiplication Tables 2-5", 2),
            ("multiplication_table_6_9", "6-9的乘法口诀", "Multiplication Tables 6-9", 3),
            ("division_meaning_p2", "除法的意义", "Meaning of Division", 3),
            ("division_table", "用乘法口诀求商", "Division Using Multiplication Tables", 3),
            ("division_remainder", "有余数的除法", "Division with Remainder", 3),
            ("even_number", "偶数", "Even Numbers", 2),
            ("odd_number", "奇数", "Odd Numbers", 2),
            ("recognize_rmb_1", "认识人民币", "Recognizing RMB", 2),
            ("rmb_exchange", "人民币换算", "RMB Exchange", 2),
            ("rmb_add_sub", "人民币的加减计算", "RMB Addition and Subtraction", 2),
        ],
        "geometry": [
            ("angle_p", "角的认识", "Understanding Angle", 2),
            ("angle_right_p", "直角", "Right Angle", 2),
            ("angle_acute_p", "锐角", "Acute Angle", 2),
            ("angle_obtuse_p", "钝角", "Obtuse Angle", 2),
            ("observe_from_front", "从不同方向观察物体", "Observing Objects from Different Views", 2),
            ("cube_faces", "正方体的展开图", "Cube Nets", 3),
            ("cube", "正方体", "Cube", 2),
            ("length_unit_m", "米", "Meter", 2),
            ("length_unit_cm", "厘米", "Centimeter", 2),
            ("measure_length", "测量长度", "Measuring Length", 2),
            ("line_segment_measure", "线段的测量", "Measuring Line Segments", 2),
        ],
        "time": [
            ("read_clock_face", "认识整时和半时", "Reading Clock: O'clock and Half Past", 2),
            ("read_exact_time", "认识几时几分", "Reading Exact Time", 3),
            ("time_sequence", "时间的先后顺序", "Sequence of Time", 2),
        ],
    },
    
    # ===== 小学三年级 =====
    "小学三年级": {
        "arithmetic": [
            ("number_1000", "千以内数的认识", "Numbers Within 1000", 2),
            ("thousands_place", "千位", "Thousands Place", 2),
            ("number_10000", "万以内数的认识", "Numbers Within 10000", 2),
            ("ten_thousand_place", "万位", "Ten-Thousands Place", 2),
            ("round_number", "四舍五入", "Rounding Numbers", 3),
            ("approx_estimate", "近似数", "Approximation", 3),
            ("two_digit_times_one", "两位数乘一位数", "Two-digit Times One-digit", 3),
            ("three_digit_times_one", "三位数乘一位数", "Three-digit Times One-digit", 3),
            ("division_one_digit", "一位数除两三位数", "One-digit Division", 3),
            ("natural_numbers", "自然数", "Natural Numbers", 2),
            ("zero", "零", "Zero", 1),
            ("whole_numbers", "整数", "Whole Numbers", 2),
            ("counting_unit", "计数单位", "Counting Unit", 2),
            ("decimal_system", "十进制", "Decimal System", 2),
            ("digit_place", "数位", "Digit Place", 2),
            ("addition", "加法", "Addition", 2),
            ("addition_meaning", "加法意义", "Meaning of Addition", 2),
            ("addition_commutative", "加法交换律", "Addition Commutative Law", 2),
            ("addition_associative", "加法结合律", "Addition Associative Law", 3),
            ("subtraction", "减法", "Subtraction", 2),
            ("subtraction_meaning", "减法意义", "Meaning of Subtraction", 2),
            ("subtraction_borrow", "退位减法", "Borrow Subtraction", 3),
        ],
        "fractions": [
            ("fractions", "分数", "Fractions", 2),
            ("fraction_concept", "分数的概念", "Concept of Fraction", 2),
            ("fraction_unit", "分数单位", "Fraction Unit", 2),
            ("fraction_half_quarter", "认识一半和四分之一", "Half and Quarter", 2),
            ("proper_fraction", "真分数", "Proper Fraction", 2),
            ("improper_fraction", "假分数", "Improper Fraction", 3),
            ("mixed_number", "带分数", "Mixed Number", 3),
            ("fraction_compare", "分数比较", "Comparing Fractions", 2),
            ("compare_simple_fraction", "简单分数比较", "Comparing Simple Fractions", 2),
            ("add_sub_simple_fraction", "同分母分数加减", "Same Denominator Fraction Add/Sub", 3),
            ("fraction_basic_property", "分数基本性质", "Basic Property of Fractions", 3),
        ],
        "geometry": [
            ("triangle", "三角形", "Triangle", 2),
            ("triangle_classify", "三角形的分类", "Classification of Triangles", 2),
            ("triangle_angle_sum", "三角形内角和", "Triangle Angle Sum", 3),
            ("triangle_p", "三角形认识", "Understanding Triangle", 2),
            ("triangle_by_angle_p", "按角分类", "Classification by Angle", 2),
            ("triangle_by_side_p", "按边分类", "Classification by Side", 2),
            ("triangle_stability", "三角形的稳定性", "Stability of Triangle", 2),
            ("quadrilateral", "四边形", "Quadrilateral", 2),
            ("rectangle", "长方形", "Rectangle", 2),
            ("square", "正方形", "Square", 2),
            ("parallelogram", "平行四边形", "Parallelogram", 3),
            ("trapezoid", "梯形", "Trapezoid", 3),
            ("area", "面积", "Area", 3),
            ("area_rectangle", "长方形面积", "Area of Rectangle", 3),
            ("area_square", "正方形面积", "Area of Square", 3),
            ("area_triangle", "三角形面积", "Area of Triangle", 3),
            ("perimeter", "周长", "Perimeter", 2),
            ("area_concept", "面积的意义", "Concept of Area", 3),
            ("area_unit", "面积单位", "Area Units", 3),
        ],
        "measurement": [
            ("length_unit_mm", "毫米", "Millimeter", 2),
            ("length_unit_km", "千米", "Kilometer", 3),
            ("mass_unit_t", "吨", "Ton", 3),
            ("time_unit_year_month", "年月日", "Year Month Day", 3),
            ("time_unit_hour_minute", "24时计时法", "24-Hour Clock", 3),
            ("year_p", "年", "Year", 2),
            ("month_p", "月", "Month", 2),
            ("day_p", "日", "Day", 2),
            ("hour_p", "时", "Hour", 2),
            ("minute_p", "分", "Minute", 2),
            ("second_p", "秒", "Second", 2),
            ("meter_p", "米", "Meter", 2),
            ("centimeter", "厘米", "Centimeter", 2),
            ("millimeter", "毫米", "Millimeter", 2),
            ("kilometer", "千米", "Kilometer", 3),
            ("kilogram_p", "千克", "Kilogram", 2),
            ("gram_p", "克", "Gram", 2),
            ("eight_directions", "八个方向", "Eight Directions", 3),
            ("describe_direction_distance", "描述路线图", "Describing Routes", 3),
        ],
    },
    
    # ===== 小学四年级 =====
    "小学四年级": {
        "arithmetic": [
            ("number_100_million", "亿以内数的认识", "Numbers Within 100 Million", 3),
            ("hundred_million_place", "亿位", "Hundred-Million Place", 3),
            ("number_1000_million", "亿以上数的认识", "Numbers Above 100 Million", 3),
            ("counting_nature", "自然数（扩展）", "Natural Numbers (Extended)", 3),
            ("multiplication_distributive", "乘法分配律", "Multiplication Distributive Law", 3),
        ],
        "geometry": [
            ("point_line_plane", "点线面", "Point Line Plane", 2),
            ("line_straight", "直线", "Straight Line", 2),
            ("line_ray", "射线", "Ray", 2),
            ("angle_measure_degree", "角度制", "Degree Measurement", 3),
            ("draw_angle", "画角", "Drawing Angles", 3),
            ("classify_angles", "角的分类", "Classifying Angles", 3),
            ("sum_of_angles_triangle", "三角形内角和", "Triangle Angle Sum", 3),
            ("parallelogram_prop", "平行四边形的特征", "Properties of Parallelogram", 3),
            ("trapezoid_prop", "梯形的特征", "Properties of Trapezoid", 3),
            ("quadrilateral_classify", "四边形的分类", "Classification of Quadrilaterals", 4),
            ("angle", "角", "Angle", 2),
            ("acute_angle", "锐角", "Acute Angle", 2),
            ("right_angle", "直角", "Right Angle", 2),
            ("obtuse_angle", "钝角", "Obtuse Angle", 2),
            ("straight_angle", "平角", "Straight Angle", 3),
            ("full_angle", "周角", "Full Angle", 3),
            ("angle_measure", "角的度量", "Measuring Angles", 3),
            ("parallel", "平行", "Parallel", 2),
            ("perpendicular", "垂直", "Perpendicular", 2),
            ("parallel_line_p", "平行线", "Parallel Lines", 3),
            ("perpendicular_line_p", "垂线", "Perpendicular Lines", 3),
            ("translation", "平移", "Translation", 2),
            ("rotation", "旋转", "Rotation", 2),
            ("cuboid", "长方体", "Cuboid", 2),
            ("area_unit_hectare", "公顷", "Hectare", 3),
            ("area_unit_km2", "平方千米", "Square Kilometer", 3),
        ],
        "statistics": [
            ("bar_chart_p4", "纵向条形统计图", "Vertical Bar Chart", 3),
            ("bar_chart_horizontal", "横向条形统计图", "Horizontal Bar Chart", 3),
            ("data_analysis_average", "数据分析（平均数应用）", "Data Analysis with Average", 3),
            ("compound_bar_chart", "复式条形统计图", "Double Bar Chart", 4),
            ("average", "平均数", "Average", 2),
            ("line_chart", "折线统计图", "Line Chart", 3),
            ("pie_chart", "扇形统计图", "Pie Chart", 4),
        ],
    },
    
    # ===== 小学五年级 =====
    "小学五年级": {
        "arithmetic": [
            ("decimals", "小数", "Decimals", 3),
            ("decimal_number", "小数", "Decimal Number", 3),
            ("decimal_integer_part", "小数整数部分", "Decimal Integer Part", 3),
            ("decimal_fractional_part", "小数小数部分", "Decimal Fractional Part", 3),
            ("decimal_basic_property", "小数的基本性质", "Basic Property of Decimals", 3),
            ("decimal_precision", "小数的性质", "Decimal Properties", 3),
            ("decimal_move_point", "小数点移动规律", "Decimal Point Movement", 3),
            ("decimal_rounding", "小数近似数", "Rounding Decimals", 3),
            ("decimal_add_sub", "小数加减", "Decimal Addition and Subtraction", 3),
            ("decimal_add_sub_p5", "小数加减（进阶）", "Decimal Add/Sub Advanced", 3),
            ("decimal_multiply", "小数乘法", "Decimal Multiplication", 4),
            ("decimal_divide", "小数除法", "Decimal Division", 4),
            ("multiple", "倍数", "Multiple", 3),
            ("factor_divisor", "因数", "Factor/Divisor", 3),
            ("divisible_by_2", "2的倍数特征", "Divisibility by 2", 3),
            ("divisible_by_5", "5的倍数特征", "Divisibility by 5", 3),
            ("divisible_by_3", "3的倍数特征", "Divisibility by 3", 3),
            ("prime_number", "质数", "Prime Number", 3),
            ("composite_number", "合数", "Composite Number", 3),
            ("prime_factorization", "质因数分解", "Prime Factorization", 4),
            ("common_factor", "公因数", "Common Factor", 3),
            ("gcf", "最大公因数", "Greatest Common Factor", 4),
            ("common_multiple", "公倍数", "Common Multiple", 3),
            ("lcm", "最小公倍数", "Least Common Multiple", 4),
            ("coprime", "互质数", "Coprime Numbers", 3),
            ("lcm_gcf_word", "最大公因数和最小公倍数应用", "Applications of GCF and LCM", 4),
            ("fraction_add", "分数加减", "Fraction Addition and Subtraction", 4),
            ("fraction_multiply", "分数乘法", "Fraction Multiplication", 4),
            ("fraction_divide", "分数除法", "Fraction Division", 4),
            ("fraction_add_sub_different_denom", "异分母分数加减", "Unlike Denominator Fraction Add/Sub", 4),
            ("mixed_number_calc", "带分数的计算", "Mixed Number Calculation", 4),
            ("fraction_word_problems", "分数应用题", "Fraction Word Problems", 4),
        ],
        "geometry": [
            ("circle", "圆", "Circle", 3),
            ("radius_diameter", "半径和直径", "Radius and Diameter", 3),
            ("circumference", "圆周长", "Circumference", 4),
            ("circle_area", "圆面积", "Area of Circle", 4),
            ("circle_advance", "圆的周长", "Circumference of Circle", 3),
            ("pi_concept", "圆周率", "Pi", 3),
            ("circumference_formula", "圆的周长公式", "Circumference Formula", 4),
            ("circle_area_derive", "圆的面积", "Area of Circle (Derived)", 4),
            ("circle_p", "圆的认识", "Understanding Circle", 3),
            ("circle_radius_diameter_relation", "半径直径关系", "Radius-Diameter Relation", 3),
            ("cartesian_plane", "认识坐标", "Introduction to Coordinates", 3),
            ("plot_points", "在方格纸上描点", "Plotting Points on Grid", 3),
            ("draw_translation", "图形的平移", "Drawing Translation", 3),
            ("draw_rotation", "图形的旋转", "Drawing Rotation", 3),
            ("draw_symmetry_axis", "作轴对称图形", "Drawing Axis Symmetric Figures", 3),
            ("composite_transform", "图形变换综合", "Composite Shape Transformations", 4),
            ("coordinate_pair", "数对", "Coordinate Pair", 3),
            ("cube_geo_p", "正方体", "Cube (Geometry)", 3),
            ("cylinder_p", "圆柱", "Cylinder", 4),
        ],
        "statistics": [
            ("median_mode_p5", "中位数和众数", "Median and Mode", 3),
            ("compound_table", "复式统计表", "Compound Statistical Table", 3),
            ("compound_bar_chart_p5", "复式条形统计图", "Double Bar Chart", 3),
            ("compound_line_chart", "复式折线统计图", "Double Line Chart", 4),
            ("analyze_statistical_data", "统计数据的分析与应用", "Statistical Data Analysis", 4),
        ],
    },
    
    # ===== 小学六年级 =====
    "小学六年级": {
        "arithmetic": [
            ("fraction_multiplication_p6", "分数乘整数", "Multiply Fraction by Integer", 3),
            ("fraction_times_fraction", "分数乘分数", "Fraction Times Fraction", 4),
            ("reciprocal", "倒数", "Reciprocal Numbers", 3),
            ("fraction_division_p6", "分数除法", "Fraction Division", 4),
            ("fraction_word_p6", "分数四则混合运算", "Fraction Mixed Operations", 5),
            ("percentage", "百分数", "Percentage", 3),
            ("percent_convert", "百分数与分数小数的互化", "Conversions Among Percent/Fraction/Decimal", 4),
            ("percent_word_problems", "百分数应用题", "Percent Word Problems", 4),
            ("increase_decrease_percent", "增加和减少百分之几", "Increase and Decrease by Percent", 5),
            ("tax_interest", "纳税与利息", "Tax and Interest", 4),
            ("ratio", "比", "Ratio", 3),
            ("ratio_simplify", "比的化简", "Simplifying Ratios", 3),
            ("proportion", "比例", "Proportion", 4),
            ("ratio_concept", "比的概念", "Concept of Ratio", 3),
            ("ratio_value", "比值", "Ratio Value", 3),
            ("ratio_basic_property", "比的基本性质", "Basic Property of Ratio", 3),
            ("proportion_basic_property", "比例的基本性质", "Basic Property of Proportion", 4),
            ("ratio_extend", "比的性质", "Ratio Properties", 4),
            ("ratio_word_problems", "按比分配问题", "Ratio Distribution Problems", 4),
            ("direct_proportion", "正比例", "Direct Proportion", 4),
            ("inverse_proportion", "反比例", "Inverse Proportion", 4),
            ("proportionality", "正比例与反比例的意义", "Direct and Inverse Proportionality", 5),
            ("solve_proportion", "用比例解决问题", "Solving Problems with Proportion", 5),
            ("scale_drawing", "比例尺", "Scale Drawing", 4),
            ("negative_number_p6", "负数的认识", "Introduction to Negative Numbers", 2),
            ("number_line_negative", "数轴上的负数", "Negative Numbers on Number Line", 3),
            ("compare_negative", "正负数的大小比较", "Comparing Positive and Negative Numbers", 3),
            ("opposite_number_p6", "相反数", "Opposite Numbers", 3),
            ("absolute_value_p6", "绝对值", "Absolute Value", 3),
            ("add_negative_numbers", "有理数加法", "Addition of Rational Numbers", 4),
            ("rational_number_p6", "有理数", "Rational Numbers", 4),
        ],
        "geometry": [
            ("sector", "扇形的认识", "Sector", 3),
            ("sector_area", "扇形面积", "Area of Sector", 5),
            ("cylinder_components", "圆柱的构成", "Parts of Cylinder", 3),
            ("cylinder_surface_area", "圆柱的表面积", "Surface Area of Cylinder", 5),
            ("cylinder_volume_p6", "圆柱的体积", "Volume of Cylinder", 5),
            ("cone_components", "圆锥的构成", "Parts of Cone", 3),
            ("cone_volume", "圆锥的体积", "Volume of Cone", 5),
        ],
        "statistics": [
            ("pie_chart_p6", "扇形统计图", "Pie Chart", 4),
            ("choices_combinations", "搭配问题", "Combination Problems", 3),
            ("probability_experiment", "简单概率实验", "Simple Probability Experiments", 3),
            ("theoretical_probability", "用分数表示可能性大小", "Theoretical Probability", 4),
            ("possibility", "可能性", "Possibility", 2),
        ],
    },
}

def build_nodes():
    """构建节点列表"""
    nodes = []
    node_ids = set()
    
    for grade, branches in GRADE_DISTRIBUTION.items():
        for branch, concepts in branches.items():
            for concept in concepts:
                node_id, zh_name, en_name, difficulty = concept
                if node_id in node_ids:
                    continue
                node_ids.add(node_id)
                
                node = {
                    "id": node_id,
                    "type": "concept",
                    "name": {"zh": zh_name, "en": en_name},
                    "description": {"zh": zh_name, "en": en_name},
                    "level": grade,
                    "branch": branch,
                    "tags": [grade, "数学"],
                    "prerequisites": [],
                    "difficulty": difficulty,
                    "importance": 8,
                    "estimated_minutes": 60
                }
                nodes.append(node)
    
    return {"nodes": nodes}

def main():
    data = build_nodes()
    
    # 备份原文件
    if DATA_FILE.exists():
        import shutil
        backup_file = DATA_FILE.with_suffix(".json.bak")
        shutil.copy(DATA_FILE, backup_file)
        print(f"备份原文件到 {backup_file}")
    
    # 写入新数据
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"写入 {len(data['nodes'])} 个节点到 {DATA_FILE}")
    
    # 统计各年级节点数
    from collections import Counter
    grade_counts = Counter(n["level"] for n in data["nodes"])
    for grade, count in sorted(grade_counts.items()):
        print(f"  {grade}: {count} 个节点")

if __name__ == "__main__":
    main()

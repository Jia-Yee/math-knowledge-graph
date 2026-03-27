#!/usr/bin/env python3
"""
小学数学知识点批量补充脚本
依据：人教版《义务教育数学课程标准》
"""

import json
import re

DATA_FILE = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"

# ----------------------------------------------------------
# 新增节点定义
# 格式：(id, 名称_zh, 名称_en, 类型, 分支, tags, 先修ID列表, 难度, 重要度, 预估分钟)
# ----------------------------------------------------------

NEW_PRIMARY_NODES = [
    # ========== 小学一年级 ==========

    # 一年级 - 数与运算
    ("number_1_to_5", "1-5的认识", "Numbers 1 to 5", "concept", "arithmetic",
     ["小学一年级"], [], 1, 10, 45),
    ("number_6_to_10", "6-10的认识", "Numbers 6 to 10", "concept", "arithmetic",
     ["小学一年级"], ["number_1_to_5"], 1, 10, 45),
    ("number_11_to_20", "11-20的认识", "Numbers 11 to 20", "concept", "arithmetic",
     ["小学一年级"], ["number_6_to_10"], 2, 10, 60),
    ("counting_by_group", "数数", "Counting by Grouping", "concept", "arithmetic",
     ["小学一年级"], ["number_11_to_20"], 2, 10, 30),
    ("compare_within_20", "20以内数的大小比较", "Comparing Numbers Within 20", "concept", "arithmetic",
     ["小学一年级"], ["number_11_to_20"], 1, 10, 30),
    ("addition_within_10", "10以内加减法", "Addition and Subtraction Within 10", "concept", "arithmetic",
     ["小学一年级"], ["number_1_to_5", "number_6_to_10"], 2, 10, 90),
    ("addition_within_20", "20以内进位加法", "Carry Addition Within 20", "concept", "arithmetic",
     ["小学一年级"], ["addition_within_10", "number_11_to_20"], 3, 10, 90),
    ("subtraction_within_20", "20以内退位减法", "Borrow Subtraction Within 20", "concept", "arithmetic",
     ["小学一年级"], ["addition_within_20"], 3, 10, 90),
    ("number_composition", "数的组成", "Composition of Numbers", "concept", "arithmetic",
     ["小学一年级"], ["number_1_to_5"], 1, 10, 30),
    ("number_order_position", "数的顺序和大小", "Number Order and Magnitude", "concept", "arithmetic",
     ["小学一年级"], ["number_11_to_20"], 2, 10, 45),

    # 一年级 - 分类与整理
    ("classify_objects", "分类", "Classification", "concept", "statistics",
     ["小学一年级"], [], 1, 9, 45),
    ("sort_and_count", "整理数据", "Sorting and Counting", "concept", "statistics",
     ["小学一年级"], ["classify_objects"], 1, 9, 45),
    ("tally_mark", "象形统计图", "Pictograph", "concept", "statistics",
     ["小学一年级"], ["sort_and_count"], 1, 9, 45),

    # 一年级 - 位置与顺序
    ("position_left_right", "认识左右", "Left and Right", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("position_up_down", "认识上下", "Up and Down", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("position_front_back", "认识前后", "Front and Back", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("row_column_position", "行与列", "Rows and Columns", "concept", "geometry",
     ["小学一年级"], ["position_left_right"], 2, 10, 45),
    ("relative_position", "相对位置", "Relative Position", "concept", "geometry",
     ["小学一年级"], ["row_column_position"], 2, 9, 45),

    # 一年级 - 认识图形
    ("recognize_square", "认识正方形", "Recognizing Squares", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("recognize_rectangle", "认识长方形", "Recognizing Rectangles", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("recognize_triangle_p1", "认识三角形", "Recognizing Triangles", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("recognize_circle", "认识圆形", "Recognizing Circles", "concept", "geometry",
     ["小学一年级"], [], 1, 10, 30),
    ("distinguish_2d_3d", "立体图形和平面图形", "2D and 3D Shapes", "concept", "geometry",
     ["小学一年级"], ["recognize_square", "recognize_circle"], 2, 10, 45),

    # ========== 小学二年级 ==========

    # 二年级 - 100以内数
    ("number_100", "100以内数的认识", "Numbers Within 100", "concept", "arithmetic",
     ["小学二年级"], ["number_11_to_20"], 2, 10, 60),
    ("hundreds_place", "百位", "Hundreds Place", "concept", "arithmetic",
     ["小学二年级"], ["number_100"], 2, 10, 30),
    ("compare_100", "100以内数的大小比较", "Comparing Numbers Within 100", "concept", "arithmetic",
     ["小学二年级"], ["number_100"], 2, 10, 45),
    ("estimate_count", "估计数量", "Estimation", "concept", "arithmetic",
     ["小学二年级"], ["number_100"], 2, 9, 45),

    # 二年级 - 表内乘法
    ("multiplication_meaning_p2", "乘法的意义", "Meaning of Multiplication", "concept", "arithmetic",
     ["小学二年级"], ["addition_within_20"], 2, 10, 60),
    ("multiplication_table_2_5", "2-5的乘法口诀", "Multiplication Tables 2-5", "concept", "arithmetic",
     ["小学二年级"], ["multiplication_meaning_p2"], 2, 10, 90),
    ("multiplication_table_6_9", "6-9的乘法口诀", "Multiplication Tables 6-9", "concept", "arithmetic",
     ["小学二年级"], ["multiplication_table_2_5"], 3, 10, 120),
    ("division_meaning_p2", "除法的意义", "Meaning of Division", "concept", "arithmetic",
     ["小学二年级"], ["multiplication_table_2_5"], 3, 10, 60),
    ("division_table", "用乘法口诀求商", "Division Using Multiplication Tables", "concept", "arithmetic",
     ["小学二年级"], ["division_meaning_p2", "multiplication_table_2_5"], 3, 10, 90),

    # 二年级 - 观察物体
    ("observe_from_front", "从不同方向观察物体", "Observing Objects from Different Views", "concept", "geometry",
     ["小学二年级"], ["distinguish_2d_3d"], 2, 10, 45),
    ("cube_faces", "正方体的展开图", "Cube Nets", "concept", "geometry",
     ["小学二年级"], ["observe_from_front"], 3, 10, 60),

    # 二年级 - 认识时间
    ("read_clock_face", "认识整时和半时", "Reading Clock: O'clock and Half Past", "concept", "arithmetic",
     ["小学二年级"], [], 2, 10, 45),
    ("read_exact_time", "认识几时几分", "Reading Exact Time", "concept", "arithmetic",
     ["小学二年级"], ["read_clock_face"], 3, 10, 60),
    ("time_sequence", "时间的先后顺序", "Sequence of Time", "concept", "arithmetic",
     ["小学二年级"], ["read_exact_time"], 2, 9, 30),

    # 二年级 - 长度单位
    ("length_unit_m", "米", "Meter", "concept", "arithmetic",
     ["小学二年级"], [], 2, 10, 30),
    ("length_unit_cm", "厘米", "Centimeter", "concept", "arithmetic",
     ["小学二年级"], [], 2, 10, 30),
    ("measure_length", "测量长度", "Measuring Length", "concept", "arithmetic",
     ["小学二年级"], ["length_unit_m", "length_unit_cm"], 2, 10, 60),
    ("line_segment_measure", "线段的测量", "Measuring Line Segments", "concept", "geometry",
     ["小学二年级"], ["measure_length"], 2, 10, 45),

    # 二年级 - 统计
    ("collect_data_p2", "收集数据", "Data Collection", "concept", "statistics",
     ["小学二年级"], ["sort_and_count"], 2, 10, 45),
    ("survey_method", "调查方法", "Survey Methods", "concept", "statistics",
     ["小学二年级"], ["collect_data_p2"], 2, 9, 45),
    ("simple_picture_graph", "简单统计图", "Simple Statistical Charts", "concept", "statistics",
     ["小学二年级"], ["survey_method"], 2, 10, 60),

    # ========== 小学三年级 ==========

    # 三年级 - 万以内数
    ("number_1000", "千以内数的认识", "Numbers Within 1000", "concept", "arithmetic",
     ["小学三年级"], ["number_100"], 2, 10, 60),
    ("thousands_place", "千位", "Thousands Place", "concept", "arithmetic",
     ["小学三年级"], ["number_1000"], 2, 10, 30),
    ("number_10000", "万以内数的认识", "Numbers Within 10000", "concept", "arithmetic",
     ["小学三年级"], ["thousands_place"], 2, 10, 60),
    ("ten_thousand_place", "万位", "Ten-Thousands Place", "concept", "arithmetic",
     ["小学三年级"], ["number_10000"], 2, 10, 30),
    ("round_number", "四舍五入", "Rounding Numbers", "concept", "arithmetic",
     ["小学三年级"], ["number_10000"], 3, 10, 60),
    ("approx_estimate", "近似数", "Approximation", "concept", "arithmetic",
     ["小学三年级"], ["round_number"], 3, 10, 45),

    # 三年级 - 两位数乘一位数
    ("two_digit_times_one", "两位数乘一位数", "Two-digit Times One-digit", "concept", "arithmetic",
     ["小学三年级"], ["multiplication_table_6_9"], 3, 10, 60),
    ("three_digit_times_one", "三位数乘一位数", "Three-digit Times One-digit", "concept", "arithmetic",
     ["小学三年级"], ["two_digit_times_one"], 3, 10, 60),
    ("division_one_digit", "一位数除两三位数", "One-digit Division", "concept", "arithmetic",
     ["小学三年级"], ["division_table", "number_1000"], 3, 10, 90),

    # 三年级 - 测量
    ("length_unit_mm", "毫米", "Millimeter", "concept", "arithmetic",
     ["小学三年级"], ["length_unit_cm"], 2, 10, 30),
    ("length_unit_km", "千米", "Kilometer", "concept", "arithmetic",
     ["小学三年级"], ["length_unit_mm", "meter_p"], 3, 10, 45),
    ("mass_unit_t", "吨", "Ton", "concept", "arithmetic",
     ["小学三年级"], ["kilogram_p"], 3, 10, 45),
    ("time_unit_year_month", "年月日", "Year Month Day", "concept", "arithmetic",
     ["小学三年级"], [], 3, 10, 60),
    ("time_unit_hour_minute", "24时计时法", "24-Hour Clock", "concept", "arithmetic",
     ["小学三年级"], ["read_exact_time"], 3, 10, 60),

    # 三年级 - 分数初步
    ("fraction_half_quarter", "认识一半和四分之一", "Half and Quarter", "concept", "arithmetic",
     ["小学三年级"], ["fractions"], 2, 10, 45),
    ("compare_simple_fraction", "简单分数比较", "Comparing Simple Fractions", "concept", "arithmetic",
     ["小学三年级"], ["fraction_half_quarter"], 3, 10, 45),
    ("add_sub_simple_fraction", "同分母分数加减", "Same Denominator Fraction Add/Sub", "concept", "arithmetic",
     ["小学三年级"], ["compare_simple_fraction"], 3, 10, 60),

    # 三年级 - 面积
    ("area_concept", "面积的意义", "Concept of Area", "concept", "geometry",
     ["小学三年级"], [], 3, 10, 45),
    ("area_unit", "面积单位（平方厘米、平方分米、平方米）", "Area Units", "concept", "geometry",
     ["小学三年级"], ["area_concept"], 3, 10, 60),
    ("area_shadow", "摆方格数面积", "Counting Area by Grid", "concept", "geometry",
     ["小学三年级"], ["area_unit"], 3, 10, 45),
    ("area_formula_direct", "长正方形面积的直接计算", "Direct Area of Rectangle/Square", "concept", "geometry",
     ["小学三年级"], ["area_shadow", "multiplication"], 4, 10, 60),

    # 三年级 - 方向
    ("eight_directions", "八个方向", "Eight Directions", "concept", "geometry",
     ["小学三年级"], [], 3, 10, 60),
    ("describe_direction_distance", "描述路线图", "Describing Routes", "concept", "geometry",
     ["小学三年级"], ["eight_directions"], 3, 10, 60),

    # ========== 小学四年级 ==========

    # 四年级 - 大数的认识
    ("number_100_million", "亿以内数的认识", "Numbers Within 100 Million", "concept", "arithmetic",
     ["小学四年级"], ["number_10000"], 3, 10, 60),
    ("hundred_million_place", "亿位", "Hundred-Million Place", "concept", "arithmetic",
     ["小学四年级"], ["number_100_million"], 3, 10, 30),
    ("number_1000_million", "亿以上数的认识", "Numbers Above 100 Million", "concept", "arithmetic",
     ["小学四年级"], ["number_100_million"], 3, 10, 60),
    ("counting_nature", "自然数", "Natural Numbers (Extended)", "concept", "arithmetic",
     ["小学四年级"], ["number_1000_million"], 3, 10, 45),

    # 四年级 - 面积单位进阶
    ("area_unit_hectare", "公顷", "Hectare", "concept", "geometry",
     ["小学四年级"], ["area_unit"], 3, 10, 45),
    ("area_unit_km2", "平方千米", "Square Kilometer", "concept", "geometry",
     ["小学四年级"], ["area_unit_hectare", "length_unit_km"], 3, 10, 45),
    ("area_formula_unified", "长方形正方形面积公式", "Rectangle and Square Area Formulas", "concept", "geometry",
     ["小学四年级"], ["area_formula_direct"], 3, 10, 45),

    # 四年级 - 角的度量
    ("angle_measure_ degree", "角度制（量角器）", "Degree Measurement", "concept", "geometry",
     ["小学四年级"], ["angle"], 3, 10, 60),
    ("draw_angle", "画角", "Drawing Angles", "concept", "geometry",
     ["小学四年级"], ["angle_measure_ degree"], 3, 10, 45),
    ("classify_angles", "锐角、直角、钝角、平角、周角", "Classifying Angles", "concept", "geometry",
     ["小学四年级"], ["angle_measure_ degree"], 3, 10, 45),
    ("sum_of_angles_triangle", "三角形内角和", "Triangle Angle Sum", "concept", "geometry",
     ["小学四年级"], ["classify_angles", "triangle"], 3, 10, 60),

    # 四年级 - 平行四边形和梯形
    ("parallelogram_prop", "平行四边形的特征", "Properties of Parallelogram", "concept", "geometry",
     ["小学四年级"], ["parallelogram"], 3, 10, 60),
    ("trapezoid_prop", "梯形的特征", "Properties of Trapezoid", "concept", "geometry",
     ["小学四年级"], ["trapezoid"], 3, 10, 45),
    ("quadrilateral_classify", "四边形的分类", "Classification of Quadrilaterals", "concept", "geometry",
     ["小学四年级"], ["parallelogram_prop", "trapezoid_prop"], 4, 10, 60),

    # 四年级 - 条形统计图
    ("bar_chart_p4", "纵向条形统计图", "Vertical Bar Chart", "concept", "statistics",
     ["小学四年级"], ["bar_chart"], 3, 10, 60),
    ("bar_chart_horizontal", "横向条形统计图", "Horizontal Bar Chart", "concept", "statistics",
     ["小学四年级"], ["bar_chart_p4"], 3, 10, 45),
    ("data_analysis_average", "数据分析（平均数应用）", "Data Analysis with Average", "concept", "statistics",
     ["小学四年级"], ["average"], 3, 10, 60),
    ("compound_bar_chart", "复式条形统计图", "Double Bar Chart", "concept", "statistics",
     ["小学四年级"], ["bar_chart_horizontal"], 4, 10, 60),

    # ========== 小学五年级 ==========

    # 五年级 - 小数进阶
    ("decimal_precision", "小数的性质", "Decimal Properties", "concept", "arithmetic",
     ["小学五年级"], ["decimals"], 3, 10, 45),
    ("decimal_move_point", "小数点移动规律", "Decimal Point Movement", "concept", "arithmetic",
     ["小学五年级"], ["decimal_precision"], 3, 10, 60),
    ("decimal_rounding", "小数近似数", "Rounding Decimals", "concept", "arithmetic",
     ["小学五年级"], ["decimal_move_point"], 3, 10, 45),
    ("decimal_add_sub_p5", "小数加减", "Decimal Addition and Subtraction", "concept", "arithmetic",
     ["小学五年级"], ["decimal_add_sub"], 3, 10, 60),

    # 五年级 - 公因数公倍数
    ("prime_factorization", "质因数分解", "Prime Factorization", "concept", "arithmetic",
     ["小学五年级"], ["prime_number", "composite_number"], 4, 10, 60),
    ("lcm_gcf_word", "最大公因数和最小公倍数应用", "Applications of GCF and LCM", "concept", "arithmetic",
     ["小学五年级"], ["gcf", "lcm"], 4, 10, 90),

    # 五年级 - 分数加减法
    ("fraction_add_sub_different_denom", "异分母分数加减", "Unlike Denominator Fraction Add/Sub", "concept", "arithmetic",
     ["小学五年级"], ["fraction_add"], 4, 10, 60),
    ("mixed_number_calc", "带分数的计算", "Mixed Number Calculation", "concept", "arithmetic",
     ["小学五年级"], ["mixed_number", "fraction_add_sub_different_denom"], 4, 10, 60),
    ("fraction_word_problems", "分数应用题", "Fraction Word Problems", "concept", "arithmetic",
     ["小学五年级"], ["fraction_add_sub_different_denom"], 4, 10, 90),

    # 五年级 - 坐标
    ("cartesian_plane", "认识坐标（数对）", "Introduction to Coordinates", "concept", "geometry",
     ["小学五年级"], ["coordinate_pair"], 3, 10, 60),
    ("plot_points", "在方格纸上描点", "Plotting Points on Grid", "concept", "geometry",
     ["小学五年级"], ["cartesian_plane"], 3, 10, 45),
    ("draw_translation", "图形的平移", "Drawing Translation", "concept", "geometry",
     ["小学五年级"], ["plot_points"], 3, 10, 45),
    ("draw_rotation", "图形的旋转", "Drawing Rotation", "concept", "geometry",
     ["小学五年级"], ["draw_translation"], 3, 10, 45),
    ("draw_symmetry_axis", "作轴对称图形", "Drawing Axis Symmetric Figures", "concept", "geometry",
     ["小学五年级"], ["axial_symmetry"], 3, 10, 60),
    ("composite_transform", "图形变换综合", "Composite Shape Transformations", "concept", "geometry",
     ["小学五年级"], ["draw_translation", "draw_rotation", "draw_symmetry_axis"], 4, 10, 60),

    # 五年级 - 统计
    ("median_mode_p5", "中位数和众数", "Median and Mode", "concept", "statistics",
     ["小学五年级"], ["average"], 3, 10, 60),
    ("compound_table", "复式统计表", "Compound Statistical Table", "concept", "statistics",
     ["小学五年级"], ["statistical_table"], 3, 10, 60),
    ("compound_bar_chart_p5", "复式条形统计图", "Double Bar Chart", "concept", "statistics",
     ["小学五年级"], ["compound_bar_chart"], 3, 10, 60),
    ("compound_line_chart", "复式折线统计图", "Double Line Chart", "concept", "statistics",
     ["小学五年级"], ["line_chart"], 4, 10, 60),
    ("analyze_statistical_data", "统计数据的分析与应用", "Statistical Data Analysis", "concept", "statistics",
     ["小学五年级"], ["median_mode_p5", "compound_bar_chart_p5"], 4, 10, 60),

    # ========== 小学六年级 ==========

    # 六年级 - 分数乘除法
    ("fraction_multiplication_p6", "分数乘整数", "Multiply Fraction by Integer", "concept", "arithmetic",
     ["小学六年级"], ["fraction_multiply"], 3, 10, 60),
    ("fraction_times_fraction", "分数乘分数", "Fraction Times Fraction", "concept", "arithmetic",
     ["小学六年级"], ["fraction_multiplication_p6"], 4, 10, 60),
    ("reciprocal", "倒数的认识", "Reciprocal Numbers", "concept", "arithmetic",
     ["小学六年级"], ["fraction_times_fraction"], 3, 10, 45),
    ("fraction_division_p6", "分数除法", "Fraction Division", "concept", "arithmetic",
     ["小学六年级"], ["fraction_times_fraction", "reciprocal"], 4, 10, 90),
    ("fraction_word_p6", "分数四则混合运算", "Fraction Mixed Operations", "concept", "arithmetic",
     ["小学六年级"], ["fraction_division_p6"], 5, 10, 90),

    # 六年级 - 百分数进阶
    ("percent_convert", "百分数与分数小数的互化", "Conversions Among Percent/Fraction/Decimal", "concept", "arithmetic",
     ["小学六年级"], ["percentage", "decimals", "fractions"], 4, 10, 60),
    ("percent_word_problems", "百分数应用题", "Percent Word Problems", "concept", "arithmetic",
     ["小学六年级"], ["percent_convert"], 4, 10, 90),
    ("increase_decrease_percent", "增加和减少百分之几", "Increase and Decrease by Percent", "concept", "arithmetic",
     ["小学六年级"], ["percent_word_problems"], 5, 10, 60),
    ("tax_interest", "纳税与利息", "Tax and Interest", "concept", "arithmetic",
     ["小学六年级"], ["percent_word_problems"], 4, 10, 60),

    # 六年级 - 比和比例
    ("ratio_extend", "比的性质", "Ratio Properties", "concept", "arithmetic",
     ["小学六年级"], ["ratio"], 4, 10, 60),
    ("ratio_word_problems", "按比分配问题", "Ratio Distribution Problems", "concept", "arithmetic",
     ["小学六年级"], ["ratio_extend"], 4, 10, 90),
    ("scale_drawing", "比例尺", "Scale Drawing", "concept", "geometry",
     ["小学六年级"], ["ratio_extend"], 4, 10, 60),
    ("proportionality", "正比例与反比例的意义", "Direct and Inverse Proportionality", "concept", "arithmetic",
     ["小学六年级"], ["direct_proportion", "inverse_proportion"], 5, 10, 90),
    ("solve_proportion", "用比例解决问题", "Solving Problems with Proportion", "concept", "arithmetic",
     ["小学六年级"], ["proportionality"], 5, 10, 90),

    # 六年级 - 圆
    ("circle_advance", "圆的周长", "Circumference of Circle", "concept", "geometry",
     ["小学六年级"], ["circle"], 3, 10, 60),
    ("pi_concept", "圆周率", "Pi", "concept", "geometry",
     ["小学六年级"], ["circle_advance"], 3, 10, 30),
    ("circumference_formula", "圆的周长公式", "Circumference Formula", "formula", "geometry",
     ["小学六年级"], ["circle_advance", "pi_concept"], 4, 10, 45),
    ("circle_area_derive", "圆的面积", "Area of Circle", "concept", "geometry",
     ["小学六年级"], ["circumference_formula"], 4, 10, 90),
    ("annulus_area", "圆环面积", "Area of Annulus", "concept", "geometry",
     ["小学六年级"], ["circle_area_derive"], 5, 10, 60),

    # 六年级 - 扇形
    ("sector", "扇形的认识", "Sector", "concept", "geometry",
     ["小学六年级"], ["circle", "angle"], 3, 10, 45),
    ("sector_area", "扇形面积", "Area of Sector", "concept", "geometry",
     ["小学六年级"], ["sector", "circle_area_derive"], 5, 10, 60),

    # 六年级 - 圆柱与圆锥
    ("cylinder_components", "圆柱的构成", "Parts of Cylinder", "concept", "geometry",
     ["小学六年级"], ["circle"], 3, 10, 30),
    ("cylinder_surface_area", "圆柱的表面积", "Surface Area of Cylinder", "concept", "geometry",
     ["小学六年级"], ["cylinder_components"], 5, 10, 90),
    ("cylinder_volume_p6", "圆柱的体积", "Volume of Cylinder", "concept", "geometry",
     ["小学六年级"], ["cylinder_surface_area"], 5, 10, 90),
    ("cone_components", "圆锥的构成", "Parts of Cone", "concept", "geometry",
     ["小学六年级"], ["cylinder_components"], 3, 10, 30),
    ("cone_volume", "圆锥的体积", "Volume of Cone", "concept", "geometry",
     ["小学六年级"], ["cone_components", "cylinder_volume_p6"], 5, 10, 90),

    # 六年级 - 统计与概率
    ("扇形统计图_p6", "扇形统计图", "Pie Chart", "concept", "statistics",
     ["小学六年级"], ["pie_chart"], 4, 10, 60),
    ("choices_combinations", "搭配问题", "Combination Problems", "concept", "statistics",
     ["小学六年级"], [], 3, 10, 60),
    ("probability_experiment", "简单概率实验", "Simple Probability Experiments", "concept", "probability",
     ["小学六年级"], ["possibility"], 3, 10, 60),
    ("theoretical_probability", "用分数表示可能性大小", "Theoretical Probability", "concept", "probability",
     ["小学六年级"], ["probability_experiment", "fraction_concept"], 4, 10, 60),

    # 六年级 - 负数
    ("negative_number_p6", "负数的认识", "Introduction to Negative Numbers", "concept", "arithmetic",
     ["小学六年级"], [], 2, 10, 45),
    ("number_line_negative", "数轴上的负数", "Negative Numbers on Number Line", "concept", "arithmetic",
     ["小学六年级"], ["negative_number_p6", "number_line"], 3, 10, 45),
    ("compare_negative", "正负数的大小比较", "Comparing Positive and Negative Numbers", "concept", "arithmetic",
     ["小学六年级"], ["number_line_negative"], 3, 10, 45),
    ("opposite_number_p6", "相反数", "Opposite Numbers", "concept", "arithmetic",
     ["小学六年级"], ["number_line_negative"], 3, 10, 45),
    ("absolute_value_p6", "绝对值", "Absolute Value", "concept", "arithmetic",
     ["小学六年级"], ["compare_negative"], 3, 10, 45),
    ("add_negative_numbers", "有理数加法", "Addition of Rational Numbers", "concept", "arithmetic",
     ["小学六年级"], ["negative_number_p6"], 4, 10, 60),
    ("rational_number_p6", "有理数", "Rational Numbers", "concept", "arithmetic",
     ["小学六年级"], ["add_negative_numbers"], 4, 10, 60),
]


def sanitize_id(node_id):
    """清理ID，移除中文和空格"""
    # 只保留字母数字和下划线
    return re.sub(r'[^a-z0-9_]', '', node_id.lower().replace(' ', '_'))


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_ids = {n['id'] for n in data['nodes']}
    existing_names = {n['name']['zh'] for n in data['nodes']}
    added = 0
    skipped = 0

    for spec in NEW_PRIMARY_NODES:
        (raw_id, name_zh, name_en, ntype, branch, tags, prereqs, diff, imp, mins) = spec

        node_id = sanitize_id(raw_id)

        # 跳过已存在的节点
        if node_id in existing_ids or name_zh in existing_names:
            skipped += 1
            continue

        # 清理prereqs中的无效ID
        prereqs = [sanitize_id(p) for p in prereqs if sanitize_id(p)]

        node = {
            "id": node_id,
            "type": ntype,
            "name": {"zh": name_zh, "en": name_en},
            "description": {"zh": name_zh, "en": name_en},
            "level": "primary",
            "branch": branch,
            "tags": tags,
            "prerequisites": prereqs,
            "difficulty": diff,
            "importance": imp,
            "estimated_minutes": mins
        }

        data['nodes'].append(node)
        added += 1

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 新增 {added} 个节点")
    print(f"⏭️  跳过（已存在）{skipped} 个")


if __name__ == "__main__":
    main()
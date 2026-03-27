#!/usr/bin/env python3
"""
数学知识图谱 — 边增强脚本
① 创建年级章节节点（星形结构）
② 补全同年级内的先修链条
③ 将孤立节点接入网络
"""

import json
import re

DATA_FILE = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"

# ----------------------------------------------------------
# 第一部分：年级章节节点定义
# 每个章节节点，members 为应连接到此章节的节点ID前缀
# ----------------------------------------------------------
CHAPTERS = [
    # ===== 小学一年级 =====
    {"id": "ch_p1_numbers", "name": "数的认识与运算", "grade": "小学一年级",
     "branch": "arithmetic", "members": [
         "number_1_to_5","number_6_to_10","number_11_to_20","number_composition",
         "counting_by_group","compare_within_20","addition_within_10","addition_within_20",
         "subtraction_within_20","number_order_position",
         "cardinal_number","ordinal_number",
     ]},
    {"id": "ch_p1_shapes", "name": "图形与几何", "grade": "小学一年级",
     "branch": "geometry", "members": [
         "recognize_square","recognize_rectangle","recognize_triangle_p1","recognize_circle",
         "distinguish_2d_3d",
         "position_left_right","position_up_down","position_front_back",
         "row_column_position","relative_position",
     ]},
    {"id": "ch_p1_measurement", "name": "认识时间与货币", "grade": "小学一年级",
     "branch": "arithmetic", "members": [
         "recognize_rmb_1","rmb_exchange","rmb_add_sub",
     ]},
    {"id": "ch_p1_classify", "name": "分类与可能性", "grade": "小学一年级",
     "branch": "statistics", "members": [
         "classify_objects","sort_and_count","tally_mark","possibility",
     ]},

    # ===== 小学二年级 =====
    {"id": "ch_p2_numbers", "name": "100以内数与乘法", "grade": "小学二年级",
     "branch": "arithmetic", "members": [
         "number_100","hundreds_place","compare_100","estimate_count",
         "multiplication","multiplication_meaning_p2","multiplication_table_2_5","multiplication_table_6_9",
         "multiplication_commutative","multiplication_associative","multiplication_distributive",
         "division","division_meaning_p2","division_table","division_remainder",
         "even_number","odd_number",
     ]},
    {"id": "ch_p2_geometry", "name": "角与长度", "grade": "小学二年级",
     "branch": "geometry", "members": [
         "observe_from_front","cube_faces","cube",
         "length_unit_m","length_unit_cm","measure_length","line_segment_measure",
         "read_clock_face","read_exact_time","time_sequence",
         "angle_p","angle_right_p","angle_acute_p","angle_obtuse_p",
     ]},
    {"id": "ch_p2_statistics", "name": "数据收集与统计", "grade": "小学二年级",
     "branch": "statistics", "members": [
         "collect_data_p2","survey_method","simple_picture_graph","bar_chart",
     ]},

    # ===== 小学三年级 =====
    {"id": "ch_p3_numbers", "name": "万以内数与乘除", "grade": "小学三年级",
     "branch": "arithmetic", "members": [
         "number_1000","thousands_place","number_10000","ten_thousand_place",
         "round_number","approx_estimate",
         "two_digit_times_one","three_digit_times_one","division_one_digit",
         "addition","addition_meaning","addition_commutative","addition_associative",
         "subtraction","subtraction_meaning","subtraction_borrow",
         "natural_numbers","natural_number","zero","whole_numbers",
         "counting_unit","decimal_system","digit_place",
     ]},
    {"id": "ch_p3_fractions", "name": "分数的初步认识", "grade": "小学三年级",
     "branch": "arithmetic", "members": [
         "fractions","fraction_concept","fraction_unit","fraction_half_quarter",
         "proper_fraction","improper_fraction","mixed_number",
         "fraction_compare","compare_simple_fraction",
         "add_sub_simple_fraction","fraction_basic_property",
     ]},
    {"id": "ch_p3_geometry", "name": "面积与图形", "grade": "小学三年级",
     "branch": "geometry", "members": [
         "triangle","triangle_classify","triangle_angle_sum","triangle_p",
         "triangle_by_angle_p","triangle_by_side_p","triangle_stability",
         "quadrilateral","rectangle","square","parallelogram","trapezoid",
         "area","area_rectangle","area_square","area_triangle","perimeter",
         "area_concept","area_unit","area_shadow","area_formula_direct",
         "parallelogram_p","rectangle_p","square_p","trapezoid_p",
     ]},
    {"id": "ch_p3_measurement", "name": "测量与时间", "grade": "小学三年级",
     "branch": "arithmetic", "members": [
         "length_unit_mm","length_unit_km","mass_unit_t",
         "time_unit_year_month","time_unit_hour_minute",
         "year_p","month_p","day_p","hour_p","minute_p","second_p",
         "meter_p","centimeter","millimeter","kilometer",
         "kilogram_p","gram_p",
         "eight_directions","describe_direction_distance",
     ]},
    {"id": "ch_p3_measurement", "name": "测量与时间", "grade": "小学三年级",
     "branch": "arithmetic", "members": [
         "length_unit_mm","length_unit_km","mass_unit_t",
         "time_unit_year_month","time_unit_hour_minute",
         "kilometer","square_meter_p",
     ]},
    {"id": "ch_p3_statistics_dir", "name": "统计与方向", "grade": "小学三年级",
     "branch": "statistics", "members": [
         "data_organization","statistical_table","bar_chart",
         "eight_directions","describe_direction_distance",
     ]},

    # ===== 小学四年级 =====
    {"id": "ch_p4_numbers", "name": "大数与运算", "grade": "小学四年级",
     "branch": "arithmetic", "members": [
         "number_100_million","hundred_million_place","number_1000_million","counting_nature",
         "multiplication_distributive",
         "rmb_yuan","rmb_jiao","rmb_fen",
     ]},
    {"id": "ch_p4_angles", "name": "角的度量与四边形", "grade": "小学四年级",
     "branch": "geometry", "members": [
         "point_line_plane","line_straight","line_ray",
         "angle_measure_ degree","draw_angle","classify_angles","sum_of_angles_triangle",
         "parallelogram_prop","trapezoid_prop","quadrilateral_classify",
         "angle","acute_angle","right_angle","obtuse_angle","straight_angle","full_angle",
         "angle_measure","parallel","perpendicular","parallel_line_p","perpendicular_line_p",
         "translation","rotation","cuboid",
     ]},
    {"id": "ch_p4_statistics", "name": "统计与平均数", "grade": "小学四年级",
     "branch": "statistics", "members": [
         "bar_chart_p4","bar_chart_horizontal","data_analysis_average","compound_bar_chart",
         "average","line_chart","pie_chart",
     ]},
    {"id": "ch_p4_geometry_area", "name": "面积单位进阶", "grade": "小学四年级",
     "branch": "geometry", "members": [
         "area_formula_unified","area_unit_hectare","area_unit_km2","square_kilometer","hectare",
     ]},

    # ===== 小学五年级 =====
    {"id": "ch_p5_decimals", "name": "小数", "grade": "小学五年级",
     "branch": "arithmetic", "members": [
         "decimals","decimal_number","decimal_integer_part","decimal_fractional_part",
         "decimal_basic_property","decimal_precision","decimal_move_point","decimal_rounding",
         "decimal_add_sub","decimal_add_sub_p5","decimal_multiply","decimal_divide",
     ]},
    {"id": "ch_p5_factors", "name": "因数与倍数", "grade": "小学五年级",
     "branch": "arithmetic", "members": [
         "multiple","factor_divisor","divisible_by_2","divisible_by_5","divisible_by_3",
         "prime_number","composite_number","prime_factorization",
         "common_factor","gcf","common_multiple","lcm","coprime",
         "lcm_gcf_word",
     ]},
    {"id": "ch_p5_fraction_ops", "name": "分数运算", "grade": "小学五年级",
     "branch": "arithmetic", "members": [
         "fraction_add","fraction_multiply","fraction_divide",
         "fraction_add_sub_different_denom","mixed_number_calc","fraction_word_problems",
     ]},
    {"id": "ch_p5_transform", "name": "位置与图形变换", "grade": "小学五年级",
     "branch": "geometry", "members": [
         "cartesian_plane","plot_points","draw_translation","draw_rotation","draw_symmetry_axis",
         "composite_transform","coordinate_pair",
     ]},
    {"id": "ch_p5_statistics", "name": "统计进阶", "grade": "小学五年级",
     "branch": "statistics", "members": [
         "median_mode_p5","compound_table","compound_bar_chart_p5","compound_line_chart",
         "analyze_statistical_data",
     ]},
    {"id": "ch_p5_geometry_circle", "name": "圆", "grade": "小学五年级",
     "branch": "geometry", "members": [
         "circle","radius_diameter","circumference","circle_area",
         "circle_advance","pi_concept","circumference_formula","circle_area_derive",
     ]},

    # ===== 小学六年级 =====
    {"id": "ch_p6_fraction_ops", "name": "分数乘除法", "grade": "小学六年级",
     "branch": "arithmetic", "members": [
         "fraction_multiplication_p6","fraction_times_fraction","reciprocal",
         "fraction_division_p6","fraction_word_p6",
     ]},
    {"id": "ch_p6_percent", "name": "百分数", "grade": "小学六年级",
     "branch": "arithmetic", "members": [
         "percentage","percent_convert","percent_word_problems","increase_decrease_percent","tax_interest",
     ]},
    {"id": "ch_p6_ratio", "name": "比和比例", "grade": "小学六年级",
     "branch": "arithmetic", "members": [
         "ratio","ratio_simplify","proportion","ratio_concept","ratio_value",
         "ratio_basic_property","proportion_basic_property","ratio_extend","ratio_word_problems",
         "direct_proportion","inverse_proportion","proportionality","solve_proportion",
         "scale_p","scale_drawing",
     ]},
    {"id": "ch_p6_circle_solid", "name": "圆与圆柱圆锥", "grade": "小学六年级",
     "branch": "geometry", "members": [
         "annulus_area","sector","sector_area",
         "cylinder_components","cylinder_surface_area","cylinder_volume_p6",
         "cone_components","cone_volume",
     ]},
    {"id": "ch_p6_negative", "name": "负数初步", "grade": "小学六年级",
     "branch": "arithmetic", "members": [
         "negative_number_p6","number_line_negative","compare_negative",
         "opposite_number_p6","absolute_value_p6","add_negative_numbers","rational_number_p6",
     ]},
    {"id": "ch_p6_statistics_prob", "name": "统计与概率", "grade": "小学六年级",
     "branch": "statistics", "members": [
         "扇形统计图_p6","choices_combinations","probability_experiment","theoretical_probability",
     ]},

    # ===== 初中一年级 =====
    {"id": "ch_j1_numbers", "name": "有理数", "grade": "初中一年级",
     "branch": "arithmetic", "members": [
         "negative_numbers","integers","positive_number","negative_number",
         "rational_numbers","rational_number","number_line","opposite_number",
         "absolute_value","absolute_value_j","rational_comparison",
         "rational_addition","rational_subtraction","rational_multiplication","rational_division",
         "power_j","irrational_numbers","irrational_number","real_numbers","real_number",
     ]},
    {"id": "ch_j1_algebra", "name": "整式与一元方程", "grade": "初中一年级",
     "branch": "algebra", "members": [
         "variable","variable_j2","constant_j2","variable_constant","expression",
         "monomial","monomial_coefficient","monomial_degree",
         "polynomial","polynomial_term","like_terms","combine_like_terms",
         "algebraic_expression",
         "equation","linear_one","linear_equation_one",
     ]},
    {"id": "ch_j1_geometry_foundation", "name": "几何基础", "grade": "初中一年级",
     "branch": "geometry", "members": [
         "euclidean_point","euclidean_line","euclidean_plane",
         "angle_right","angle_acute","angle_obtuse",
         "triangle_definition","triangle_by_sides","triangle_by_angles",
         "solid_figure","plane_figure_j","point_line_plane_j",
         "two_points_determine_line","shortest_line_segment","midpoint",
     ]},
    {"id": "ch_j1_angles_lines", "name": "角与线", "grade": "初中一年级",
     "branch": "geometry", "members": [
         "angle_degree_minute_second","angle_bisector_j",
         "complementary_angle","supplementary_angle","adjacent_supplementary","vertical_angles",
         "perpendicular_j","perpendicular_lines","parallel_lines",
     ]},
    {"id": "ch_j1_statistics", "name": "数据的收集与描述", "grade": "初中一年级",
     "branch": "statistics", "members": [
         "data_collection","mean","median","mode","population","sample",
         "median_j","mode_j",
         "impossible_event_j","random_event_j",
     ]},

    # ===== 初中二年级 =====
    {"id": "ch_j2_algebra", "name": "整式运算与因式分解", "grade": "初中二年级",
     "branch": "algebra", "members": [
         "power_operations","polynomial_multiplication",
         "difference_of_squares","perfect_square",
         "factoring","factorization","factor_common","factor_formula","cross_factorization",
         "linear_two","linear_system","linear_equation_two","system_linear_eq",
         "substitution_elimination","addition_elimination",
         "inequality","linear_inequality","inequality_properties","linear_inequality_system",
     ]},
    {"id": "ch_j2_congruent", "name": "全等三角形", "grade": "初中二年级",
     "branch": "geometry", "members": [
         "congruent","triangle_congruence","sss","sas","asa","hl_j",
         "isosceles_triangle_j","equilateral_triangle_j","right_triangle","right_triangle_j",
         "pythagorean","pythagorean_theorem","pythagorean_triple",
         "special_right",
     ]},
    {"id": "ch_j2_quadrilaterals", "name": "四边形", "grade": "初中二年级",
     "branch": "geometry", "members": [
         "quad_props","parallelogram","rhombus","square_geo",
         "polygon_j","polygon_angle_sum",
         "parallelogram_j","rectangle_j","rhombus_j","square_j","trapezoid_j","isosceles_trapezoid",
     ]},
    {"id": "ch_j2_function_intro", "name": "函数初步", "grade": "初中二年级",
     "branch": "algebra", "members": [
         "function_concept_j","function_representation",
         "direct_proportional_function","linear_function_j","inverse_proportional_function",
         "quadratic_function_j",
     ]},
    {"id": "ch_j2_statistics_var", "name": "数据的波动", "grade": "初中二年级",
     "branch": "statistics", "members": [
         "variance_junior","variance_j","standard_deviation",
     ]},

    # ===== 初中三年级 =====
    {"id": "ch_j3_radical", "name": "二次根式", "grade": "初中三年级",
     "branch": "algebra", "members": [
         "square_root","cube_root","arithmetic_square_root",
         "quadratic_radical","simplest_radical","radical_properties","denominator_rationalization",
     ]},
    {"id": "ch_j3_quadratic", "name": "一元二次方程", "grade": "初中三年级",
     "branch": "algebra", "members": [
         "quadratic","quadratic_equation","quadratic_formula","discriminant","vieta_theorem",
         "fractional_equation",
     ]},
    {"id": "ch_j3_similar", "name": "相似三角形", "grade": "初中三年级",
     "branch": "geometry", "members": [
         "similar","aa_similarity","similar_polygons","similar_triangles",
     ]},
    {"id": "ch_j3_circle", "name": "圆", "grade": "初中三年级",
     "branch": "geometry", "members": [
         "circle_theorems","circle_definition","circle_radius_diameter",
         "circle_chord","circle_arc","circle_tangent","circle_angle_theorem","perpendicular_diameter",
         "circle_j","chord_j","arc_j","central_angle","inscribed_angle",
         "tangent_j","tangent_radius_perpendicular",
         "triangle_centroid","triangle_orthocenter","triangle_incenter","triangle_circumcenter",
     ]},
    {"id": "ch_j3_trig_intro", "name": "锐角三角函数", "grade": "初中三年级",
     "branch": "trigonometry", "members": [
         "trig_ratio","sine","cosine","tangent","trig_ratio_def_j","sin_cos_tan_j",
         "trig_values_30_45_60_j","trig_identities_j","solve_right_triangle_j",
         "special_angle_30","special_angle_45","special_angle_60","special_angle_0_90",
     ]},
    {"id": "ch_j3_prob_comb", "name": "概率与统计", "grade": "初中三年级",
     "branch": "probability", "members": [
         "probability","classical_probability","list_method_prob","tree_diagram_prob",
         "set_theory","set_operations","permutation","combination",
     ]},
    {"id": "ch_j3_trig_angle_system", "name": "角的度量体系", "grade": "初中三年级",
     "branch": "trigonometry", "members": [
         "angle_concept","initial_side","terminal_side","positive_angle","negative_angle","zero_angle",
         "degree_system","minute_second","quadrantal_angle","coterminal_angle",
     ]},

    # ===== 高中一年级 =====
    {"id": "ch_s1_set_function", "name": "集合与函数", "grade": "高中一年级",
     "branch": "algebra", "members": [
         "set_concept","set_element","number_sets","set_representation","subset","proper_subset","empty_set",
         "intersection_set","union_set","complement_set","set_math","universal_set","power_set",
         "set_union","set_intersection","set_difference","set_complement","symmetric_difference",
         "function","domain","range","function_concept_s","function_domain_s","function_basic",
         "function_monotonicity","function_monotonicity_calc","function_periodicity","function_periodicity_calc",
         "function_even_odd","function_even_odd_s","function_zero_point","function_boundedness",
         "dichotomy","elementary_functions",
         "linear_func","linear_func_s","quadratic_func","quadratic_func_s",
         "power_function","power_func","power_func_s",
         "exponential","exponential_func_s","exponential_function",
         "logarithm","log_func","log_func_s","logarithm_s","logarithmic_function","logarithm_operations",
         "inverse_func","inverse_func_s","composite_func","composite_func_s",
     ]},
    {"id": "ch_s1_trig", "name": "三角函数", "grade": "高中一年级",
     "branch": "trigonometry", "members": [
         "unit_circle","unit_circle_s","radian","radian_system","degree_radian_conversion",
         "trig_functions","trig_circ_def_s","trig_sign_s","trig_signs",
         "trig_identities","trig_identities_s","trig_reciprocal","trig_quotient",
         "pythagorean_identity","sine_def","cosine_def","tangent_def","cotangent_def","secant_def","cosecant_def",
         "induction_formula","trig_periodicity","unit_circle_sin_cos",
         "addition_formula_s","sin_add","sin_sub","cos_add","cos_sub","tan_add",
         "double_angle_s","double_angle_sin","double_angle_cos","double_angle_tan",
         "half_angle_s","half_angle_sin","half_angle_cos","half_angle_tan",
         "power_reduction","product_to_sum","sum_to_product","universal_substitution",
         "trig_equations","trig_equation_s","sin_graph","cos_graph","tan_graph",
         "amplitude_transform","period_transform","phase_transform","general_sinusoidal",
     ]},
    {"id": "ch_s1_sequence", "name": "数列", "grade": "高中一年级",
     "branch": "algebra", "members": [
         "sequence","sequence_s","sequence_concept","arithmetic_seq","arithmetic_seq_s",
         "arithmetic_sequence","arithmetic_formula","arithmetic_sum","arithmetic_sum_s","arithmetic_mean",
         "geometric_seq","geometric_seq_s","geometric_sequence","geometric_formula","geometric_sum","geometric_sum_s","geometric_mean",
         "sequence_summation_methods","sequence_concept",
     ]},
    {"id": "ch_s1_inequality", "name": "不等式", "grade": "高中一年级",
     "branch": "algebra", "members": [
         "inequality_relation","inequality_property","quadratic_inequality","mean_inequality","linear_programming",
     ]},
    {"id": "ch_s1_logic", "name": "逻辑与命题", "grade": "高中一年级",
     "branch": "logic", "members": [
         "four_propositions","sufficient_condition","necessary_condition","necessary_sufficient_condition",
         "logical_connectives","quantifier","logical_connective","negation","conjunction","disjunction","implication","equivalence_logical",
     ]},
    {"id": "ch_s1_counting", "name": "计数原理", "grade": "高中一年级",
     "branch": "discrete", "members": [
         "addition_counting","multiplication_counting","math_induction","mathematical_induction","binomial","binomial_theorem","binomial_term",
     ]},

    # ===== 高中二年级 =====
    {"id": "ch_s2_analytic_geo", "name": "解析几何", "grade": "高中二年级",
     "branch": "geometry", "members": [
         "cartesian","cartesian_s","line_eq","circle_eq","ellipse","hyperbola","parabola","conic",
         "distance_s","trig_ratio","sine","cosine","tangent","sine_def","cosine_def","tangent_def",
         "cotangent_def","secant_def","cosecant_def","trig_ratio_def_j","sin_cos_tan_j",
     ]},
    {"id": "ch_s2_complex", "name": "复数", "grade": "高中二年级",
     "branch": "algebra", "members": [
         "complex","imaginary_unit","complex_number","real_part","imaginary_part",
         "pure_imaginary","complex_modulus","conjugate_complex",
     ]},
    {"id": "ch_s2_prob_stat", "name": "概率与统计", "grade": "高中二年级",
     "branch": "probability", "members": [
         "random_event_p","event_relation_p","probability_def_p","classical_prob_p","geometric_prob_p",
         "conditional_prob_p","independent_events_p","event_independence",
         "bernoulli_trial_p","binomial_dist_p","binomial_distribution",
         "hypergeometric_distribution","variance_h","probability_theory","random_variable","expectation","variance","distribution",
         "conditional_probability","probability_distribution","random_variable_p","distribution_law_p","expectation_p","variance_p",
         "simple_random_sampling","systematic_sampling","stratified_sampling","frequency_distribution",
         "scatter_plot","regression_line","chi_square_test","inductive_reasoning","analogical_reasoning","deductive_reasoning",
         "synthesis_method","analysis_method","proof_by_contradiction","variance_j",
     ]},

    # ===== 高中三年级 =====
    {"id": "ch_s3_calculus", "name": "导数与积分", "grade": "高中三年级",
     "branch": "analysis", "members": [
         "limit","limit_concept_s","limit_calc_s","continuity","continuity_s",
         "infinitesimal","infinite","one_sided_limit",
         "derivative","derivative_def_s","derivative_rule_s","diff_rules","diff_applications",
         "basic_derivative_formulas","derivative_product_quotient","monotonicity_derivative_s",
         "extreme_value_s","max_min_s","differential_concept",
         "integration","definite_integral","fundamental_theorem","integral_concept_s",
         "antiderivative_s","indefinite_integral_s","definite_integral_s","newton_leibniz_s",
         "integral_area_s","integral_volume_s","integral_geometric_meaning","integral_properties",
         "inverse_trig","inverse_trig_s","inverse_func","inverse_func_s",
         "trig_equations","trig_equation_s","trig_identities","trig_identities_s",
         "angle_measure_s",
     ]},
    {"id": "ch_s3_space_geo", "name": "空间几何与向量", "grade": "高中三年级",
     "branch": "geometry", "members": [
         "spatial_geometry","plane_in_space","spatial_vector","space_coordinate",
         "space_vector_operation","dot_product","cross_product",
         "space_plane_equation","space_line_equation","space_line_plane","skew_lines","dihedral_angle",
         "prism","pyramid","cylinder_geo","cone_geo","sphere_geo","surface_area_calc","volume_calc",
         "euclidean_parallel_postulate","menelaus_theorem","ceva_theorem","ptolemy_theorem",
     ]},
    {"id": "ch_s3_distributions", "name": "常用分布", "grade": "高中三年级",
     "branch": "probability", "members": [
         "normal_distribution","normal_dist_p","normal_standardize","chi_square_distribution",
         "t_distribution","f_distribution","gamma_distribution","beta_distribution",
         "poisson_dist","geometric_dist","hypergeometric_dist","bernoulli_dist","rv_concept","distribution_function_p",
         "discrete_rv","prob_distribution","continuous_rv","pdf","uniform_dist_p","exponential_dist_p",
         "standard_normal_p","rv_function","random_vector","joint_dist","marginal_dist",
         "conditional_dist_p","rv_independence","convolution","max_min_dist",
         "chi_square_test","point_estimation","hypothesis_testing","linear_regression_stat","least_squares_stat",
     ]},
]


# ----------------------------------------------------------
# 第二部分：同年级内的先修链
# 格式：(from_id, to_id)  from是to的先修
# ----------------------------------------------------------
CURRICULUM_PREREQS = [
    # ===== 小学一年级内部 =====
    ("number_1_to_5", "number_6_to_10"),
    ("number_6_to_10", "number_11_to_20"),
    ("number_11_to_20", "counting_by_group"),
    ("number_11_to_20", "compare_within_20"),
    ("number_1_to_5", "addition_within_10"),
    ("addition_within_10", "addition_within_20"),
    ("addition_within_10", "subtraction_within_20"),
    ("number_1_to_5", "number_composition"),
    ("recognize_circle", "circle_center"),
    ("recognize_circle", "circle_radius_p"),
    ("recognize_circle", "circle_diameter_p"),
    ("position_left_right", "row_column_position"),
    ("position_up_down", "row_column_position"),
    ("position_front_back", "row_column_position"),
    ("point_line_plane", "line_straight"),
    ("point_line_plane", "line_ray"),
    ("line_straight", "angle_p"),
    ("line_ray", "angle_p"),
    ("angle_p", "angle_right_p"),
    ("angle_p", "angle_acute_p"),
    ("angle_p", "angle_obtuse_p"),
    ("recognize_square", "distinguish_2d_3d"),
    ("recognize_circle", "distinguish_2d_3d"),
    ("distinguish_2d_3d", "cuboid"),

    # ===== 小学二年级内部 =====
    ("number_11_to_20", "number_100"),
    ("number_100", "hundreds_place"),
    ("multiplication_meaning_p2", "multiplication_table_2_5"),
    ("multiplication_table_2_5", "multiplication_table_6_9"),
    ("multiplication_table_2_5", "division_meaning_p2"),
    ("division_meaning_p2", "division_table"),
    ("division_table", "division_remainder"),
    ("multiplication_table_2_5", "multiplication_distributive"),
    ("multiplication_distributive", "two_digit_times_one"),
    ("two_digit_times_one", "three_digit_times_one"),
    ("division_table", "division_one_digit"),
    ("division_one_digit", "two_digit_times_one"),
    ("measure_length", "line_segment_measure"),
    ("read_clock_face", "read_exact_time"),
    ("read_exact_time", "time_sequence"),
    ("observe_from_front", "cube_faces"),

    # ===== 小学三年级内部 =====
    ("number_100", "number_1000"),
    ("number_1000", "thousands_place"),
    ("number_1000", "number_10000"),
    ("number_10000", "ten_thousand_place"),
    ("number_10000", "round_number"),
    ("round_number", "approx_estimate"),
    ("three_digit_times_one", "two_digit_times_one"),
    ("multiplication_table_6_9", "two_digit_times_one"),
    ("division_one_digit", "two_digit_times_one"),
    ("division_one_digit", "three_digit_times_one"),
    ("length_unit_cm", "length_unit_mm"),
    ("length_unit_m", "length_unit_km"),
    ("length_unit_m", "kilometer"),
    ("fraction_concept", "fraction_unit"),
    ("fraction_unit", "fraction_half_quarter"),
    ("fraction_concept", "fraction_compare"),
    ("fraction_compare", "compare_simple_fraction"),
    ("fraction_concept", "proper_fraction"),
    ("fraction_concept", "improper_fraction"),
    ("proper_fraction", "mixed_number"),
    ("fraction_half_quarter", "fraction_compare"),
    ("compare_simple_fraction", "add_sub_simple_fraction"),
    ("fraction_compare", "fraction_basic_property"),
    ("fraction_basic_property", "fraction_add"),
    ("fraction_basic_property", "fraction_multiply"),
    ("add_sub_simple_fraction", "fraction_add"),
    ("fractions", "fraction_concept"),
    ("fractions", "fraction_unit"),
    ("fractions", "fraction_compare"),
    ("fractions", "fraction_add"),
    ("fractions", "fraction_multiply"),
    ("fractions", "fraction_divide"),
    ("triangle", "triangle_classify"),
    ("triangle", "triangle_angle_sum"),
    ("triangle_classify", "triangle_by_angle_p"),
    ("triangle_classify", "triangle_by_side_p"),
    ("triangle", "rectangle"),
    ("rectangle", "square"),
    ("parallel", "parallelogram"),
    ("parallel", "trapezoid"),
    ("parallel_line_p", "parallelogram"),
    ("perpendicular_line_p", "parallelogram"),
    ("perpendicular", "trapezoid"),
    ("area", "area_rectangle"),
    ("area", "area_square"),
    ("area_rectangle", "area_formula_direct"),
    ("area_square", "area_formula_direct"),
    ("area_shadow", "area_formula_direct"),
    ("rectangle", "area_rectangle"),
    ("square", "area_square"),
    ("triangle", "area_triangle"),
    ("area_concept", "area_unit"),
    ("area_unit", "area_shadow"),

    # ===== 小学四年级内部 =====
    ("number_10000", "number_100_million"),
    ("number_100_million", "hundred_million_place"),
    ("number_100_million", "number_1000_million"),
    ("multiplication_distributive", "number_100_million"),
    ("parallel", "angle_measure_ degree"),
    ("angle_measure_ degree", "draw_angle"),
    ("angle_measure_ degree", "classify_angles"),
    ("classify_angles", "sum_of_angles_triangle"),
    ("sum_of_angles_triangle", "parallelogram_prop"),
    ("parallelogram_prop", "quadrilateral_classify"),
    ("parallelogram_prop", "trapezoid_prop"),
    ("bar_chart", "bar_chart_p4"),
    ("bar_chart_p4", "compound_bar_chart"),
    ("average", "data_analysis_average"),
    ("data_analysis_average", "compound_bar_chart"),
    ("bar_chart_p4", "bar_chart_horizontal"),
    ("area_unit", "area_formula_unified"),
    ("area_rectangle", "area_formula_unified"),
    ("area_square", "area_formula_unified"),
    ("square_kilometer", "area_unit_km2"),
    ("hectare", "area_unit_km2"),

    # ===== 小学五年级内部 =====
    ("decimal_integer_part", "decimal_basic_property"),
    ("decimal_basic_property", "decimal_precision"),
    ("decimal_precision", "decimal_move_point"),
    ("decimal_move_point", "decimal_rounding"),
    ("decimal_move_point", "decimal_multiply"),
    ("decimal_multiply", "decimal_divide"),
    ("decimal_move_point", "decimal_add_sub_p5"),
    ("fraction_basic_property", "decimal_precision"),  # 类比迁移
    ("multiple", "factor_divisor"),
    ("factor_divisor", "divisible_by_2"),
    ("factor_divisor", "divisible_by_5"),
    ("factor_divisor", "divisible_by_3"),
    ("divisible_by_2", "prime_number"),
    ("divisible_by_3", "prime_number"),
    ("prime_number", "composite_number"),
    ("factor_divisor", "common_factor"),
    ("common_factor", "gcf"),
    ("multiple", "common_multiple"),
    ("common_multiple", "lcm"),
    ("gcf", "lcm_gcf_word"),
    ("lcm", "lcm_gcf_word"),
    ("factor_divisor", "prime_factorization"),
    ("prime_factorization", "lcm_gcf_word"),
    ("fraction_add", "fraction_add_sub_different_denom"),
    ("fraction_add_sub_different_denom", "mixed_number_calc"),
    ("fraction_multiply", "fraction_times_fraction"),
    ("fraction_times_fraction", "fraction_division_p6"),
    ("fraction_division_p6", "fraction_word_p6"),
    ("fraction_times_fraction", "reciprocal"),
    ("cartesian_plane", "plot_points"),
    ("draw_translation", "draw_rotation"),
    ("draw_translation", "draw_symmetry_axis"),
    ("draw_symmetry_axis", "composite_transform"),
    ("draw_rotation", "composite_transform"),
    ("fraction_concept", "percent_convert"),
    ("percentage", "percent_convert"),
    ("decimal_move_point", "percent_convert"),
    ("circle_advance", "circumference_formula"),
    ("pi_concept", "circumference_formula"),
    ("circumference_formula", "circle_area_derive"),
    ("circle_area_derive", "annulus_area"),
    ("circle", "sector"),
    ("sector", "sector_area"),

    # ===== 小学六年级内部 =====
    ("fraction_multiply", "fraction_multiplication_p6"),
    ("fraction_multiplication_p6", "fraction_times_fraction"),
    ("fraction_times_fraction", "reciprocal"),
    ("reciprocal", "fraction_division_p6"),
    ("fraction_division_p6", "fraction_word_p6"),
    ("percent_convert", "percent_word_problems"),
    ("percent_word_problems", "increase_decrease_percent"),
    ("percent_word_problems", "tax_interest"),
    ("ratio", "ratio_extend"),
    ("ratio_extend", "ratio_word_problems"),
    ("ratio_word_problems", "scale_drawing"),
    ("direct_proportion", "proportionality"),
    ("inverse_proportion", "proportionality"),
    ("proportionality", "solve_proportion"),
    ("cylinder_components", "cylinder_surface_area"),
    ("cylinder_components", "cylinder_volume_p6"),
    ("cylinder_volume_p6", "cone_volume"),
    ("cone_components", "cone_volume"),
    ("negative_number_p6", "number_line_negative"),
    ("number_line_negative", "compare_negative"),
    ("compare_negative", "opposite_number_p6"),
    ("opposite_number_p6", "absolute_value_p6"),
    ("compare_negative", "add_negative_numbers"),
    ("add_negative_numbers", "rational_number_p6"),
    ("circle_area_derive", "annulus_area"),
    ("sector_area", "annulus_area"),
    ("possibility", "probability_experiment"),
    ("probability_experiment", "theoretical_probability"),

    # ===== 初中一年级内部 =====
    ("negative_numbers", "rational_numbers"),
    ("rational_numbers", "real_numbers"),
    ("number_line", "absolute_value"),
    ("absolute_value", "rational_comparison"),
    ("rational_comparison", "rational_addition"),
    ("rational_addition", "rational_subtraction"),
    ("rational_addition", "rational_multiplication"),
    ("rational_multiplication", "rational_division"),
    ("rational_division", "power_j"),
    ("power_j", "square_root"),
    ("power_j", "cube_root"),
    ("power_j", "arithmetic_square_root"),
    ("power_j", "irrational_numbers"),
    ("irrational_numbers", "real_numbers"),
    ("real_numbers", "real_number"),
    ("variable", "expression"),
    ("expression", "monomial"),
    ("monomial", "polynomial"),
    ("like_terms", "combine_like_terms"),
    ("combine_like_terms", "algebraic_expression"),
    ("polynomial", "algebraic_expression"),
    ("algebraic_expression", "equation"),
    ("equation", "linear_one"),
    ("linear_one", "linear_equation_one"),
    ("euclidean_point", "euclidean_line"),
    ("euclidean_line", "euclidean_plane"),
    ("euclidean_point", "angle_right"),
    ("euclidean_line", "angle_acute"),
    ("triangle_definition", "triangle_by_sides"),
    ("triangle_definition", "triangle_by_angles"),
    ("solid_figure", "plane_figure_j"),
    ("solid_figure", "point_line_plane_j"),
    ("point_line_plane_j", "plane_figure_j"),
    ("euclidean_line", "two_points_determine_line"),
    ("two_points_determine_line", "shortest_line_segment"),
    ("two_points_determine_line", "midpoint"),
    ("euclidean_point", "angle_right"),
    ("angle_right", "complementary_angle"),
    ("angle_right", "supplementary_angle"),
    ("complementary_angle", "angle_bisector_j"),
    ("supplementary_angle", "adjacent_supplementary"),
    ("euclidean_line", "vertical_angles"),
    ("angle_right", "perpendicular_j"),
    ("perpendicular_j", "parallel_lines"),
    ("perpendicular_j", "perpendicular_lines"),
    ("mean", "median"),
    ("mean", "mode"),
    ("median", "median_j"),
    ("mode", "mode_j"),
    ("data_collection", "mean"),
    ("impossible_event_j", "random_event_j"),

    # ===== 初中二年级内部 =====
    ("polynomial", "power_operations"),
    ("power_operations", "polynomial_multiplication"),
    ("polynomial_multiplication", "difference_of_squares"),
    ("polynomial_multiplication", "perfect_square"),
    ("difference_of_squares", "factor_formula"),
    ("perfect_square", "factor_formula"),
    ("factor_formula", "factoring"),
    ("factoring", "factorization"),
    ("factorization", "factor_common"),
    ("factor_common", "cross_factorization"),
    ("algebraic_expression", "fractional_expression"),
    ("fractional_expression", "fraction_reduction"),
    ("fraction_reduction", "fraction_addition"),
    ("fraction_addition", "fractional_equation"),
    ("linear_equation_one", "linear_two"),
    ("linear_two", "linear_equation_two"),
    ("linear_two", "linear_system"),
    ("linear_system", "system_linear_eq"),
    ("linear_equation_two", "substitution_elimination"),
    ("linear_equation_two", "addition_elimination"),
    ("inequality", "inequality_properties"),
    ("inequality_properties", "linear_inequality"),
    ("linear_inequality", "linear_inequality_system"),
    ("number_line", "inequality"),
    ("absolute_value", "inequality"),
    ("triangle_by_sides", "congruent"),
    ("congruent", "sss"),
    ("congruent", "sas"),
    ("congruent", "asa"),
    ("congruent", "hl_j"),
    ("congruent", "isosceles_triangle_j"),
    ("isosceles_triangle_j", "equilateral_triangle_j"),
    ("congruent", "right_triangle"),
    ("right_triangle", "pythagorean"),
    ("right_triangle", "special_right"),
    ("pythagorean", "pythagorean_triple"),
    ("polygon_j", "quad_props"),
    ("polygon_j", "parallelogram_j"),
    ("parallelogram_j", "rectangle_j"),
    ("parallelogram_j", "rhombus_j"),
    ("rectangle_j", "square_j"),
    ("parallelogram_j", "trapezoid_j"),
    ("trapezoid_j", "isosceles_trapezoid"),
    ("quad_props", "parallelogram_prop"),
    ("parallelogram", "parallelogram_j"),
    ("rhombus", "rhombus_j"),
    ("square_geo", "square_j"),
    ("trapezoid", "trapezoid_j"),
    ("variable", "function_concept_j"),
    ("function_concept_j", "function_representation"),
    ("function_concept_j", "direct_proportional_function"),
    ("function_concept_j", "linear_function_j"),
    ("linear_function_j", "inverse_proportional_function"),
    ("function_representation", "quadratic_function_j"),
    ("variance_j", "standard_deviation"),

    # ===== 初中三年级内部 =====
    ("real_numbers", "square_root"),
    ("square_root", "arithmetic_square_root"),
    ("arithmetic_square_root", "quadratic_radical"),
    ("quadratic_radical", "simplest_radical"),
    ("simplest_radical", "radical_properties"),
    ("radical_properties", "denominator_rationalization"),
    ("square_root", "quadratic"),
    ("quadratic", "quadratic_equation"),
    ("quadratic_equation", "quadratic_formula"),
    ("quadratic_equation", "discriminant"),
    ("quadratic_formula", "vieta_theorem"),
    ("quadratic_radical", "fractional_equation"),
    ("fractional_equation", "quadratic_equation"),
    ("congruent", "similar"),
    ("similar", "aa_similarity"),
    ("similar", "similar_polygons"),
    ("similar", "similar_triangles"),
    ("similar", "special_right"),
    ("similar_polygons", "similar_triangles"),
    ("congruent", "right_triangle"),
    ("circle_definition", "circle_theorems"),
    ("circle_theorems", "circle_chord"),
    ("circle_theorems", "circle_arc"),
    ("circle_theorems", "circle_tangent"),
    ("circle_tangent", "circle_angle_theorem"),
    ("circle_tangent", "perpendicular_diameter"),
    ("central_angle", "inscribed_angle"),
    ("inscribed_angle", "circle_angle_theorem"),
    ("congruent", "triangle_centroid"),
    ("congruent", "triangle_orthocenter"),
    ("congruent", "triangle_incenter"),
    ("congruent", "triangle_circumcenter"),
    ("right_triangle", "trig_ratio"),
    ("trig_ratio", "sine"),
    ("trig_ratio", "cosine"),
    ("trig_ratio", "tangent"),
    ("sine", "sin_cos_tan_j"),
    ("cosine", "sin_cos_tan_j"),
    ("tangent", "sin_cos_tan_j"),
    ("sin_cos_tan_j", "trig_values_30_45_60_j"),
    ("trig_values_30_45_60_j", "solve_right_triangle_j"),
    ("sin_cos_tan_j", "special_right"),
    ("degree_system", "angle_concept"),
    ("angle_concept", "initial_side"),
    ("angle_concept", "terminal_side"),
    ("terminal_side", "positive_angle"),
    ("terminal_side", "negative_angle"),
    ("positive_angle", "quadrantal_angle"),
    ("positive_angle", "coterminal_angle"),
    ("degree_system", "radian_system"),
    ("radian_system", "degree_radian_conversion"),
    ("trig_ratio", "special_angle_30"),
    ("trig_ratio", "special_angle_45"),
    ("trig_ratio", "special_angle_60"),
    ("probability", "classical_probability"),
    ("classical_probability", "list_method_prob"),
    ("classical_probability", "tree_diagram_prob"),
    ("set_theory", "set_operations"),
    ("set_operations", "permutation"),
    ("set_operations", "combination"),
    ("permutation", "combination"),

    # ===== 高中一年级内部 =====
    ("set_concept", "set_element"),
    ("set_element", "number_sets"),
    ("number_sets", "empty_set"),
    ("set_element", "subset"),
    ("subset", "proper_subset"),
    ("subset", "intersection_set"),
    ("subset", "union_set"),
    ("intersection_set", "complement_set"),
    ("union_set", "complement_set"),
    ("number_sets", "function"),
    ("function", "domain"),
    ("function", "range"),
    ("domain", "function_concept_s"),
    ("function_concept_s", "function_monotonicity"),
    ("function_concept_s", "function_periodicity"),
    ("function_concept_s", "function_even_odd"),
    ("function_concept_s", "function_zero_point"),
    ("function_monotonicity", "dichotomy"),
    ("dichotomy", "quadratic_function_s"),
    ("function_concept_s", "elementary_functions"),
    ("elementary_functions", "linear_func_s"),
    ("elementary_functions", "quadratic_func_s"),
    ("elementary_functions", "power_func_s"),
    ("elementary_functions", "exponential_func_s"),
    ("elementary_functions", "log_func_s"),
    ("power_func_s", "power_function"),
    ("exponential_func_s", "exponential_function"),
    ("log_func_s", "logarithmic_function"),
    ("exponential", "logarithm"),
    ("exponential", "log_func"),
    ("logarithm", "log_func"),
    ("log_func", "logarithm_operations"),
    ("inverse_func_s", "composite_func_s"),
    ("composite_func_s", "inverse_func"),
    ("unit_circle", "trig_functions"),
    ("unit_circle", "radian"),
    ("radian", "trig_functions"),
    ("trig_functions", "trig_identities_s"),
    ("trig_identities_s", "addition_formula_s"),
    ("addition_formula_s", "double_angle_s"),
    ("double_angle_s", "half_angle_s"),
    ("trig_identities_s", "trig_equations"),
    ("trig_functions", "sin_graph"),
    ("trig_functions", "cos_graph"),
    ("trig_functions", "tan_graph"),
    ("sin_graph", "amplitude_transform"),
    ("sin_graph", "period_transform"),
    ("sin_graph", "phase_transform"),
    ("amplitude_transform", "general_sinusoidal"),
    ("period_transform", "general_sinusoidal"),
    ("phase_transform", "general_sinusoidal"),
    ("inverse_trig_s", "inverse_trig"),
    ("sequence_concept", "arithmetic_sequence"),
    ("sequence_concept", "geometric_sequence"),
    ("arithmetic_sequence", "arithmetic_formula"),
    ("arithmetic_formula", "arithmetic_sum"),
    ("arithmetic_sum", "arithmetic_mean"),
    ("geometric_sequence", "geometric_formula"),
    ("geometric_formula", "geometric_sum"),
    ("geometric_sum", "geometric_mean"),
    ("arithmetic_sum", "sequence_summation_methods"),
    ("geometric_sum", "sequence_summation_methods"),
    ("number_sets", "inequality_relation"),
    ("inequality_relation", "inequality_property"),
    ("inequality_property", "quadratic_inequality"),
    ("quadratic_inequality", "linear_programming"),
    ("quadratic_inequality", "mean_inequality"),
    ("four_propositions", "sufficient_condition"),
    ("four_propositions", "necessary_condition"),
    ("sufficient_condition", "necessary_sufficient_condition"),
    ("necessary_condition", "necessary_sufficient_condition"),
    ("sufficient_condition", "logical_connectives"),
    ("addition_counting", "multiplication_counting"),
    ("multiplication_counting", "mathematical_induction"),
    ("mathematical_induction", "binomial_theorem"),

    # ===== 高中二年级内部 =====
    ("cartesian", "line_eq"),
    ("cartesian", "circle_eq"),
    ("cartesian", "ellipse"),
    ("cartesian", "hyperbola"),
    ("cartesian", "parabola"),
    ("cartesian", "conic"),
    ("cartesian", "distance_s"),
    ("distance_s", "circle_eq"),
    ("ellipse", "hyperbola"),
    ("ellipse", "parabola"),
    ("hyperbola", "parabola"),
    ("circle_eq", "ellipse"),
    ("ellipse", "conic"),
    ("line_eq", "distance_s"),
    ("spatial_geometry", "space_coordinate"),
    ("space_coordinate", "space_vector_operation"),
    ("space_vector_operation", "dot_product"),
    ("space_vector_operation", "cross_product"),
    ("dot_product", "space_line_equation"),
    ("dot_product", "space_plane_equation"),
    ("space_coordinate", "space_line_plane"),
    ("spatial_geometry", "prism"),
    ("spatial_geometry", "pyramid"),
    ("spatial_geometry", "cylinder_geo"),
    ("spatial_geometry", "cone_geo"),
    ("spatial_geometry", "sphere_geo"),
    ("cylinder_geo", "surface_area_calc"),
    ("cylinder_geo", "volume_calc"),
    ("cone_geo", "volume_calc"),
    ("pyramid", "surface_area_calc"),
    ("prism", "surface_area_calc"),
    ("prism", "volume_calc"),
    ("random_event_p", "probability_def_p"),
    ("probability_def_p", "classical_prob_p"),
    ("probability_def_p", "geometric_prob_p"),
    ("classical_prob_p", "conditional_prob_p"),
    ("classical_prob_p", "independent_events_p"),
    ("conditional_prob_p", "bayes_formula"),
    ("independent_events_p", "bernoulli_trial_p"),
    ("bernoulli_trial_p", "binomial_distribution"),
    ("binomial_distribution", "binomial_dist_p"),
    ("random_variable", "distribution"),
    ("random_variable", "expectation"),
    ("random_variable", "variance"),
    ("expectation", "variance"),
    ("variance", "normal_distribution"),
    ("normal_distribution", "normal_standardize"),
    ("normal_standardize", "chi_square_test"),
    ("simple_random_sampling", "stratified_sampling"),
    ("simple_random_sampling", "systematic_sampling"),
    ("scatter_plot", "regression_line"),
    ("regression_line", "chi_square_test"),

    # ===== 高中三年级内部 =====
    ("limit", "continuity"),
    ("continuity", "derivative"),
    ("derivative", "derivative_rule_s"),
    ("derivative_rule_s", "diff_rules"),
    ("derivative_rule_s", "diff_applications"),
    ("diff_applications", "monotonicity_derivative_s"),
    ("diff_applications", "extreme_value_s"),
    ("extreme_value_s", "max_min_s"),
    ("derivative", "differential_concept"),
    ("differential_concept", "integration"),
    ("integration", "definite_integral"),
    ("definite_integral", "fundamental_theorem"),
    ("fundamental_theorem", "newton_leibniz_s"),
    ("definite_integral", "integral_area_s"),
    ("definite_integral", "integral_volume_s"),
    ("integral_area_s", "integral_volume_s"),
    ("inverse_trig", "integration"),
    ("trig_identities", "integration"),
    ("inverse_trig_s", "inverse_trig"),
    ("composite_func", "limit"),
    ("composite_func", "continuity"),
    ("composite_func", "derivative"),
    ("composite_func", "integration"),
    ("integral_area_s", "normal_distribution"),
    ("normal_distribution", "normal_dist_p"),
    ("normal_dist_p", "rv_function"),
    ("random_variable", "rv_concept"),
    ("rv_concept", "distribution_function_p"),
    ("distribution_function_p", "discrete_rv"),
    ("discrete_rv", "continuous_rv"),
    ("continuous_rv", "pdf"),
    ("pdf", "uniform_dist_p"),
    ("pdf", "exponential_dist_p"),
    ("exponential_dist_p", "normal_dist_p"),
    ("normal_dist_p", "standard_normal_p"),
    ("discrete_rv", "bernoulli_dist"),
    ("bernoulli_dist", "binomial_dist_p"),
    ("binomial_dist_p", "poisson_dist"),
    ("rv_function", "convolution"),
    ("random_variable", "random_vector"),
    ("random_vector", "joint_dist"),
    ("joint_dist", "marginal_dist"),
    ("joint_dist", "conditional_dist_p"),
    ("marginal_dist", "rv_independence"),
    ("expectation", "expectation_func"),
    ("variance", "std_deviation"),
    ("variance", "covariance_p"),
    ("covariance_p", "correlation_p"),
    ("correlation_p", "covariance_matrix_p"),
    ("normal_distribution", "chi_square_distribution"),
    ("chi_square_distribution", "t_distribution"),
    ("chi_square_distribution", "f_distribution"),
    ("rv_concept", "point_estimation"),
    ("point_estimation", "hypothesis_testing"),
    ("hypothesis_testing", "type_i_error"),
    ("type_i_error", "p_value"),
    ("p_value", "anova"),
    ("simple_random_sampling", "hypothesis_testing"),
    ("limit", "limit_calc_s"),
    ("continuity", "limit_calc_s"),
    ("derivative", "derivative_def_s"),
    ("derivative_rule_s", "derivative_product_quotient"),
    ("derivative_rule_s", "diff_rules"),
    ("integral_volume_s", "volume_calc"),

    # ===== 跨年级衔接 =====
    # 小学→初中
    ("absolute_value_p6", "absolute_value"),
    ("rational_number_p6", "rational_numbers"),
    ("number_line_negative", "number_line"),
    ("add_negative_numbers", "rational_addition"),
    ("percentage", "percentage"),  # 已有连接
    ("ratio_extend", "ratio_concept_j"),  # 初中比例
    ("scale_p", "scale_drawing"),
    ("cylinder_volume_p6", "cylinder_geo"),
    ("cone_volume", "cone_geo"),
    ("circle_area_derive", "circle_definition"),
    ("annulus_area", "circle_geo"),
    ("theoretical_probability", "probability"),
    ("random_event_j", "probability"),

    # 初中→高中
    ("pythagorean", "pythagorean_theorem"),
    ("quadratic_equation", "quadratic_formula_j"),  # 初中二次方程
    ("linear_function_j", "linear_func"),
    ("function_concept_j", "function"),
    ("direct_proportional_function", "linear_func"),
    ("inverse_proportional_function", "inverse_proportional_function_s"),
    ("triangle_congruence", "congruent"),
    ("congruent", "triangle_centroid"),
    ("similar_triangles", "similar"),
    ("circle_theorems", "circle_j"),
    ("inscribed_angle", "circle_theorems"),
    ("trig_ratio", "trig_functions"),
    ("special_right", "special_angle_30"),
    ("special_right", "special_angle_45"),
    ("special_right", "special_angle_60"),
    ("pythagorean", "special_right"),
    ("special_angle_30", "trig_values_30_45_60_j"),
    ("special_angle_45", "trig_values_30_45_60_j"),
    ("special_angle_60", "trig_values_30_45_60_j"),
    ("degree_system", "radian_system"),
    ("radian_system", "degree_radian_conversion"),
    ("combination", "binomial_theorem"),
    ("combination", "permutation"),
    ("combinatorial_probability", "probability"),
    ("list_method_prob", "permutation"),
    ("list_method_prob", "combination"),
    ("tree_diagram_prob", "combination"),

    # 高中内部
    ("unit_circle", "unit_circle_s"),
    ("radian_system", "unit_circle"),
    ("radian", "radian_system"),
    ("trig_functions", "trig_ratio"),
    ("inverse_trig", "inverse_trig_s"),
    ("trig_identities", "trig_identities_s"),
    ("quadratic_function_j", "quadratic_func_s"),
    ("linear_function_j", "linear_func_s"),
    ("ellipse", "conic"),
    ("hyperbola", "conic"),
    ("parabola", "conic"),
    ("line_eq", "circle_eq"),
    ("space_coordinate", "cartesian_s"),
    ("dot_product", "space_line_plane"),
    ("cylinder_geo", "cylinder_p"),
    ("cone_geo", "cone_p"),
    ("cylinder_p", "cylinder_geo"),
    ("cone_p", "cone_geo"),
    ("normal_distribution", "normal_dist_p"),
    ("binomial_distribution", "binomial_dist_p"),
    ("random_variable", "random_variable_p"),
    ("probability_theory", "probability_def_p"),
    ("limit", "derivative"),
    ("continuity", "derivative"),
    ("derivative", "fundamental_theorem"),
    ("integral_area_s", "volume_calc"),
    ("volume_calc", "integral_volume_s"),
    ("space_plane_equation", "space_line_plane"),
]


def sanitize_id(raw):
    return re.sub(r'[^a-z0-9_]', '', raw.lower().replace(' ', '_'))


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data['nodes']
    existing_ids = {n['id'] for n in nodes}
    existing_names = {n['name']['zh'] for n in nodes}

    # 1. 创建章节节点
    new_chapter_nodes = []
    chapter_node_ids = set()
    grade_tag_map = {
        '小学': ['小学一年级','小学二年级','小学三年级','小学四年级','小学五年级','小学六年级'],
        '初中': ['初中一年级','初中二年级','初中三年级'],
        '高中': ['高中一年级','高中二年级','高中三年级'],
        '大学': ['大学及以上'],
    }

    def get_grade_tag(grade):
        for key, tags in grade_tag_map.items():
            if grade in tags:
                return tags
        return ['大学及以上']

    for ch in CHAPTERS:
        cid = sanitize_id(ch['id'])
        if cid in existing_ids:
            chapter_node_ids.add(cid)
            continue
        grade_tags = get_grade_tag(ch['grade'])
        node = {
            "id": cid,
            "type": "branch",
            "name": {"zh": ch['name'], "en": ch['name']},
            "description": {"zh": f"小学数学章节 — {ch['name']}", "en": ""},
            "level": ch['grade'][:2] + ('primary' if ch['grade'].startswith('小学') else 'junior' if ch['grade'].startswith('初中') else 'senior'),
            "branch": ch['branch'],
            "tags": grade_tags,
            "prerequisites": [],
            "difficulty": 2,
            "importance": 9,
            "estimated_minutes": 120
        }
        new_chapter_nodes.append(node)
        chapter_node_ids.add(cid)

    # 2. 建立节点ID → 章节的映射
    node_to_chapter = {}
    for ch in CHAPTERS:
        cid = sanitize_id(ch['id'])
        for member_id in ch['members']:
            mid = sanitize_id(member_id)
            if mid in existing_ids or mid in chapter_node_ids:
                node_to_chapter[mid] = cid

    # 3. 收集新边（prerequisites）
    # 先修链边
    new_prereq_edges = []
    for (from_id, to_id) in CURRICULUM_PREREQS:
        fid = sanitize_id(from_id)
        tid = sanitize_id(to_id)
        if fid in existing_ids and tid in existing_ids:
            new_prereq_edges.append((fid, tid))

    # 章节星形边：每个成员节点 → 章节节点
    chapter_edges = []
    for node_id, ch_id in node_to_chapter.items():
        if node_id in existing_ids and ch_id in chapter_node_ids:
            chapter_edges.append((node_id, ch_id))

    # 4. 应用到节点
    updated = 0
    new_node_ids = set()

    # 先加章节节点
    for n in new_chapter_nodes:
        data['nodes'].append(n)
        new_node_ids.add(n['id'])
    print(f"✅ 新增 {len(new_chapter_nodes)} 个章节节点")

    # 建立ID→节点的快速查找
    id_to_node = {n['id']: n for n in data['nodes']}

    # 添加先修边
    prereq_added = 0
    for (fid, tid) in new_prereq_edges:
        tn = id_to_node.get(tid)
        if tn and fid not in tn.get('prerequisites', []):
            if 'prerequisites' not in tn:
                tn['prerequisites'] = []
            tn['prerequisites'].append(fid)
            prereq_added += 1

    # 添加章节星形边
    chapter_added = 0
    for (nid, chid) in chapter_edges:
        tn = id_to_node.get(nid)
        if tn and chid not in tn.get('prerequisites', []):
            if 'prerequisites' not in tn:
                tn['prerequisites'] = []
            tn['prerequisites'].append(chid)
            chapter_added += 1

    print(f"✅ 新增 {prereq_added} 条先修边")
    print(f"✅ 新增 {chapter_added} 条章节星形边")

    # 5. 统计验证
    node_ids_final = {n['id'] for n in data['nodes']}
    total_edges = 0
    isolated = 0
    for n in data['nodes']:
        valid_prereqs = [p for p in n.get('prerequisites', []) if p in node_ids_final]
        n['prerequisites'] = valid_prereqs
        total_edges += len(valid_prereqs)
        if not valid_prereqs and not any(n['id'] in p.get('prerequisites', []) for p in data['nodes']):
            isolated += 1

    print(f"\n=== 更新后统计 ===")
    print(f"总节点: {len(data['nodes'])}")
    print(f"总边数: {total_edges}")
    print(f"平均边数: {total_edges/len(data['nodes']):.1f}")
    print(f"孤立节点: {isolated}")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ 数据已保存")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""大学知识点连通脚本 - 大学分支章节 + 先修链构建"""
import json
import re

DATA_FILE = "/Users/jia/.qclaw/workspace/math-knowledge-graph/data/core-nodes.json"

def sid(raw):
    """生成安全的ID"""
    return re.sub(r'[^a-z0-9_]', '', raw.lower().replace(' ', '_'))

def matches(node, kws):
    """判断节点是否匹配关键词列表"""
    zh = (node.get('name', {}).get('zh', '') or '').lower()
    en = (node.get('name', {}).get('en', '') or '').lower()
    nid = (node.get('id', '') or '').lower()
    desc = (node.get('description', {}).get('zh', '') or '').lower()
    txt = ' '.join([zh, en, nid, desc])
    return any(kw.lower() in txt for kw in kws)

# 分支章节定义
BRANCH_CHAPTERS = [
    ["ch_ug_ode", "常微分方程", "pde", ["ode", "differential equation", "initial condition", "boundary condition", "existence uniqueness", "linear ode", "constant coefficient", "homogeneous ode", "variation parameters", "bernoulli equation", "euler equation", "laplace transform ode", "green function ode", "higher order ode", "sturm liouville", "euler lagrange", "riccati", "exact equation", "integrating factor", "liouville theorem ode", "ordinary differential"]],
    ["ch_ug_pde", "偏微分方程", "pde", ["pde", "partial differential", "elliptic", "parabolic", "hyperbolic", "laplace equation", "poisson equation", "harmonic function", "heat equation", "wave equation", "green function pde", "max principle", "hopf lemma", "separation variable", "fourier transform pde", "characteristic", "transport equation", "well posed", "sobolev", "variational method", "ritz", "galerkin", "numerical pde", "nonlinear pde", "cahn hilliard", "navier stokes", "kdv", "burgers", "fokker planck", "lax milgram", "trace theorem", "fundamental solution", "elliptic pde", "parabolic pde", "hyperbolic pde", "mixed bvp", "initial value", "boundary value", "cauchy problem", "ricci flow", "hamilton ricci flow", "mean curvature flow"]],
    ["ch_ug_analysis", "实变复变函数", "analysis", ["real analysis", "measure", "lebesgue", "measurable", "almost everywhere", "lp space", "holder inequality", "convergence theorem", "dominated convergence", "monotone convergence", "fatou lemma", "stieltjes integral", "integral", "riemann stieltjes", "lp completeness", "convolution", "young inequality", "fourier transform", "plancherel", "weierstrass theorem", "complex analysis", "holomorphic", "analytic", "cauchy riemann", "harmonic function analysis", "conformal mapping", "riemann mapping", "schwarz lemma", "picard theorem", "residue", "continued fraction", "normal family", "univalent function", "bloch constant", "multivariate complex", "approximation theory", "best approximation", "bernstein", "weierstrass", "fourier series", "trigonometric series", "orlicz", "banach function space"]],
    ["ch_ug_number_theory", "初等数论", "number_theory", ["number theory", "divisibility", "prime", "composite", "sieve", "gcd", "lcm", "euclidean algorithm", "extended euclidean", "bezout", "congruence", "residue system", "euler phi", "euler totient", "fermat little", "euler theorem", "chinese remainder", "linear congruence", "miller rabin", "pollard rho", "integer factorization", "discrete logarithm", "diffie hellman", "elgamal", "rsa", "digital signature", "hash", "diophantine", "pell equation", "primitive root", "quadratic residue", "legendre symbol", "jacobi symbol", "quadratic reciprocity", "gauss lemma", "hilbert symbol", "class field", "p adic", "algebraic number", "algebraic integer", "dirichlet series", "riemann zeta", "prime number theorem", "fermat last", "goldbach", "twin prime", "perfect number", "moebius", "mertens", "chebotarev", "analytic number theory", "additive number theory", "sieve theory", "brun", "bombieri", "vinogradov", "goldston", "yildirim", "bounds prime gap", "transcendental number", "lindemann", "gel fond", "baker theory", "linear forms", "height function", "ahlgren"]],
    ["ch_ug_algebra", "抽象代数与伽罗瓦", "algebra", ["abstract algebra", "group", "subgroup", "coset", "normal subgroup", "quotient group", "homomorphism", "isomorphism", "kernel", "cyclic group", "permutation", "symmetric group", "alternating", "finite group", "abelian", "free group", "group action", "orbit", "stabilizer", "burnside", "polya enumeration", "sylow", "lagrange theorem", "cauchy theorem", "galois", "galois theory", "galois group", "field extension", "algebraic extension", "normal extension", "separable extension", "galois extension", "solvable group", "insolubility quintic", "noetherian", "hilbert basis", "ideal", "quotient ring", "noetherian ring", "dimension", "field", "splitting field", "primitive element", "torsion", "module", "representation", "character", "schur lemma", "maschke", "tensor product", "exterior algebra", "lie algebra", "lie group", "lie group representation", "adjoint representation", "casimir", "universal enveloping", "poisson algebra", "quantum group", "hopf algebra", "coalgebra", "bialgebra", "grassmann", "clifford algebra", "weyl algebra", "weyl group", "brauer group", "algebraic k theory", "k theory", "atiyah hirzebruch", "bott periodicity", "chern class", "adams operation", "algebraic topology", "kobayashi"]],
    ["ch_ug_dynamics", "动力系统", "dynamics", ["dynamical system", "flow", "vector field", "fixed point", "equilibrium", "attractor", "repeller", "hyperbolic", "stable manifold", "unstable manifold", "center manifold", "bifurcation", "saddle node", "pitchfork", "hopf bifurcation", "poincare map", "limit cycle", "liapunov stability", "liapunov function", "lasalle invariance", "hamiltonian system", "gradient system", "conservative system", "integrable system", "liouville theorem dyn", "poincare recurrence", "ergodic", "birkhoff", "von neumann ergodic", "kolmogorov sinai", "entropy", "topological entropy", "measure entropy", "chaos", "sensitive dependence", "liapunov exponent", "topological mixing", "logistic map", "period doubling", "feigenbaum", "fractal", "hausdorff dimension", "box dimension", "lorenz attractor", "strange attractor", "soliton", "symbolic dynamics", "expanding map", "jordan curve", "horseshoe", "melnikov", "homoclinic", "heteroclinic", "normal hyperbolicity", "invariant manifold", "center bundle", "filtration", "nonuniform hyperbolic", "srb measure", "physical measure", "natural measure", "equilibrium state", "topological pressure", "variational principle", "maximizing measure", "rotational", "twist map", "standard map", "chenciner", "montgomery", "aubry mather", "minimizing orbit", "kam theorem", "resonance", "lock in", "arnold diffusion", "nekhoroshev", "fast dynamo", "turbulence", "fluid dynamics"]],
    ["ch_ug_numerical", "数值分析", "numerical", ["numerical analysis", "scientific computing", "error analysis", "error propagation", "numerical stability", "condition number", "interpolation", "lagrange", "newton interpolation", "hermite", "cubic spline", "spline", "numerical integration", "gaussian quadrature", "monte carlo", "numerical linear algebra", "lu decomposition", "cholesky", "qr decomposition", "svd", "power iteration", "inverse iteration", "rayleigh quotient", "lanczos", "krylov subspace", "cg method", "conjugate gradient", "gmres", "bicgstab", "newton method", "quasi newton", "dfp", "bfgs", "inexact newton", "preconditioner", "algebraic multigrid", "domain decomposition", "finite element", "variational formulation", "sobolev space numerical", "ritz method", "galerkin method", "convergence rate", "optimal convergence", "runge kutta", "adams", "multistep method", "predictor corrector", "adaptive step", "stiff equation", "dae", "spectral method", "fft", "spectral accuracy", "collocation", "finite difference", "finite volume", "wavelet", "compressed sensing", "sparse recovery", "rip", "l1 minimization", "inverse problem", "regularization", "tikhonov", "truncated svd", "iterative regularization", "optimal control", "optimal design", "automatic differentiation", "adjoint method", "algorithmic differentiation", "reverse mode", "forward mode", "fast multipole", "fmm", "treecode", "n body", "particle method", "smoothed particle hydrodynamics", "sph", "spectral element", "discontinuous galerkin", "dg method", "virtual element", "vem", "isogeometric", "nurbs", "mesh generation", "delaunay", "advancing front", "octree", "quadtree", "adaptive mesh", "amr", "refinement", "load balancing", "parallel"]],
    ["ch_ug_probability", "概率论", "probability", ["probability theory", "probability space", "conditional probability", "bayes formula", "bayes", "independent events", "bernoulli trial", "binomial distribution", "geometric distribution", "negative binomial", "hypergeometric", "poisson distribution", "exponential distribution", "uniform distribution", "normal distribution", "gaussian", "lognormal", "gamma distribution", "beta distribution", "cauchy", "weibull", "chi square", "t distribution", "f distribution", "random variable", "discrete rv", "continuous rv", "distribution function", "pdf", "pmf", "moment", "expectation", "variance", "covariance", "correlation", "conditional expectation", "conditional variance", "characteristic function", "convergence rv", "almost sure", "convergence probability", "convergence distribution", "lp convergence", "central limit theorem", "clt", "law large numbers", "slln", "wlln", "borel cantelli", "kolmogorov", "stochastic process", "filtration", "adapted process", "stopping time", "martingale", "brownian motion", "wiener process", "ito integral", "ito lemma", "stochastic differential", "sde", "stochastic differential equation", "fokker planck", "kolmogorov forward", "markov chain", "transition probability", "stationary distribution", "ergodic theorem", "poisson process", "renewal", "queueing", "information theory", "entropy", "mutual information", "kl divergence", "relative entropy", "fisher information", "exponential family", "maximum entropy", "bayesian statistics", "prior posterior", "conjugate prior", "gibbs sampling", "metropolis hastings", "mcmc", "em algorithm", "variational inference", "stochastic control", "financial mathematics", "option pricing", "black scholes", "binomial model", "hull white", "heston", "local volatility", "stochastic volatility", "sabr", "bergomi", "rough volatility", "volterra integral", "rough path", "signature", "controlled differential"]],
    ["ch_ug_statistics", "数理统计", "statistics", ["statistics", "statistical inference", "point estimation", "maximum likelihood", "mle", "method moments", "em algorithm", "unbiased estimation", "cramer rao", "efficiency", "asymptotic", "fisher information", "interval estimation", "confidence interval", "t interval", "chi square interval", "hypothesis testing", "neyman pearson", "ump", "likelihood ratio test", "chi square test", "goodness fit", "independence test", "regression", "linear regression", "ols", "ridge", "lasso", "elastic net", "logistic regression", "generalized linear model", "glm", "survival analysis", "kaplan meier", "cox model", "proportional hazard", "cox regression", "nonparametric", "bootstrap", "permutation test", "wilcoxon", "mann whitney", "kruskal wallis", "friedman", "anova", "variance analysis", "statistical learning", "svm", "support vector", "kernel svm", "random forest", "boosting", "xgboost", "ensemble", "neural network", "deep learning", "cross validation", "overfitting", "generalization", "causal inference", "potential outcome", "propensity score", "matching", "ipw", "marginal structural", "structural causal", "dag", "do calculus", "backdoor", "frontdoor", "instrumental variable", "two stage least squares", "mediation", "heterogeneity", "treatment effect", "meta analysis", "publication bias", "fixed effect", "random effect", "bayesian statistics", "bayesian hypothesis", "bayes factor", "markov chain monte carlo", "gibbs", "metropolis", "convergence diagnosis", "multiple testing", "fdr", "benjamini hochberg", "multiple comparison", "bonferroni", "holm", "multiple comparison procedure", "benjamini yekutieli", "storey", "qvalue", "local fdr", "empirical bayes", "false discovery rate", "type i error", "type ii error", "power analysis", "sample size", "statistical power", "effect size", "cohens d", "odds ratio", "relative risk", "risk ratio", "hazard ratio", "attributable risk", "number needed to treat", "nnt", "sensitivity specificity", "ppv", "npv", "roc curve", "auc", "precision recall", "f1 score", "confusion matrix"]],
    ["ch_ug_topology", "拓扑学", "topology", ["topology", "topological space", "open set", "closed set", "neighborhood", "hausdorff", "compactness", "connectedness", "path connected", "locally connected", "separation axioms", "metrizable", "complete metric", "banach fixed point", "brouwer fixed point", "schauder", "tychonoff", "fundamental group", "covering space", "deck transformation", "homotopy", "homotopy group", "homotopy equivalence", "homology", "cohomology", "cup product", "poincare duality", "kuenneth", "spectral sequence", "cell complex", "simplicial complex", "cw complex", "nerve lemma", "triangulation", "manifold", "smooth manifold", "riemannian", "orientation", "transversality", "sard theorem", "whitney embedding", "morse theory", "morse function", "critical point", "handlebody", "surgery", "bordism", "characteristic class", "stiefel whitney", "pontryagin", "chern", "euler class", "index theorem", "atiyah singer", "elliptic operator", "dirac operator", "low dimension topology", "three manifold", "poincare conjecture", "geometrization", "hyperbolic manifold", "knot theory", "knot", "braid group", "link", "linking number", "alexander polynomial", "jones polynomial", "khovanov", "fundamental group topology", "presentations", "dehn surgery", "heegaard", "virtual haken", "l2 invariant", "topological quantum", "tqft", "chern simons", "topological order", "topological phase", "topological insulator", "mapper", "vietoris rips", "persistent homology", "topological data analysis", "tda", "barcode", "persistence diagram", "mapper algorithm", "zipper", "reeb graph", "quasiconformal mapping", "conformal dynamics", "holomorphic dynamics", "julia set", "mandelbrot set", "sullivan measure", "bergman kernel", "geometric function theory", "ahlfors", "ahlfors five island", "ahlfors beurling"]],
    ["ch_ug_discrete", "组合学与离散数学", "discrete", ["combinatorics", "discrete mathematics", "counting", "permutation", "combination", "binomial theorem", "pascal triangle", "multinomial theorem", "inclusion exclusion", "pigeonhole principle", "ramsey theory", "ramsey number", "extremal combinatorics", "turan theorem", "vandermonde", "ballot problem", "catalan number", "dyck path", "noncrossing", "matching", "set partition", "stirling number", "bell number", "group action combinatorics", "burnside lemma", "polya enumeration", "cycle index", "pattern inventory", "graph theory", "graph", "vertex", "edge", "degree", "path", "cycle", "tree", "spanning tree", "eulerian", "hamiltonian", "matching", "coloring", "planar graph", "four color", "graph isomorphism", "network flow", "max flow min cut", "ford fulkerson", "edmonds karp", "dinic", "bipartite matching", "hungarian", "kuhn munkres", "hall marriage", "tutte theorem", "kruskal", "prim", "dijkstra", "bellman ford", "floyd warshall", "shortest path", "steiner tree", "tsp", "traveling salesman", "graph minor", "robertson seymour", "treewidth", "branchwidth", "boolean formula", "cnf", "dnf", "satisfiability", "sat", "np complete", "np", "p np", "circuit complexity", "proof complexity", "probabilistically checkable", "pcp", "interactive proof", "ip pspace", "randomized computation", "bpp", "rp", "zpp", "approximation algorithm", "ptas", "apx", "inapproximability", "pcp theorem", "combinatorial optimization", "integer programming", "branch and bound", "cutting plane", "gomory cut", "linear programming", "duality", "simplex", "ellipsoid", "khachiyan", "combinatorial game", "sprague grundy", "impartial game", "partizan game", "poset", "lattice", "boolean algebra", "de morgan", "filter", "ultrafilter", "ideal ring", "mobius function", "mobius inversion", "combinatorial design", "bibd", "steiner system", "orthogonal array", "finite projective plane", "convex hull", "voronoi diagram", "delaunay triangulation", "computational geometry", "random graph", "erdos renyi", "threshold function", "phase transition", "probabilistic method", "expectation method", "lovasz local lemma", "second moment method", "jansen inequalities", "random walk", "markov chain mixing", "coupling", "spectral gap", "cheeger inequality", "expander graph", "randomized rounding", "derandomization", "probabilistic analysis", "competitive ratio", "online algorithm"]],
    ["ch_ug_physics", "数学物理", "physics", ["mathematical physics", "general relativity", "spacetime", "metric", "lorentz", "riemann curvature", "ricci curvature", "scalar curvature", "einstein field", "schwarzschild", "black hole", "hawking radiation", "penrose", "singularity theorem", "causal structure", "light cone", "gravitational lens", "perihelion", "bondi", "adm formalism", "yang mills", "gauge theory", "gauge field", "connection curvature form", "chern class", "chern simons", "instanton", "path integral quantization", "quantization", "brst quantization", "ghosts", "brst", "anomalies", "abelian anomaly", "nonabelian anomaly", "witten", "witten turaev", "res hetikhin", "turaev viro", "modular tensor", "topological quantum field", "topological quantum computation", "braiding", "anyons", "statistical mechanics", "ising model", "potts model", "ising", "onsager solution", "partition function", "free energy", "thermodynamic limit", "critical phenomenon", "phase transition", "critical exponent", "scaling law", "landau theory", "ginzburg criterion", "mean field", "spontaneous symmetry", "mermin wagner", "kosterlitz thouless", "yang yang", "kosterlitz", "kt transition", "ads cft", "maldacena", "conformal field", "virasoro algebra", "kac moody", "central charge", "conformal block", "operator product", "bootstrap", "conformal bootstrap", "numerical bootstrap", "energy condition", "cosmic censorship", "chronology protection", "novikov", "closed timelike", "wormhole", "er epr", "quantum gravity", "loop quantum gravity", "lqg", "causal dynamical triangulations", "causal set", "spin foam", "twistor", "string theory", "string", "m theory", "brane", "d brane", "ads", "cft", "holography", "bulk boundary", "boundary cft", "ads soliton", "renormalization flow", "rg flow", "beta function", "asymptotic safety", "quantum anomaly", "wess zumino", "consistent anomaly", "green schwarz", "renormalization group"]],
    ["ch_ug_spherical", "球面三角与非欧几何", "trigonometry", ["spherical", "spherical trigonometry", "spherical cosine", "spherical sine", "napoleon theorem", "spherical geometry", "non euclidean", "hyperbolic geometry", "hyperbolic plane", "poincare disk", "poincare half plane", "beltrami", "lobachevsky", "riemann hyperbolic", "hyperbolic metric", "geodesic", "geodesic distance", "hyperbolic area", "hyperbolic circle", "hyperbolic triangle", "angle parallelism", "saccheri", "gauss bonnet", "curvature", "total curvature", "gauss map", "gauss codazzi", "gauss bonnet chern", "principal curvature", "gaussian curvature", "mean curvature", "sectional curvature", "sectional", "cartan", "moving frame", "connection form", "parallel transport", "geodesic deviation", "jacobi field", "jacobi equation", "conjugate point", "monodromy", "developable surface", "ruled surface", "minimal surface", "mean curvature flow", "willmore surface", "calabi yau", "calabi conjecture", "ricci flow", "thurston geometrization", "poincare", "perelman solution", "three sphere", "sphere theorem", "connected sum", "prime decomposition", "elliptic", "flat", "solv", "nil", "product geometry", "model geometry", "geometric structure", "conformal", "riemann mapping theorem", "quasiconformal", "quasisymmetric", "dendrite", "topological tree"]],
]

# 先修链定义
PREREQS = [
    # ODE -> PDE
    ("limit", "ode_definition"), ("continuity", "ode_definition"), ("derivative", "ode_definition"),
    ("fundamental_theorem", "ode_existence"),
    ("ode_definition", "ode_uniqueness"), ("ode_uniqueness", "ode_linear"),
    ("ode_linear", "constant_coefficient"), ("constant_coefficient", "ode_homogeneous"),
    ("ode_homogeneous", "ode_particular"), ("ode_particular", "variation_parameters"),
    ("ode_definition", "exact_equation"), ("exact_equation", "integrating_factor"),
    ("integrating_factor", "bernoulli_eq"),
    ("variation_parameters", "euler_lagrange"),
    ("ode_definition", "first_order_pde"), ("first_order_pde", "transport_equation"),
    ("transport_equation", "characteristic_method"),
    ("derivative", "pde_definition"), ("pde_definition", "order_pde"),
    ("order_pde", "solution_pde"), ("solution_pde", "explicit_solution"),
    ("pde_definition", "elliptic_pde"), ("elliptic_pde", "laplace_equation"),
    ("laplace_equation", "harmonic_function"), ("harmonic_function", "poisson_equation"),
    ("laplace_equation", "green_function_pde"),
    ("laplace_equation", "dirichlet_condition"), ("laplace_equation", "neumann_condition"),
    ("dirichlet_condition", "boundary_condition"),
    ("laplace_equation", "max_value_principle"), ("max_value_principle", "hopf_lemma"),
    ("pde_definition", "parabolic_pde"), ("parabolic_pde", "heat_equation"),
    ("heat_equation", "fundamental_solution_pde"),
    ("separation_of_variables", "fourier_series"),
    ("pde_definition", "hyperbolic_pde"), ("hyperbolic_pde", "wave_equation"),
    ("wave_equation", "string_vibration"), ("wave_equation", "huygens_principle"),
    ("pde_definition", "sobolev_space"), ("sobolev_space", "sobolev_embedding"),
    ("sobolev_embedding", "lax_milgram"),
    ("lax_milgram", "variational_method"), ("variational_method", "galerkin_method"),

    # 数论
    ("gcd", "bezout_lemma"), ("prime_number", "sieve_eratosthenes"),
    ("sieve_eratosthenes", "prime_infinite"),
    ("gcd", "euler_function_extended"),
    ("euler_function_extended", "fermat_little"),
    ("fermat_little", "wilson_theorem"),
    ("bezout_lemma", "linear_congruence"), ("linear_congruence", "chinese_remainder"),
    ("prime_number", "quadratic_residue"), ("quadratic_residue", "legendre_symbol"),
    ("legendre_symbol", "quadratic_reciprocity"),
    ("quadratic_reciprocity", "jacobi_symbol"),
    ("integer_factorization", "pollard_rho"),
    ("pollard_rho", "pollard_p_1"),
    ("primitive_root", "discrete_logarithm"),
    ("discrete_logarithm", "diffie_hellman"),
    ("diffie_hellman", "elgamal"),
    ("fermat_little", "rsa"),

    # 代数
    ("group_theory", "subgroup"),
    ("subgroup", "coset"), ("subgroup", "normal_subgroup"),
    ("coset", "quotient_group"), ("subgroup", "homomorphism"),
    ("homomorphism", "isomorphism"), ("homomorphism", "kernel"),
    ("isomorphism", "lagrange_theorem"), ("lagrange_theorem", "cauchy_theorem"),
    ("cauchy_theorem", "sylow_theorems"), ("sylow_theorems", "simple_group"),
    ("subgroup", "cyclic_group"), ("cyclic_group", "permutation_group"),
    ("group_action", "orbit_stabilizer"), ("orbit_stabilizer", "polya_enumeration"),
    ("group", "abelian_group"),
    ("vector_space", "tensor_product"), ("tensor_product", "exterior_algebra"),
    ("vector_space", "representation_theory"), ("representation_theory", "group_representation"),
    ("group_representation", "character_theory"), ("character_theory", "schur_lemma"),
    ("ring_theory", "ideal"), ("ideal", "quotient_ring"),
    ("field_theory", "field_extension"), ("field_extension", "algebraic_extension"),
    ("algebraic_extension", "normal_extension"), ("normal_extension", "separable_extension"),
    ("separable_extension", "galois_extension"), ("galois_extension", "galois_group"),
    ("galois_group", "galois_correspondence"),
    ("galois_correspondence", "fundamental_theorem_galois"),
    ("fundamental_theorem_galois", "insolubility_of_quintic"),

    # 动力系统
    ("derivative", "vector_field"), ("vector_field", "flow_dynamical"),
    ("vector_field", "fixed_point_dyn"), ("fixed_point_dyn", "stable_fixed_point"),
    ("stable_fixed_point", "lyapunov_stability"), ("lyapunov_stability", "lyapunov_function"),
    ("lyapunov_function", "lasalle_invariance"),
    ("fixed_point_dyn", "hyperbolic_fixed_point"),
    ("hyperbolic_fixed_point", "stable_manifold_dyn"),
    ("bifurcation", "saddle_node"), ("saddle_node", "pitchfork"),
    ("pitchfork", "hopf_bifurcation"),
    ("limit_cycle", "poincare_map"),
    ("hamiltonian_system", "integrable_system"),
    ("ergodic_theory", "birkhoff_ergodic"),
    ("birkhoff_ergodic", "poincare_recurrence"),
    ("chaos", "lyapunov_exponent"), ("chaos", "sensitive_dependence"),
    ("logistic_map", "period_doubling"), ("period_doubling", "feigenbaum_constant"),

    # 数值分析
    ("numerical_linear_algebra_new", "gaussian_elimination"),
    ("gaussian_elimination", "lu_decomposition"),
    ("lu_decomposition", "cholesky_decomposition"),
    ("lu_decomposition", "qr_decomposition"),
    ("qr_decomposition", "svd"),
    ("svd", "condition_number"),
    ("power_iteration", "rayleigh_quotient"),
    ("rayleigh_quotient", "lanczos_method"),
    ("lanczos_method", "krylov_subspace"),
    ("krylov_subspace", "cg_method"), ("cg_method", "gmres_method"),
    ("newton_method", "quasi_newton"), ("quasi_newton", "dfp"), ("quasi_newton", "bfgs"),
    ("conjugate_gradient", "preconditioner"),
    ("finite_element_method_new", "variational_formulation"),
    ("variational_formulation", "lax_milgram"),
    ("fft", "spectral_method"),
    ("compressed_sensing", "sparse_recovery"),

    # 概率
    ("probability", "random_variable"),
    ("random_variable", "discrete_rv"),
    ("random_variable", "continuous_rv"),
    ("discrete_rv", "bernoulli_dist"),
    ("bernoulli_dist", "binomial_dist"),
    ("binomial_dist", "poisson_dist"), ("poisson_dist", "poisson_process"),
    ("continuous_rv", "uniform_dist"), ("uniform_dist", "exponential_dist"),
    ("exponential_dist", "normal_distribution"),
    ("normal_distribution", "chi_square_distribution"),
    ("normal_distribution", "t_distribution"),
    ("normal_distribution", "f_distribution"),
    ("moment", "expectation"), ("moment", "variance"),
    ("variance", "covariance"), ("covariance", "correlation"),
    ("conditional_probability", "bayes_formula"),
    ("bayes_formula", "prior_posterior"),
    ("prior_posterior", "bayesian_statistics"),
    ("central_limit_theorem", "law_of_large_numbers"),
    ("probability", "stochastic_process"),
    ("stochastic_process", "brownian_motion"),
    ("brownian_motion", "ito_integral"), ("ito_integral", "ito_lemma"),
    ("ito_lemma", "stochastic_differential_equation"),
    ("brownian_motion", "martingale"), ("martingale", "stopping_time"),
    ("stochastic_process", "markov_chain"),
    ("markov_chain", "transition_probability"),
    ("transition_probability", "stationary_distribution"),

    # 统计
    ("probability", "point_estimation"), ("point_estimation", "maximum_likelihood"),
    ("maximum_likelihood", "mle_asymptotic"),
    ("point_estimation", "bayesian_estimation"),
    ("bayesian_estimation", "credible_interval"),
    ("point_estimation", "interval_estimation"),
    ("interval_estimation", "confidence_interval"),
    ("hypothesis_testing", "neyman_pearson"),
    ("hypothesis_testing", "likelihood_ratio_test"),
    ("chi_square_test", "goodness_of_fit"),
    ("regression_analysis", "linear_regression_stat"),
    ("linear_regression_stat", "ols"),
    ("ols", "ridge_regression"), ("ridge_regression", "lasso"),
    ("linear_regression_stat", "logistic_regression"),
    ("logistic_regression", "generalized_linear_model"),
    ("regression_analysis", "nonparametric_regression"),
    ("statistical_learning", "svm"), ("svm", "kernel_svm"),
    ("statistical_learning", "ensemble_methods"),
    ("ensemble_methods", "boosting"), ("boosting", "xgboost"),
    ("neural_network", "deep_learning"),

    # 拓扑
    ("set_theory", "metric_space"), ("metric_space", "topology_space"),
    ("topology_space", "hausdorff_space"),
    ("topology_space", "compactness"), ("compactness", "heine_borel"),
    ("topology_space", "connectedness"),
    ("connectedness", "path_connectedness"),
    ("fundamental_group", "covering_space"),
    ("covering_space", "homotopy_lifting"),
    ("homotopy", "homotopy_group"), ("homotopy_group", "fundamental_group"),
    ("homotopy", "homology"), ("homology", "simplicial_homology"),

    # 离散
    ("addition_counting", "multiplication_counting"),
    ("multiplication_counting", "permutation"),
    ("permutation", "combination"),
    ("combination", "binomial_theorem"),
    ("binomial_theorem", "inclusion_exclusion"),
    ("graph_theory", "tree"),
    ("tree", "spanning_tree"),
    ("graph_theory", "network_flow"),
    ("network_flow", "max_flow_min_cut"),
    ("network_flow", "matching"),
    ("matching", "bipartite_matching"),
    ("matching", "hall_marriage"),
    ("graph_coloring", "chromatic_polynomial"),
    ("graph_theory", "eulerian_graph"),
    ("eulerian_graph", "hamiltonian_graph"),
]


def main():
    print("=" * 50)
    print("  大学知识点连通脚本")
    print("=" * 50)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data['nodes']
    existing_ids = {n['id'] for n in nodes}
    id_to_node = {n['id']: n for n in nodes}

    def stats():
        nids = existing_ids
        total = sum(len([p for p in n.get('prerequisites', []) if p in nids]) for n in nodes)
        iso = sum(1 for n in nodes
                  if not [p for p in n.get('prerequisites', []) if p in nids]
                  and not any(n['id'] in p.get('prerequisites', []) for p in nodes))
        return len(nodes), total, total / len(nodes) if nodes else 0, iso

    nc, ec, av, ic = stats()
    print(f"\n现状: 节点{nc} 边{ec} 均{av:.1f} 孤立{ic}")

    # 步骤1: 创建分支章节节点
    print("\n📦 步骤1: 创建分支章节节点")
    new_ch = 0
    for row in BRANCH_CHAPTERS:
        cid, name, branch, kws = row
        if cid in existing_ids:
            continue
        node = {
            "id": cid, "type": "chapter",
            "name": {"zh": name, "en": name},
            "description": {"zh": f"大学数学 — {name}", "en": ""},
            "level": "undergrad", "branch": branch,
            "tags": ["大学及以上"],
            "prerequisites": [],
            "difficulty": 3, "importance": 9, "estimated_minutes": 180
        }
        nodes.append(node)
        existing_ids.add(cid)
        id_to_node[cid] = node
        new_ch += 1
    print(f"   ✅ 新增 {new_ch} 个章节节点")

    # 步骤2: 关键词匹配星形边
    print("\n⭐ 步骤2: 构建归属星形边")
    id_to_node = {n['id']: n for n in nodes}
    assigned = 0
    for n in nodes:
        if n['id'].startswith('ch_') or '大学及以上' not in (n.get('tags') or []):
            continue
        best_count = 0
        best_cid = None
        for row in BRANCH_CHAPTERS:
            cid, name, branch, kws = row
            if cid not in existing_ids:
                continue
            cnt = sum(1 for kw in kws if matches(n, [kw]))
            if cnt > best_count:
                best_count = cnt
                best_cid = cid
        if best_cid and best_cid not in n.get('prerequisites', []):
            n.setdefault('prerequisites', []).append(best_cid)
            assigned += 1
    print(f"   ✅ 归属星形边: {assigned} 条")

    # 步骤3: 先修链
    print("\n🔗 步骤3: 构建先修链")
    id_to_node = {n['id']: n for n in nodes}
    pa = 0
    for (fid, tid) in PREREQS:
        f, t = sid(fid), sid(tid)
        if f not in existing_ids or t not in existing_ids:
            continue
        tn = id_to_node.get(t)
        if tn and f not in tn.get('prerequisites', []):
            tn.setdefault('prerequisites', []).append(f)
            pa += 1
    print(f"   ✅ 新增先修边: {pa} 条")

    # 步骤4: 自动修复孤立节点
    print("\n🔧 步骤4: 自动修复孤立节点")
    id_to_node = {n['id']: n for n in nodes}
    existing_ids = {n['id'] for n in nodes}
    branch_ch = {row[2]: row[0] for row in BRANCH_CHAPTERS if row[0] in existing_ids}

    iso_nodes = [n for n in nodes
                 if not n['id'].startswith('ch_')
                 and not [p for p in n.get('prerequisites', []) if p in existing_ids]
                 and not any(n['id'] in p.get('prerequisites', []) for p in nodes)]

    fixed = 0
    for n in iso_nodes:
        branch = n.get('branch', '')
        # 同分支有先修知识的候选
        cands = [n2 for n2 in nodes if n2['id'] != n['id']
                 and not n2['id'].startswith('ch_')
                 and n2.get('branch') == branch
                 and '大学及以上' in (n2.get('tags') or [])
                 and [p for p in n2.get('prerequisites', []) if p in existing_ids]]
        if cands:
            best = max(cands, key=lambda x: len([p for p in x.get('prerequisites', []) if p in existing_ids]))
            if best['id'] not in n.get('prerequisites', []):
                n.setdefault('prerequisites', []).append(best['id'])
                fixed += 1
                continue
        # 连分支章节
        cid = branch_ch.get(branch)
        if cid and cid in existing_ids and cid not in n.get('prerequisites', []):
            n.setdefault('prerequisites', []).append(cid)
            fixed += 1
    print(f"   ✅ 自动修复: {fixed} 个孤立节点")

    # 步骤5: 清理无效边
    print("\n🧹 步骤5: 清理无效边")
    existing_ids = {n['id'] for n in nodes}
    cleaned = 0
    for n in nodes:
        old = len(n.get('prerequisites', []))
        valid = [p for p in n.get('prerequisites', []) if p in existing_ids]
        if len(valid) < old:
            cleaned += old - len(valid)
            n['prerequisites'] = valid
    print(f"   ✅ 清理: {cleaned} 条")

    # 最终统计
    nc2, ec2, av2, ic2 = stats()
    existing_ids = {n['id'] for n in nodes}
    k12 = sum(1 for n in nodes
              if not n['id'].startswith('ch_')
              and '大学及以上' not in (n.get('tags') or [])
              and not [p for p in n.get('prerequisites', []) if p in existing_ids]
              and not any(n['id'] in p.get('prerequisites', []) for p in nodes))

    print(f"\n📈 更新后: 节点{nc2}(+{nc2 - nc}) 边{ec2}(+{ec2 - ec}) 均{av2:.1f} K12孤立{k12} 大学孤立{ic2}")
    if ic2 == 0 and k12 == 0:
        print("🎉 全部知识点已连通！无孤立节点！")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ 数据已保存")


if __name__ == '__main__':
    main()

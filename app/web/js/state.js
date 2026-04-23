const API='http://localhost:8088',USER_ID='student_001';

// ===== 认证相关 =====
const AUTH = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    
    isAuthenticated() {
        if (!this.token) return false;
        try {
            const payload = JSON.parse(atob(this.token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch {
            return false;
        }
    },
    
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        this.token = null;
        this.user = null;
        window.location.href = '/login.html';
    },
    
    getAuthHeaders() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }
};

// 全局辅助函数
function getPrereqIds(p){return(p||[]).map(x=>typeof x==='object'?x.nodeId:x);}
const GRADE_LEVELS=[
    {id:'all',name:'全部',color:'#6366f1'},
    {id:'小学一年级',name:'小学一年级',color:'#10b981'},{id:'小学二年级',name:'小学二年级',color:'#059669'},
    {id:'小学三年级',name:'小学三年级',color:'#0891b2'},{id:'小学四年级',name:'小学四年级',color:'#0284c7'},
    {id:'小学五年级',name:'小学五年级',color:'#7c3aed'},{id:'小学六年级',name:'小学六年级',color:'#db2777'},
    {id:'初中一年级',name:'初中一年级',color:'#d97706'},{id:'初中二年级',name:'初中二年级',color:'#ea580c'},
    {id:'初中三年级',name:'初中三年级',color:'#dc2626'},{id:'高中一年级',name:'高中一年级',color:'#2563eb'},
    {id:'高中二年级',name:'高中二年级',color:'#1d4ed8'},{id:'高中三年级',name:'高中三年级',color:'#1e40af'},
    {id:'大学及以上',name:'大学及以上',color:'#374151'},
];
const BRANCH_NAMES={arithmetic:'算术',algebra:'代数',geometry:'几何',analysis:'分析',probability:'概率',statistics:'统计',discrete:'离散数学',number_theory:'数论',logic:'逻辑',topology:'拓扑',applied:'应用数学',other:'其他',trigonometry:'三角学',dynamics:'动力系统',numerical:'数值分析',optimization:'优化',pde:'微分方程',physics:'数学物理',
// 中文分支
'小学数学':'小学数学','高等数学':'高等数学','拓扑学':'拓扑学','图论':'图论','博弈论':'博弈论','范畴论':'范畴论','随机过程':'随机过程','算术':'算术','控制论':'控制论','线性代数':'线性代数','复分析':'复分析','概率论':'概率论','统计学':'统计学','组合数学':'组合数学','离散数学':'离散数学','逻辑学':'逻辑学','优化理论':'优化理论','动力系统':'动力系统','数值分析':'数值分析','偏微分方程':'偏微分方程','集合论':'集合论','三角学':'三角学','数论':'数论','泛函分析':'泛函分析','微分几何':'微分几何','抽象代数':'抽象代数',
// 详细分支
'抽象代数(详细)':'抽象代数(详细)','微分几何(详细)':'微分几何(详细)','复分析(详细)':'复分析(详细)',
// 英文分支
'functional_analysis':'泛函分析','differential_geometry':'微分几何','abstract_algebra':'抽象代数','category_theory':'范畴论','stochastic_processes':'随机过程','graph_theory':'图论','game_theory':'博弈论','control_theory':'控制论'};
const TYPE_BADGE={concept:'tb-concept',theorem:'tb-theorem',formula:'tb-formula',method:'tb-method',law:'tb-law',conjecture:'tb-conjecture'};
const GRADE_COLOR={};GRADE_LEVELS.forEach(g=>GRADE_COLOR[g.id]=g.color);
const ERROR_TYPES={
    "concept_error":"概念理解错误",
    "calculation_error":"计算错误",
    "formula_error":"公式记错",
    "misunderstanding":"审题错误",
    "careless":"粗心大意",
    "wrong_approach":"思路错误",
    "confusion":"知识点混淆",
    "other":"其他"
};

let allNodes=[],filteredNodes=[],userKnowledge={},currentPage='graph',selectedGrade='all',selectedBranch='';
let currentSimulation=null;
let quizQuestions=[],quizIndex=0,quizAnswers={},quizLevel='',quizBranch='';
let quizReviewed=new Set(); // 本轮已同步的节点ID（避免userKnowledge残留干扰）
let graphMode='all';
let graphFocusNodeId=null; // 图谱聚焦节点ID
let inLinks=new Map(); // 全局入边映射，用于renderList

// ============================================================

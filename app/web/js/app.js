async function init(){
    await Promise.all([loadNodes(),loadUserKnowledge(),loadBranches()]);
    // 初始化全局inLinks映射
    initInLinks();
    renderGradeFilter();renderBranchFilter();updateStats();showPage('graph');
}

// 初始化全局入边映射
function initInLinks(){
    inLinks=new Map();
    const nodeIds=new Set(allNodes.map(n=>n.id));
    allNodes.forEach(n=>{
        if(n.prerequisites){
            for(const p of n.prerequisites){
                const pid=typeof p==='object'?p.nodeId:p;
                if(nodeIds.has(pid)){
                    inLinks.set(n.id,(inLinks.get(n.id)||[]).concat([pid]));
                }
            }
        }
    });
}

async function loadNodes(){
    try{
        const r=await fetch(`${API}/nodes?limit=50000`);
        const d=await r.json();
        allNodes=d.nodes||[];applyFilters();
    }catch(e){allNodes=[]}
}

async function loadUserKnowledge(){
    try{
        const r=await fetch(`${API}/users/${USER_ID}/profile`);
        const p=await r.json();
        const kn=p.known_nodes||[];
        userKnowledge={};
        kn.forEach(n=>{const id=typeof n==='string'?n:(n.node_id||n.id);userKnowledge[id]={status:'known'}});
    }catch(e){userKnowledge={}}
}

function renderBranchFilter(){
    const el=document.getElementById('branchFilter');
    if(!el)return;
    const brs={};
    allNodes.forEach(n=>{const b=n.branch||'other';brs[b]=(brs[b]||0)+1});
    el.innerHTML=Object.entries(brs).sort((a,b)=>b[1]-a[1]).map(([k,c])=>`<span class="branch-tag${selectedBranch===k?' active':''}" onclick="toggleBranch('${k}')">${BRANCH_NAMES[k]||k}(${c})</span>`).join('');
    document.getElementById('totalBranches').textContent=Object.keys(brs).length;
}

async function loadBranches(){
    const brs={};
    allNodes.forEach(n=>{const b=n.branch||'other';brs[b]=(brs[b]||0)+1});
    const el=document.getElementById('branchFilter');
    el.innerHTML=Object.entries(brs).sort((a,b)=>b[1]-a[1]).map(([k,c])=>`<span class="branch-tag${selectedBranch===k?' active':''}" onclick="toggleBranch('${k}')">${BRANCH_NAMES[k]||k}(${c})</span>`).join('');
    document.getElementById('totalBranches').textContent=Object.keys(brs).length;
}

function applyFilters(){
    filteredNodes=allNodes.filter(n=>{
        if(selectedGrade!=='all'){if(!n.tags||!n.tags.includes(selectedGrade))return false}
        if(selectedBranch&&n.branch!==selectedBranch)return false;
        return true;
    });
    document.getElementById('totalNodes').textContent=allNodes.length;
}

function renderGradeFilter(){
    const el=document.getElementById('gradeFilter');
    const counts={all:allNodes.length};
    allNodes.forEach(n=>{if(n.tags)for(const t of n.tags){counts[t]=(counts[t]||0)+1}});
    el.innerHTML=GRADE_LEVELS.map(g=>`<button class="grade-btn${selectedGrade===g.id?' active':''}" onclick="selectGrade('${g.id}')">
        <span class="grade-dot" style="background:${g.color}"></span>
        <span class="grade-name">${g.name}</span>
        <span class="grade-count">${g.id==='all'?allNodes.length:(counts[g.id]||0)}</span>
    </button>`).join('');
}

function selectGrade(id){selectedGrade=id;applyFilters();renderGradeFilter();if(currentPage==='graph')renderGraph();else if(currentPage==='list')renderList();}

function toggleBranch(b){selectedBranch=selectedBranch===b?'':b;applyFilters();loadBranches();if(currentPage==='graph')renderGraph();else if(currentPage==='list')renderList();}

function updateStats(){
    document.getElementById('totalNodes').textContent=allNodes.length;
}

// ============================================================
function showPage(page){
    currentPage=page;
    document.querySelectorAll('.nav-btn').forEach(b=>b.classList.toggle('active',b.dataset.page===page));
    switch(page){
        case'graph':renderGraphPage();break;
        case'list':renderListPage();break;
        case'conjectures':renderConjecturesPage();break;
        case'mathematicians':renderMathematiciansPage();break;
        case'quiz':renderQuizPage();break;
        case'wrong-questions':renderWrongQuestionsPage();break;
        case'stats':renderStatsPage();break;
    }
    closeDetail();
}

function showToast(msg){
    const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'),2000);
}

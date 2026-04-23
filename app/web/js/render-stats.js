async function renderStatsPage(){
    document.getElementById('mainContent').innerHTML=`<div class="stats-page">
        <div class="stats-hero" id="statsHero"></div>
        <div class="stats-grid">
            <div class="stats-card"><div class="stats-card-title">📈 年级掌握情况</div><div id="levelStats"></div></div>
            <div class="stats-card"><div class="stats-card-title">🔬 分支掌握情况</div><div id="branchStats"></div></div>
        </div>
    </div>`;
    // 计算统计
    const levelStats={},branchStats={};
    GRADE_LEVELS.filter(g=>g.id!=='all').forEach(g=>levelStats[g.id]={total:0,known:0});
    Object.values(BRANCH_NAMES).forEach(b=>branchStats[b]={total:0,known:0});
    allNodes.forEach(n=>{
        const grade=n.tags&&n.tags.find(t=>GRADE_COLOR[t]);
        if(grade&&levelStats[grade]){levelStats[grade].total++;if(userKnowledge[n.id]?.status==='known')levelStats[grade].known++}
        const br=BRANCH_NAMES[n.branch]||n.branch;
        if(branchStats[br]){branchStats[br].total++;if(userKnowledge[n.id]?.status==='known')branchStats[br].known++}
    });
    const totalKnown=Object.values(levelStats).reduce((s,v)=>s+v.known,0);
    const total=allNodes.length;
    const pct=total>0?Math.round(totalKnown/total*100):0;
    document.getElementById('statsHero').innerHTML=`
        <div class="hero-stat"><div class="hero-stat-value">${allNodes.length}</div><div class="hero-stat-label">总知识点</div></div>
        <div class="hero-stat"><div class="hero-stat-value">${totalKnown}</div><div class="hero-stat-label">已掌握</div></div>
        <div class="hero-stat"><div class="hero-stat-value">${total-totalKnown}</div><div class="hero-stat-label">待学习</div></div>
        <div class="hero-stat"><div class="hero-stat-value">${pct}%</div><div class="hero-stat-label">掌握率</div></div>`;
    document.getElementById('levelStats').innerHTML=GRADE_LEVELS.filter(g=>g.id!=='all'&&levelStats[g.id]?.total>0).map(g=>{
        const s=levelStats[g.id],p=s.total>0?Math.round(s.known/s.total*100):0;
        return`<div class="level-bar-item">
            <div class="level-bar-header"><span class="level-bar-name">${g.name}</span><span class="level-bar-count">${s.known}/${s.total}</span></div>
            <div class="level-bar-track"><div class="level-bar-fill" style="width:${p}%;background:${g.color}"></div></div>
        </div>`;
    }).join('');
    document.getElementById('branchStats').innerHTML=Object.entries(branchStats).filter(([,v])=>v.total>0).sort((a,b)=>b[1].total-a[1].total).slice(0,10).map(([k,v])=>{
        const p=v.total>0?Math.round(v.known/v.total*100):0;
        const colors=['#6366f1','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#84cc16','#ec4899','#14b8a6','#f97316'];
        return`<div class="level-bar-item">
            <div class="level-bar-header"><span class="level-bar-name">${k}</span><span class="level-bar-count">${v.known}/${v.total}</span></div>
            <div class="level-bar-track"><div class="level-bar-fill" style="width:${p}%;background:${colors[Object.keys(branchStats).indexOf(k)%colors.length]}"></div></div>
            <div class="level-bar-footer">
                <span style="font-size:.78em;color:var(--text-secondary)">▶ 查看详情</span>
            </div>
        </div>`;
    }).join('');
}

function renderPagination(totalPages, total, start, end){
    const infoEl = document.getElementById('paginationInfo');
    const btnsEl = document.getElementById('paginationBtns');
    
    if(totalPages <= 1){
        infoEl.innerHTML = `显示 ${start+1}-${end} / 共 ${total} 条`;
        btnsEl.innerHTML = '';
        return;
    }
    
    infoEl.innerHTML = `显示 ${start+1}-${end} / 共 ${total} 条`;
    
    // 分页按钮
    let btns = '';
    
    // 上一页
    if(listPage > 1){
        btns += `<button onclick="goPage(${listPage-1})" style="padding:4px 10px;border:1px solid var(--border);background:var(--surface);border-radius:6px;cursor:pointer">◀ 上一页</button>`;
    }
    
    // 页码
    const maxPages = 7;
    let pages = [];
    if(totalPages <= maxPages){
        pages = Array.from({length: totalPages}, (_,i) => i+1);
    } else {
        pages = [1];
        if(listPage > 3) pages.push('...');
        for(let i = Math.max(2, currentPage-1); i <= Math.min(totalPages-1, currentPage+1); i++){
            pages.push(i);
        }
        if(listPage < totalPages-2) pages.push('...');
        pages.push(totalPages);
    }
    
    pages.forEach(p => {
        if(p === '...'){
            btns += `<span style="padding:4px 8px">...</span>`;
        } else {
            const active = p === listPage ? 'background:var(--primary);color:#fff;border:none' : '';
            btns += `<button onclick="goPage(${p})" style="padding:4px 10px;border:1px solid var(--border);background:var(--surface);border-radius:6px;cursor:pointer;${active}">${p}</button>`;
        }
    });
    
    // 下一页
    if(listPage < totalPages){
        btns += `<button onclick="goPage(${listPage+1})" style="padding:4px 10px;border:1px solid var(--border);background:var(--surface);border-radius:6px;cursor:pointer">下一页 ▶</button>`;
    }
    
    btnsEl.innerHTML = btns;
}

function goPage(page){
    listPage = page;
    currentPage = page;
    renderList();
}

// ============================================================

function renderListPage(){
    const main=document.getElementById('mainContent');
    main.innerHTML=`<div class="page-header">
        <div class="page-title">知识库 <span>${filteredNodes.length} 个知识点</span></div>
        <select class="sort-select" onchange="sortNodes(this.value)">
            <option value="difficulty">按难度 ↑</option>
            <option value="difficulty-desc">按难度 ↓</option>
            <option value="importance">按重要性 ↑</option>
            <option value="importance-desc">按重要性 ↓</option>
            <option value="name">按名称</option>
        </select>
    </div>
    <div class="nodes-grid" id="nodesGrid"></div>
    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;margin-top:10px;border-top:1px solid var(--border)">
        <div id="paginationInfo" style="font-size:.85em;color:var(--text-secondary)"></div>
        <div id="paginationBtns" style="display:flex;gap:4px;align-items:center"></div>
    </div>`;
    listPage = 1;
    renderList();
}

function sortNodes(order){
    switch(order){
        case'difficulty':filteredNodes.sort((a,b)=>a.difficulty-b.difficulty);break;
        case'difficulty-desc':filteredNodes.sort((a,b)=>b.difficulty-a.difficulty);break;
        case'importance':filteredNodes.sort((a,b)=>a.importance-b.importance);break;
        case'importance-desc':filteredNodes.sort((a,b)=>b.importance-a.importance);break;
        case'name':filteredNodes.sort((a,b)=>(a.name?.zh||'').localeCompare(b.name?.zh||''));break;
    }
    listPage = 1;
    renderList();
}

// 分页相关变量
let listPage = 1;
const pageSize = 50;

function renderList(){
    const grid=document.getElementById('nodesGrid');
    if(!grid)return;
    if(filteredNodes.length===0){grid.innerHTML=`<div class="empty-state"><div class="empty-state-icon">📚</div><div class="empty-state-title">暂无数据</div></div>`;document.getElementById('paginationInfo').innerHTML='';document.getElementById('paginationBtns').innerHTML='';return}
    
    // 计算分页
    const totalPages = Math.ceil(filteredNodes.length / pageSize);
    const start = (listPage - 1) * pageSize;
    const end = Math.min(start + pageSize, filteredNodes.length);
    const pageNodes = filteredNodes.slice(start, end);
    
    grid.innerHTML=pageNodes.map(n=>{
        const gradeTag=n.tags&&n.tags.find(t=>GRADE_COLOR[t]);
        const borderColor=gradeTag?GRADE_COLOR[gradeTag]:'var(--primary)';
        const hasPrereq=n.prerequisites&&n.prerequisites.length>0;
        const inDegree=(inLinks.get(n.id)||[]).length;
        const isIsolated=!hasPrereq&&inDegree===0;
        const diffDots=Array.from({length:10},(_,i)=>`<div class="diff-dot${i<n.difficulty?' filled':''}"></div>`).join('');
        return `<div class="node-card" onclick="openDetail('${n.id}')" style="--accent:${borderColor}">
            <style>.node-card[style*="${borderColor}"]::before{background:${borderColor}}</style>
            <div class="node-card-header">
                <div class="node-card-title">${n.name?.zh||n.name||''}</div>
                <div style="display:flex;gap:4px;align-items:center">
                    <span class="type-badge ${TYPE_BADGE[n.type]||'tb-concept'}">${n.type||'概念'}</span>
                    <a href="/app/web/admin.html?node=${n.id}" target="_blank" onclick="event.stopPropagation()" style="padding:2px 6px;background:#6366f1;color:#fff;text-decoration:none;border-radius:4px;font-size:.7em">管理</a>
                </div>
            </div>
            <div class="node-card-desc">${n.description?.zh||n.description||''}</div>
            <div class="node-card-tags">
                ${gradeTag?`<span class="mini-tag mt-grade">${gradeTag}</span>`:''}
                ${n.branch?`<span class="mini-tag mt-branch">${BRANCH_NAMES[n.branch]||n.branch}</span>`:''}
            </div>
            <div class="node-card-footer">
                <div class="diff-row">
                    <span>难度</span>
                    <div class="diff-dots">${diffDots}</div>
                </div>
                <div class="time-est">⏱ ${n.estimated_minutes||60}min</div>
                <div class="prereq-chip${hasPrereq?' has':''}${isIsolated?' isolated':''}">▶ ${isIsolated?'🔴 孤立':hasPrereq?n.prerequisites.length+'个先修':'无先修'}</div>
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

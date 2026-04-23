async function openDetail(id){
    const n=allNodes.find(x=>x.id===id);if(!n)return;
    document.getElementById('detailPanel').classList.remove('hidden');
    document.getElementById('detailTitle').textContent=n.name?.zh||n.name||'';
    document.getElementById('detailSubtitle').textContent=`${n.type||'concept'} · ${BRANCH_NAMES[n.branch]||n.branch||'其他'}`;
    const gradeTag=n.tags&&n.tags.find(t=>GRADE_COLOR[t]);
    const content=document.getElementById('detailContent');
    content.innerHTML=`
        <div class="detail-section"><div class="detail-section-title">描述</div><div class="detail-desc">${n.description?.zh||n.description||'暂无描述'}</div></div>
        <div class="detail-section"><div class="detail-section-title">标签</div><div class="detail-tags">${(n.tags||[]).map(t=>`<span class="detail-tag" style="background:${GRADE_COLOR[t]?'#f1f5f9':'var(--bg)'};color:${GRADE_COLOR[t]||'var(--text-secondary)'};border:1px solid ${GRADE_COLOR[t]||'var(--border)'}">${t}</span>`).join('')}</div></div>
        <div class="detail-section"><div class="detail-section-title">指标</div>
            <div class="detail-metrics">
                <div class="metric-card"><div class="metric-value">${n.difficulty}</div><div class="metric-label">难度</div></div>
                <div class="metric-card"><div class="metric-value">${n.importance}</div><div class="metric-label">重要性</div></div>
                <div class="metric-card"><div class="metric-value">${n.estimated_minutes||60}</div><div class="metric-label">分钟</div></div>
            </div>
        </div>
        ${n.has_obsidian_notes?`<div class="detail-section"><div class="detail-section-title">📝 Obsidian 笔记 (${n.obsidian_count}篇)</div><div class="detail-tags">${(n.obsidian_notes||[]).map(note=>`<span class="detail-tag" style="background:#fef3c7;color:#d97706;cursor:pointer">📄 ${note}</span>`).join('')}</div></div>`:''}
        ${(n.prerequisites||[]).length>0?`<div class="detail-section"><div class="detail-section-title">前置知识</div><div class="prereq-list">${(await getPrereqDetails(n.prerequisites)).map(p=>`<div class="rel-item" onclick="openDetail('${p.id}')"><div class="rel-arrow">←</div><span>${typeof p.name==="object"?p.name.zh||p.name.en||p.name||p.id:p.name||p.id}</span></div>`).join('')}</div></div>`:''}
        <div class="detail-section"><div class="detail-section-title">后续知识</div><div id="nextNodesList"><div class="loading" style="padding:10px;font-size:.85em">加载中</div></div></div>
        <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
            <a href="/app/web/admin.html?node=${n.id}" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;background:#6366f1;color:#fff;text-decoration:none;border-radius:6px;font-size:.85em;font-weight:500">
                🔧 管理知识点
            </a>
        </div>
    `;
    // 加载后续知识
    fetchNextNodes(n.id);
}

async function getPrereqDetails(prereqs){
    const ids = getPrereqIds(prereqs);
    return ids.map(id=>{const n=allNodes.find(x=>x.id===id);const name=n?.name;return n?{id:n.id,name:typeof name==='object'?name.zh||name.en||name||id:name||id}:{id,name:id}}).filter(x=>x);
}

async function fetchNextNodes(nodeId){
    const next=allNodes.filter(n=>getPrereqIds(n.prerequisites).includes(nodeId));
    const el=document.getElementById('nextNodesList');
    if(!el)return;
    if(next.length===0){el.innerHTML='<div style="font-size:.85em;color:var(--text-secondary)">暂无后续知识</div>';return}
    el.innerHTML=next.slice(0,10).map(n=>`<div class="rel-item" onclick="openDetail('${n.id}')"><div class="rel-arrow">→</div><span>${n.name?.zh||n.name||n.id}</span></div>`).join('');
}

function openObsidianNote(notePath){
    const vault = encodeURIComponent('Pkmer-Math');
    const note = encodeURIComponent(notePath);
    window.open(`obsidian://open?vault=${vault}&file=${note}`);
}
function closeDetail(){document.getElementById('detailPanel').classList.add('hidden')}

// ============================================================
function handleSearch(q){
    const el=document.getElementById('searchResults');
    if(!q.trim()){el.classList.remove('show');return}
    const results=allNodes.filter(n=>(n.name?.zh||'').includes(q)||(n.name?.en||'').includes(q)||(n.description?.zh||'').includes(q)).slice(0,8);
    if(results.length===0){el.innerHTML=`<div class="search-item"><div class="search-item-name">未找到结果</div></div>`;el.classList.add('show');return}
    el.innerHTML=results.map(n=>`<div class="search-item" onclick="openDetail('${n.id}');document.getElementById('searchResults').classList.remove('show');document.getElementById('searchInput').value=''">
        <div class="search-item-name">${n.name?.zh||n.name||''}</div>
        <div class="search-item-meta">${(n.tags||[]).filter(t=>GRADE_COLOR[t]).join(' · ')||n.branch?(BRANCH_NAMES[n.branch]||n.branch):''}</div>
    </div>`).join('');
    el.classList.add('show');
}

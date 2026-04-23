async function renderConjecturesPage(){
    document.getElementById('mainContent').innerHTML = `
    <div style="max-width:1200px;margin:0 auto">
        <div style="margin-bottom:20px">
            <h2 style="font-size:1.5em;font-weight:700;margin-bottom:6px">🚀 数学前沿问题</h2>
            <p style="color:var(--text-secondary);font-size:.9em">包含著名未解猜想、开放数学问题和重要研究前沿，支持按类型和难度筛选，展示关联图谱</p>
        </div>
        
        <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
            <div style="display:flex;gap:6px">
                <button class="mini-btn${conjectureFilter==='all'?' active':''}" onclick="setConjectureFilter('all')">全部</button>
                <button class="mini-btn${conjectureFilter==='conjecture'?' active':''}" onclick="setConjectureFilter('conjecture')">🤔 猜想</button>
                <button class="mini-btn${conjectureFilter==='problem'?' active':''}" onclick="setConjectureFilter('problem')">❓ 未解问题</button>
                <button class="mini-btn${conjectureFilter==='proved'?' active':''}" onclick="setConjectureFilter('proved')">✅ 已解决</button>
                <button class="mini-btn${conjectureFilter==='unproved'?' active':''}" onclick="setConjectureFilter('unproved')">❓ 未解决</button>
            </div>
            <div style="margin-left:auto;display:flex;gap:6px;align-items:center">
                <span style="font-size:.85em;color:var(--text-secondary)">排序:</span>
                <button class="mini-btn${conjectureSort==='difficulty'?' active':''}" onclick="setConjectureSort('difficulty')">按难度</button>
                <button class="mini-btn${conjectureSort==='name'?' active':''}" onclick="setConjectureSort('name')">按名称</button>
            </div>
        </div>
        
        <div id="conjectureStats" style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap"></div>
        <div id="conjectureList" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px"></div>
    </div>`;
    
    renderConjectureList();
}

function setConjectureFilter(f){ conjectureFilter = f; renderConjectureList(); }
function setConjectureSort(s){ conjectureSort = s; renderConjectureList(); }

function renderConjectureList(){
    // 获取猜想 + 问题
    let conjectures = allNodes.filter(n =>
        n.type === 'conjecture' ||
        n.type === 'problem' ||
        (n.tags && (n.tags.includes('数学猜想') || n.tags.includes('数学问题') || n.tags.includes('重要问题')))
    );
    
    const conj = conjectures.filter(n => n.type === 'conjecture');
    const prob = conjectures.filter(n => n.type === 'problem');
    const proved = conjectures.filter(n => ['proved','disproved'].includes(n.status));
    const unproved = conjectures.filter(n => ['unproved','unknown'].includes(n.status));
    
    document.getElementById('conjectureStats').innerHTML = `
        <div style="background:var(--surface);padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:var(--primary)">${conjectures.length}</div>
            <div style="font-size:.82em;color:var(--text-secondary)">全部前沿问题</div>
        </div>
        <div style="background:#fce7f3;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#db2777">${conj.length}</div>
            <div style="font-size:.82em;color:#be185d">🤔 猜想</div>
        </div>
        <div style="background:#fef3c7;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#d97706">${prob.length}</div>
            <div style="font-size:.82em;color:#b45309">❓ 未解问题</div>
        </div>
        <div style="background:#fee2e2;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#dc2626">${unproved.length}</div>
            <div style="font-size:.82em;color:#b91c1c">❓ 未解决</div>
        </div>
        <div style="background:#dcfce7;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#16a34a">${proved.length}</div>
            <div style="font-size:.82em;color:#15803d">✅ 已解决</div>
        </div>`;
    
    // 过滤
    if(conjectureFilter === 'conjecture'){ conjectures = conj; }
    else if(conjectureFilter === 'problem'){ conjectures = prob; }
    else if(conjectureFilter === 'proved'){ conjectures = conjectures.filter(n => ['proved','disproved'].includes(n.status)); }
    else if(conjectureFilter === 'unproved'){ conjectures = conjectures.filter(n => ['unproved','unknown'].includes(n.status)); }
    
    // 排序
    if(conjectureSort === 'difficulty'){
        conjectures.sort((a,b) => (b.difficulty||50) - (a.difficulty||50));
    } else if(conjectureSort === 'name'){
        conjectures.sort((a,b) => (a.name?.zh||'').localeCompare(b.name?.zh||''));
    }
    
    const list = document.getElementById('conjectureList');
    if(conjectures.length === 0){
        list.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-secondary)">暂无符合条件的记录</div>';
        return;
    }
    
    const statusColors = {
        proved: {bg:'#dcfce7', color:'#16a34a', text:'✅ 已解决'},
        disproved: {bg:'#fee2e2', color:'#dc2626', text:'❌ 已否定'},
        partially_proved: {bg:'#fef3c7', color:'#d97706', text:'🔄 部分解决'},
        unproved: {bg:'#fee2e2', color:'#dc2626', text:'❓ 未解决'},
        disputed: {bg:'#fef3c7', color:'#d97706', text:'⚠️ 争议中'},
        unknown: {bg:'#f1f5f9', color:'#64748b', text:'❓ 未解决'}
    };
    const diffLabels = ['', '入门', '基础', '进阶', '困难', '极难'];
    
    list.innerHTML = conjectures.map(c => {
        const name = c.name?.zh || c.name?.en || '';
        const desc = c.description?.zh || c.name?.zh || '';
        const status = c.status || 'unknown';
        const difficulty = c.difficulty || 50;
        const year = c.year || '';
        const proposer = c.proposer || '';
        const type = c.type || 'conjecture';
        const isConj = type === 'conjecture';
        const sc = statusColors[status] || statusColors.unknown;
        const diffDots = Math.round(difficulty / 20);
        const diffLabel = diffLabels[diffDots] || '未知';
        const typeLabel = isConj ? '🤔 猜想' : '❓ 问题';
        const typeColor = isConj ? '#db2777' : '#d97706';
        
        return `
        <div class="conjecture-card" onclick="showConjectureDetail('${c.id}')" style="background:var(--surface);border-radius:14px;padding:20px;box-shadow:var(--shadow);cursor:pointer;transition:all .2s;border:1px solid var(--border)">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px">
                <h3 style="font-size:1.05em;font-weight:600;line-height:1.3;flex:1;max-width:70%">${name}</h3>
                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-left:8px">
                    <span style="font-size:.72em;padding:2px 8px;border-radius:20px;font-weight:600;background:${typeColor}22;color:${typeColor}">${typeLabel}</span>
                    <span style="font-size:.72em;padding:2px 8px;border-radius:20px;font-weight:600;background:${sc.bg};color:${sc.color}">${sc.text}</span>
                </div>
            </div>
            <p style="font-size:.85em;color:var(--text-secondary);line-height:1.6;margin-bottom:14px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">${desc}</p>
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px">
                ${year ? `<span style="font-size:.78em;padding:3px 8px;background:#f1f5f9;border-radius:6px;color:var(--text-secondary)">📅 ${year}</span>` : ''}
                ${proposer ? `<span style="font-size:.78em;padding:3px 8px;background:#f1f5f9;border-radius:6px;color:var(--text-secondary)">👤 ${proposer}</span>` : ''}
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;padding-top:12px;border-top:1px solid var(--border)">
                <div style="display:flex;align-items:center;gap:6px">
                    <span style="font-size:.78em;color:var(--text-secondary)">难度:</span>
                    <div style="display:flex;gap:3px">
                        ${[1,2,3,4,5].map(i => `<div style="width:8px;height:8px;border-radius:50%;background:${i<=diffDots?'#f59e0b':'#e2e8f0'}"></div>`).join('')}
                    </div>
                    <span style="font-size:.75em;color:var(--text-secondary)">${diffLabel}</span>
                </div>
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

function showConjectureDetail(nodeId){
    try {
    // 全局辅助函数已在上方定义
    function escapeHtml(str) {
        if (!str) return '';
        return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/\n/g,'<br>');
    }
    const node = allNodes.find(n => n.id === nodeId);
    if(!node) {
        console.error('节点未找到:', nodeId);
        return;
    }
    
    const name = escapeHtml(node.name?.zh || node.name?.en || '');
    const desc = escapeHtml(node.description?.zh || node.name?.zh || '');
    const status = node.status || 'unknown';
    const year = node.year || '';
    const proposer = node.proposer || '';
    const statusDetail = node.status_detail || '';
    const branch = node.branch || '';
    const type = node.type || 'conjecture';
    const isConj = type === 'conjecture';
    
    const statusColors = {
        proved: {bg:'#dcfce7', color:'#16a34a', text:'✅ 已解决'},
        disproved: {bg:'#fee2e2', color:'#dc2626', text:'❌ 已否定'},
        partially_proved: {bg:'#fef3c7', color:'#d97706', text:'🔄 部分解决'},
        unproved: {bg:'#fee2e2', color:'#dc2626', text:'❓ 未解决'},
        disputed: {bg:'#fef3c7', color:'#d97706', text:'⚠️ 争议中'}
    };
    const sc = statusColors[status] || {bg:'#f1f5f9',color:'#64748b',text:'❓ 未知'};
    
    const prereqs = getPrereqIds(node.prerequisites).map(pid => {
        const p = allNodes.find(n => n.id === pid);
        return p ? `<span onclick="showConjectureDetail('${pid}')" style="display:inline-block;padding:4px 10px;background:#dbeafe;border-radius:6px;font-size:.8em;color:#0284c7;cursor:pointer;margin:2px">${p.name?.zh||pid}</span>` : '';
    }).join('');
    
    const related = allNodes.filter(n => {
        if(n.id === nodeId) return false;
        const nname = (n.name?.zh||'') + (n.name?.en||'');
        return nname.includes(name.substring(0,4)) || (n.branch === branch && n.type !== 'conjecture' && n.type !== 'problem');
    }).slice(0,12).map(n => {
        return `<span onclick="showConjectureDetail('${n.id}')" style="display:inline-block;padding:4px 10px;background:#f1f5f9;border-radius:6px;font-size:.8em;color:#64748b;cursor:pointer;margin:2px">${n.name?.zh||n.id}</span>`;
    }).join('');
    
    const typeLabel = isConj ? '🤔 猜想' : '❓ 数学问题';
    const typeColor = isConj ? '#db2777' : '#d97706';
    
    const modal = document.createElement('div');
    modal.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000;padding:20px';
    modal.onclick = (e) => { if(e.target===modal) modal.remove(); };
    modal.innerHTML = `
    <div style="background:var(--surface);border-radius:16px;max-width:700px;width:100%;max-height:80vh;overflow-y:auto;box-shadow:var(--shadow-lg)">
        <div style="padding:24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between">
            <h2 style="font-size:1.3em;font-weight:700">${name}</h2>
            <button onclick="this.closest('div').parentElement.remove()" style="background:none;border:none;font-size:1.5em;cursor:pointer;padding:8px;color:var(--text-secondary)">×</button>
        </div>
        <div style="padding:24px">
            <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
                <span style="padding:4px 12px;border-radius:20px;font-size:.85em;font-weight:600;background:${typeColor}22;color:${typeColor}">${typeLabel}</span>
                <span style="padding:4px 12px;border-radius:20px;font-size:.85em;font-weight:600;background:${sc.bg};color:${sc.color}">${sc.text}</span>
                <span style="padding:4px 12px;border-radius:20px;font-size:.85em;background:#f1f5f9;color:var(--text-secondary)">📚 ${branch}</span>
                ${year ? `<span style="padding:4px 12px;border-radius:20px;font-size:.85em;background:#f1f5f9;color:var(--text-secondary)">📅 ${year}年</span>` : ''}
            </div>
            <div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:8px;color:var(--text)">📝 问题内容</h4>
                <p style="font-size:.9em;line-height:1.7;color:var(--text-secondary)">${desc}</p>
            </div>
            ${proposer ? `<div style="margin-bottom:20px"><h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">👤 提出者</h4><p style="font-size:.9em;color:var(--text-secondary)">${proposer}</p></div>` : ''}
            ${statusDetail ? `<div style="margin-bottom:20px"><h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">📊 状态说明</h4><p style="font-size:.9em;line-height:1.6;color:var(--text-secondary)">${statusDetail}</p></div>` : ''}
            ${prereqs ? `<div style="margin-bottom:20px"><h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">📖 前置知识</h4><div style="display:flex;flex-wrap:wrap;gap:6px">${prereqs}</div></div>` : ''}
            ${related ? `<div style="margin-bottom:20px"><h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">🔗 相关知识</h4><div style="display:flex;flex-wrap:wrap;gap:6px">${related}</div></div>` : ''}
            <div style="display:flex;gap:10px;margin-top:24px">
                <button onclick="viewConjectureGraph('${nodeId}')" style="flex:1;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--surface);cursor:pointer;font-weight:500">查看关联图谱</button>
            </div>
        </div>
    </div>`;
    document.body.appendChild(modal);
    } catch(e) {
        console.error('showConjectureDetail 错误:', e);
    }
}




// ===== 错题本页面（支持分页+图片）=====
const WQ_PAGE_SIZE = 10;


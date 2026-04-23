// ============================================================
// 数学家页面
// ============================================================
let mathematicianFilter = 'all';
let mathematicianSort = 'name';
async function renderMathematiciansPage(){
    document.getElementById('mainContent').innerHTML = `
    <div style="max-width:1200px;margin:0 auto">
        <div style="margin-bottom:20px">
            <h2 style="font-size:1.5em;font-weight:700;margin-bottom:6px">👨‍🔬 数学家</h2>
            <p style="color:var(--text-secondary);font-size:.9em">著名数学家及其贡献，按时期、领域筛选</p>
        </div>
        <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
            <div style="display:flex;gap:6px">
                <button class="mini-btn${mathematicianFilter==='all'?' active':''}" onclick="setMathematicianFilter('all')">全部</button>
                <button class="mini-btn${mathematicianFilter==='ancient'?' active':''}" onclick="setMathematicianFilter('ancient')">🏛️ 古代</button>
                <button class="mini-btn${mathematicianFilter==='modern'?' active':''}" onclick="setMathematicianFilter('modern')">📜 近代</button>
                <button class="mini-btn${mathematicianFilter==='contemporary'?' active':''}" onclick="setMathematicianFilter('contemporary')">🌟 现代</button>
            </div>
            <div style="margin-left:auto;display:flex;gap:6px;align-items:center">
                <span style="font-size:.85em;color:var(--text-secondary)">排序:</span>
                <button class="mini-btn${mathematicianSort==='name'?' active':''}" onclick="setMathematicianSort('name')">按姓名</button>
                <button class="mini-btn${mathematicianSort==='birth'?' active':''}" onclick="setMathematicianSort('birth')">按年代</button>
            </div>
        </div>
        <div id="mathematicianStats" style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap"></div>
        <div id="mathematicianList" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px"></div>
    </div>`;
    renderMathematicianList();
}
function setMathematicianFilter(f){ mathematicianFilter = f; renderMathematicianList(); }
function setMathematicianSort(s){ mathematicianSort = s; renderMathematicianList(); }
function renderMathematicianList(){
    // 从allNodes中筛选出数学家
    let mathematicians = allNodes.filter(n =>
        n.type === 'mathematician' ||
        (n.tags && (n.tags.includes('数学家') || n.tags.includes('数学人物')))
    );
    // 统计数据
    const ancient = mathematicians.filter(n => n.birth_year && n.birth_year < 1500);
    const modern = mathematicians.filter(n => n.birth_year && n.birth_year >= 1500 && n.birth_year < 1900);
    const contemporary = mathematicians.filter(n => n.birth_year && n.birth_year >= 1900);
    const statsEl = document.getElementById('mathematicianStats');
    if(statsEl){
        statsEl.innerHTML = `
        <div style="background:var(--surface);padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:var(--primary)">${mathematicians.length}</div>
            <div style="font-size:.82em;color:var(--text-secondary)">全部数学家</div>
        </div>
        <div style="background:#fef3c7;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#d97706">${ancient.length}</div>
            <div style="font-size:.82em;color:#b45309">🏛️ 古代</div>
        </div>
        <div style="background:#dbeafe;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#2563eb">${modern.length}</div>
            <div style="font-size:.82em;color:#1d4ed8">📜 近代</div>
        </div>
        <div style="background:#dcfce7;padding:12px 20px;border-radius:10px;box-shadow:var(--shadow)">
            <div style="font-size:1.8em;font-weight:700;color:#16a34a">${contemporary.length}</div>
            <div style="font-size:.82em;color:#15803d">🌟 现代</div>
        </div>`;
    }
    // 过滤
    if(mathematicianFilter === 'ancient'){ mathematicians = ancient; }
    else if(mathematicianFilter === 'modern'){ mathematicians = modern; }
    else if(mathematicianFilter === 'contemporary'){ mathematicians = contemporary; }
    // 排序
    if(mathematicianSort === 'name'){
        mathematicians.sort((a,b) => (a.name?.zh||'').localeCompare(b.name?.zh||''));
    } else if(mathematicianSort === 'birth'){
        mathematicians.sort((a,b) => (a.birth_year||0) - (b.birth_year||0));
    }
    const list = document.getElementById('mathematicianList');
    if(!list) return;
    if(mathematicians.length === 0){
        list.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-secondary)">暂无数学家数据</div>';
        return;
    }
    list.innerHTML = mathematicians.map(m => {
        const name = m.name?.zh || m.name?.en || '';
        const desc = m.description?.zh || m.biography?.zh || '';
        const birth = m.birth_year || '?';
        const death = m.death_year || '?';
        const period = m.birth_year < 1500 ? '🏛️ 古代' : m.birth_year < 1900 ? '📜 近代' : '🌟 现代';
        const periodColor = m.birth_year < 1500 ? '#d97706' : m.birth_year < 1900 ? '#2563eb' : '#16a34a';
        const fields = (m.fields || m.contributions || []).slice(0, 3).map(f => 
            `<span style="font-size:.72em;padding:2px 8px;border-radius:10px;background:#f1f5f9;color:var(--text-secondary)">${f}</span>`
        ).join('');
        return `
        <div class="mathematician-card" onclick="showMathematicianDetail('${m.id}')" style="background:var(--surface);border-radius:14px;padding:20px;box-shadow:var(--shadow);cursor:pointer;transition:all .2s;border:1px solid var(--border)">
            <div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:12px">
                <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--primary-light));display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.5em;font-weight:600;flex-shrink:0">
                    ${name.charAt(0)}
                </div>
                <div style="flex:1;min-width:0">
                    <h3 style="font-size:1.1em;font-weight:600;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${name}</h3>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px">
                        <span style="font-size:.72em;padding:2px 8px;border-radius:20px;font-weight:600;background:${periodColor}22;color:${periodColor}">${period}</span>
                        <span style="font-size:.72em;padding:2px 8px;border-radius:20px;background:#f1f5f9;color:var(--text-secondary)">${birth}-${death}</span>
                    </div>
                </div>
            </div>
            <p style="font-size:.85em;color:var(--text-secondary);line-height:1.6;margin-bottom:12px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${desc}</p>
            <div style="display:flex;flex-wrap:wrap;gap:4px">${fields}</div>
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
function showMathematicianDetail(nodeId){
    const node = allNodes.find(n => n.id === nodeId);
    if(!node) return;
    const name = node.name?.zh || node.name?.en || '';
    const desc = node.description?.zh || node.biography?.zh || '';
    const birth = node.birth_year || node.year?.split('—')[0] || '?';
    const death = node.death_year || node.year?.split('—')[1] || '?';
    const birthplace = node.birthplace || '';
    const nationality = node.nationality || node.country || '';
    const fields = node.fields || node.contributions || [];
    const works = node.works || node.known_works || [];
    // 查找该数学家相关的数学知识
    // 1. 发现的定理 - 通过 mathematicians 字段或名称匹配
    const discoveredTheorems = allNodes.filter(n => {
        if (n.type !== 'theorem' && n.type !== 'formula' && n.type !== 'law') return false;
        // 检查 mathematicians 字段
        if (n.mathematicians && n.mathematicians.includes(nodeId)) return true;
        // 检查 discoverer 字段
        if (n.discoverer === nodeId || n.discoverer === name) return true;
        // 检查 name 或 description 中是否包含数学家名字
        const nodeText = (n.name?.zh || '') + (n.description?.zh || '');
        return nodeText.includes(name) && n.type === 'theorem';
    }).slice(0, 10);
    // 2. 证明的定理
    const provedTheorems = allNodes.filter(n => {
        if (n.type !== 'theorem') return false;
        if (n.proved_by && (n.proved_by.includes(nodeId) || n.proved_by.includes(name))) return true;
        const nodeText = (n.name?.zh || '') + (n.description?.zh || '');
        return nodeText.includes(name) && n.type === 'theorem';
    }).slice(0, 10);
    // 3. 提出的问题/猜想
    const proposedProblems = allNodes.filter(n => {
        if (n.type !== 'conjecture' && n.type !== 'problem') return false;
        if (n.proposer === nodeId || n.proposer === name) return true;
        if (n.mathematicians && n.mathematicians.includes(nodeId)) return true;
        const nodeText = (n.name?.zh || '') + (n.description?.zh || '');
        return nodeText.includes(name) && (n.type === 'conjecture' || n.type === 'problem');
    }).slice(0, 10);
    // 4. 相关的概念
    const relatedConcepts = allNodes.filter(n => {
        if (n.type !== 'concept') return false;
        if (n.named_after && (n.named_after.includes(nodeId) || n.named_after.includes(name))) return true;
        const nodeText = (n.name?.zh || '') + (n.description?.zh || '');
        return nodeText.includes(name);
    }).slice(0, 8);
    const modal = document.createElement('div');
    modal.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000;padding:20px';
    modal.onclick = (e) => { if(e.target===modal) modal.remove(); };
    modal.innerHTML = `
    <div style="background:var(--surface);border-radius:16px;max-width:800px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:var(--shadow-lg)">
        <div style="padding:24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:16px">
                <div style="width:70px;height:70px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--primary-light));display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.8em;font-weight:600">${name.charAt(0)}</div>
                <div>
                    <h2 style="font-size:1.3em;font-weight:700">${name}</h2>
                    <div style="font-size:.85em;color:var(--text-secondary);margin-top:4px">${birth}-${death} · ${nationality} · ${birthplace}</div>
                </div>
            </div>
            <button onclick="this.closest('div').parentElement.remove()" style="background:none;border:none;font-size:1.5em;cursor:pointer;padding:8px;color:var(--text-secondary)">×</button>
        </div>
        <div style="padding:24px">
            <div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:8px;color:var(--text)">📝 简介</h4>
                <p style="font-size:.9em;line-height:1.7;color:var(--text-secondary)">${desc}</p>
            </div>
            ${fields.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">🔬 研究领域</h4>
                <div style="display:flex;flex-wrap:wrap;gap:6px">${fields.map(f => `<span style="padding:4px 12px;border-radius:20px;font-size:.85em;background:#dbeafe;color:#0284c7">${f}</span>`).join('')}</div>
            </div>` : ''}
            ${works.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:8px">📚 主要著作</h4>
                <ul style="font-size:.9em;color:var(--text-secondary);line-height:1.8;padding-left:20px">${works.map(w => `<li>${w}</li>`).join('')}</ul>
            </div>` : ''}
            <!-- 发现的定理 -->
            ${discoveredTheorems.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:6px">
                    <span>💡</span> 发现的定理/公式 (${discoveredTheorems.length})
                </h4>
                <div style="display:flex;flex-direction:column;gap:8px">
                    ${discoveredTheorems.map(t => `
                        <div onclick="showPage('graph');graphFocusNodeId='${t.id}';renderGraph();document.body.querySelector('[style*=\\\"position:fixed\\\"]').remove()" 
                             style="padding:10px 14px;background:#f0fdf4;border-radius:8px;cursor:pointer;transition:all .15s;border-left:3px solid #16a34a">
                            <div style="font-size:.9em;font-weight:500;color:#166534">${t.name?.zh || t.name}</div>
                            <div style="font-size:.8em;color:#65a30d;margin-top:2px">${t.description?.zh?.substring(0, 60) || ''}...</div>
                        </div>
                    `).join('')}
                </div>
            </div>` : ''}
            <!-- 证明的定理 -->
            ${provedTheorems.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:6px">
                    <span>✓</span> 证明的定理 (${provedTheorems.length})
                </h4>
                <div style="display:flex;flex-direction:column;gap:8px">
                    ${provedTheorems.map(t => `
                        <div onclick="showPage('graph');graphFocusNodeId='${t.id}';renderGraph();document.body.querySelector('[style*=\\\"position:fixed\\\"]').remove()" 
                             style="padding:10px 14px;background:#dbeafe;border-radius:8px;cursor:pointer;transition:all .15s;border-left:3px solid #2563eb">
                            <div style="font-size:.9em;font-weight:500;color:#1e40af">${t.name?.zh || t.name}</div>
                            <div style="font-size:.8em;color:#60a5fa;margin-top:2px">${t.description?.zh?.substring(0, 60) || ''}...</div>
                        </div>
                    `).join('')}
                </div>
            </div>` : ''}
            <!-- 提出的问题/猜想 -->
            ${proposedProblems.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:6px">
                    <span>❓</span> 提出的问题/猜想 (${proposedProblems.length})
                </h4>
                <div style="display:flex;flex-direction:column;gap:8px">
                    ${proposedProblems.map(p => `
                        <div onclick="showPage('conjectures');showConjectureDetail('${p.id}')" 
                             style="padding:10px 14px;background:#fef3c7;border-radius:8px;cursor:pointer;transition:all .15s;border-left:3px solid #d97706">
                            <div style="font-size:.9em;font-weight:500;color:#92400e">${p.name?.zh || p.name}</div>
                            <div style="font-size:.8em;color:#f59e0b;margin-top:2px">
                                ${p.status === 'proved' ? '✅ 已解决' : p.status === 'unproved' ? '❓ 未解决' : '❓ 待研究'}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>` : ''}
            <!-- 相关概念 -->
            ${relatedConcepts.length > 0 ? `<div style="margin-bottom:20px">
                <h4 style="font-size:.95em;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:6px">
                    <span>📐</span> 相关概念 (${relatedConcepts.length})
                </h4>
                <div style="display:flex;flex-wrap:wrap;gap:6px">
                    ${relatedConcepts.map(c => `
                        <span onclick="showPage('graph');graphFocusNodeId='${c.id}';renderGraph();document.body.querySelector('[style*=\\\"position:fixed\\\"]').remove()" 
                              style="padding:4px 12px;background:#f3e8ff;border-radius:20px;font-size:.85em;color:#7c3aed;cursor:pointer">
                            ${c.name?.zh || c.name}
                        </span>
                    `).join('')}
                </div>
            </div>` : ''}
        </div>
    </div>`;
    document.body.appendChild(modal);
}
// ============================================================
document.addEventListener('DOMContentLoaded',init);

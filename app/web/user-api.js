/**
 * 用户学习数据 API 模块
 * Phase 4: 前端对接
 * 
 * 使用方式:
 *   import { loadLearningStats, loadRecommendations } from './user-api.js';
 */

// 获取当前用户 ID
function getUserId() {
    return AUTH?.user?.id || null;
}

// 通用认证请求
async function authFetch(url, options = {}) {
    const headers = {
        ...options.headers,
        ...AUTH.getAuthHeaders()
    };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        AUTH.logout();
        throw new Error('Unauthorized');
    }
    return response;
}

// ============================================================
// 知识掌握 API
// ============================================================

/**
 * 获取用户知识掌握列表
 */
async function loadUserKnowledgeMap() {
    if (!AUTH.isAuthenticated()) return {};
    
    try {
        const res = await authFetch(`${API}/knowledge?limit=10000`);
        if (!res.ok) return {};
        
        const data = await res.json();
        const map = {};
        
        (data.items || []).forEach(item => {
            map[item.node_id] = {
                status: item.status,
                confidence: item.confidence,
                study_count: item.study_count,
                correct_count: item.correct_count,
                last_study_at: item.last_study_at
            };
        });
        
        return map;
    } catch (e) {
        console.warn('加载用户知识失败:', e);
        return {};
    }
}

/**
 * 更新知识点掌握状态
 */
async function updateKnowledge(nodeId, status, confidence = 0.5, correct = true) {
    if (!AUTH.isAuthenticated()) return null;
    
    try {
        const res = await authFetch(`${API}/knowledge`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ node_id: nodeId, status, confidence, correct })
        });
        
        if (!res.ok) throw new Error('更新失败');
        return await res.json();
    } catch (e) {
        console.warn('更新知识失败:', e);
        return null;
    }
}

/**
 * 获取学习统计
 */
async function loadLearningStats() {
    if (!AUTH.isAuthenticated()) return null;
    
    try {
        const res = await authFetch(`${API}/knowledge/stats`);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.warn('加载学习统计失败:', e);
        return null;
    }
}

/**
 * 获取特定节点的掌握状态
 */
async function getNodeKnowledge(nodeId) {
    if (!AUTH.isAuthenticated()) return null;
    
    try {
        const res = await authFetch(`${API}/knowledge/node/${nodeId}`);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        return null;
    }
}

// ============================================================
// 学习路径推荐 API
// ============================================================

/**
 * 获取学习推荐
 */
async function loadRecommendations(limit = 10) {
    if (!AUTH.isAuthenticated()) return null;
    
    try {
        const res = await authFetch(`${API}/learning-path/recommendations?limit=${limit}`);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.warn('加载推荐失败:', e);
        return null;
    }
}

/**
 * 获取掌握概览
 */
async function loadMasteryOverview() {
    if (!AUTH.isAuthenticated()) return null;
    
    try {
        const res = await authFetch(`${API}/learning-path/mastery-overview`);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.warn('加载掌握概览失败:', e);
        return null;
    }
}

// ============================================================
// 渲染函数
// ============================================================

/**
 * 渲染学习进度卡片到侧边栏
 */
async function renderLearningProgress() {
    const stats = await loadLearningStats();
    if (!stats) return;
    
    const total = stats.total_known + stats.total_learning + stats.total_unknown;
    const pct = total > 0 ? Math.round(stats.total_known / total * 100) : 0;
    
    // 更新各个元素
    const setEl = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    
    setEl('learningProgressBadge', `${pct}%`);
    setEl('knownCount', stats.total_known);
    setEl('learningCount', stats.total_learning);
    setEl('accuracyRate', `${stats.accuracy}%`);
    setEl('progressBarFill', `${pct}%`);
    setEl('studyCount', `总学习 ${stats.total_studied} 次`);
    setEl('streakDays', stats.streak_days > 0 ? `🔥 ${stats.streak_days}天` : '');
}

/**
 * 渲染推荐学习内容
 */
async function renderLearningRecommendations() {
    const data = await loadRecommendations(5);
    if (!data) return;
    
    const container = document.getElementById('recommendationsPanel');
    if (!container) return;
    
    // ready_to_learn
    const readyHtml = data.ready_to_learn.slice(0, 3).map(node => `
        <div class="rec-item ready" onclick="showNodeDetail('${node.node_id}')">
            <div class="rec-item-header">
                <span class="rec-name">${node.name}</span>
                <span class="rec-badge ready-badge">可学习</span>
            </div>
            <div class="rec-meta">
                <span class="rec-branch">${BRANCH_NAMES[node.branch] || node.branch}</span>
                <span class="rec-diff">★${node.difficulty}</span>
            </div>
        </div>
    `).join('');
    
    // next_challenges
    const challengeHtml = data.next_challenges.slice(0, 2).map(node => `
        <div class="rec-item challenge" onclick="showNodeDetail('${node.node_id}')">
            <div class="rec-item-header">
                <span class="rec-name">${node.name}</span>
                <span class="rec-badge challenge-badge">有挑战</span>
            </div>
            <div class="rec-meta">
                <span class="rec-branch">${BRANCH_NAMES[node.branch] || node.branch}</span>
                <span class="rec-blocked">需学前置</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div class="rec-section">
            <div class="rec-section-title">🎯 可直接学习</div>
            ${readyHtml || '<div class="rec-empty">暂无推荐</div>'}
        </div>
        <div class="rec-section">
            <div class="rec-section-title">🔥 挑战内容</div>
            ${challengeHtml || '<div class="rec-empty">暂无挑战</div>'}
        </div>
    `;
}

/**
 * 更新节点卡片上的掌握状态标记
 */
function updateNodeCardStatus(nodeId, status) {
    const card = document.querySelector(`[data-node-id="${nodeId}"]`);
    if (!card) return;
    
    // 移除旧状态
    card.classList.remove('node-known', 'node-learning', 'node-unknown');
    
    // 添加新状态
    if (status === 'known') {
        card.classList.add('node-known');
        const badge = card.querySelector('.status-badge');
        if (badge) badge.textContent = '✓ 已掌握';
    } else if (status === 'learning') {
        card.classList.add('node-learning');
    }
}

/**
 * 标记节点为已学习（快捷函数）
 */
async function markNodeAs(nodeId, status, correct = true) {
    const result = await updateKnowledge(nodeId, status, 0.5, correct);
    if (result) {
        userKnowledge[nodeId] = { status, ...result };
        updateNodeCardStatus(nodeId, status);
        updateLocalStats();
    }
    return result;
}

// ============================================================
// 本地统计更新（无需再请求 API）
// ============================================================

function updateLocalStats() {
    const known = Object.values(userKnowledge).filter(k => k.status === 'known').length;
    const learning = Object.values(userKnowledge).filter(k => k.status === 'learning').length;
    const total = allNodes.length;
    const pct = total > 0 ? Math.round(known / total * 100) : 0;
    
    // 更新侧边栏
    const el = document.getElementById('localStatsKnown');
    if (el) el.textContent = known;
    
    const el2 = document.getElementById('localStatsPct');
    if (el2) el2.textContent = `${pct}%`;
}

// 导出（兼容全局）
if (typeof window !== 'undefined') {
    window.loadUserKnowledgeMap = loadUserKnowledgeMap;
    window.updateKnowledge = updateKnowledge;
    window.loadLearningStats = loadLearningStats;
    window.getNodeKnowledge = getNodeKnowledge;
    window.loadRecommendations = loadRecommendations;
    window.loadMasteryOverview = loadMasteryOverview;
    window.renderLearningProgress = renderLearningProgress;
    window.renderLearningRecommendations = renderLearningRecommendations;
    window.updateNodeCardStatus = updateNodeCardStatus;
    window.markNodeAs = markNodeAs;
    window.updateLocalStats = updateLocalStats;
}

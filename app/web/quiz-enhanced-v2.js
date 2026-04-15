// ============================================================
// 增强版知识点同步页面 - 支持学习统计、4级评估、复习提醒
// ============================================================

let quizUserProfile = null;
let quizReviewQueue = [];

// 加载用户知识画像
async function loadUserKnowledgeProfile() {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/knowledge-profile`);
        quizUserProfile = await r.json();
    } catch (e) {
        console.error('Failed to load knowledge profile:', e);
        quizUserProfile = null;
    }
}

// 加载复习队列
async function loadReviewQueue() {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/review-queue?limit=10`);
        const data = await r.json();
        quizReviewQueue = data.queue || [];
    } catch (e) {
        console.error('Failed to load review queue:', e);
        quizReviewQueue = [];
    }
}

// 渲染学习统计卡片
function renderLearningStats() {
    if (!quizUserProfile || !quizUserProfile.stats) {
        return '';
    }
    
    const stats = quizUserProfile.stats;
    const summary = quizUserProfile.learning_summary || {};
    
    return `
    <div style="background:linear-gradient(135deg,#6366f1,#818cf8);border-radius:16px;padding:20px;color:#fff;margin-bottom:16px">
        <div style="font-size:1.1em;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:8px">
            📊 学习统计
            <span style="font-size:.75em;opacity:.8;font-weight:400">(${quizUserProfile.profile?.name || USER_ID})</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
            <div style="text-align:center;background:rgba(255,255,255,.15);border-radius:12px;padding:14px 8px">
                <div style="font-size:2em;font-weight:700">${stats.total_concepts || 0}</div>
                <div style="font-size:.78em;opacity:.9">总知识点</div>
            </div>
            <div style="text-align:center;background:rgba(255,255,255,.15);border-radius:12px;padding:14px 8px">
                <div style="font-size:2em;font-weight:700;color:#86efac">${stats.mastered || 0}</div>
                <div style="font-size:.78em;opacity:.9">已掌握</div>
            </div>
            <div style="text-align:center;background:rgba(255,255,255,.15);border-radius:12px;padding:14px 8px">
                <div style="font-size:2em;font-weight:700;color:#fde047">${stats.learning || 0}</div>
                <div style="font-size:.78em;opacity:.9">学习中</div>
            </div>
            <div style="text-align:center;background:rgba(255,255,255,.15);border-radius:12px;padding:14px 8px">
                <div style="font-size:2em;font-weight:700;color:#fca5a5">${stats.needs_review || 0}</div>
                <div style="font-size:.78em;opacity:.9">需复习</div>
            </div>
        </div>
        ${summary.total_practice_time ? `
        <div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,.2);display:flex;justify-content:space-around;font-size:.85em">
            <span>⏱️ 总学习时长: ${Math.round(summary.total_practice_time / 60)} 小时</span>
            <span>🔥 连续学习: ${summary.current_streak || 0} 天</span>
        </div>
        ` : ''}
    </div>`;
}

// 渲染复习提醒
function renderReviewAlert() {
    if (!quizReviewQueue || quizReviewQueue.length === 0) {
        return '';
    }
    
    const firstItem = quizReviewQueue[0];
    const totalTime = quizReviewQueue.reduce((sum, item) => sum + 5, 0); // 假设每题5分钟
    
    return `
    <div style="background:linear-gradient(135deg,#f97316,#fb923c);border-radius:14px;padding:16px;color:#fff;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:12px">
        <div style="display:flex;align-items:center;gap:12px;flex:1">
            <div style="font-size:2em">🔥</div>
            <div>
                <div style="font-weight:600;margin-bottom:2px">有 ${quizReviewQueue.length} 个知识点需要复习</div>
                <div style="font-size:.85em;opacity:.9">
                    优先: ${firstItem.name?.zh || firstItem.node_id} 
                    (掌握度 ${firstItem.mastery}%, ${firstItem.days_since_practice} 天未复习)
                </div>
                <div style="font-size:.8em;opacity:.8;margin-top:4px">预计 ${totalTime} 分钟完成全部复习</div>
            </div>
        </div>
        <button onclick="startReviewMode()" style="padding:10px 18px;background:#fff;color:#f97316;border:none;border-radius:10px;font-weight:600;cursor:pointer;white-space:nowrap">
            开始复习
        </button>
    </div>`;
}

// 开始复习模式
async function startReviewMode() {
    if (!quizReviewQueue || quizReviewQueue.length === 0) {
        showToast('暂无需要复习的知识点');
        return;
    }
    
    // 将复习队列转换为题目
    quizQuestions = quizReviewQueue.map(item => {
        // 从 allNodes 中找到对应的节点
        const node = allNodes.find(n => n.id === item.node_id);
        return node || {
            id: item.node_id,
            name: item.name,
            tags: [quizLevel],
            branch: 'other'
        };
    }).filter(q => q); // 过滤掉未找到的
    
    quizIndex = 0;
    quizAnswers = {};
    quizReviewed = new Set();
    isReviewMode = true;
    
    renderQuizContent();
}

// 渲染增强版同步页面
async function renderQuizPageEnhanced() {
    // 加载用户数据
    await Promise.all([loadUserKnowledgeProfile(), loadReviewQueue()]);
    
    // 如果已有进行中的评测，先恢复状态
    const hasInProgress = quizQuestions.length > 0 && quizIndex < quizQuestions.length;

    // 获取当前年级的分支列表
    const gradeNodes = quizLevel ? allNodes.filter(n => n.tags && n.tags.includes(quizLevel)) : [];
    const branchCounts = {};
    gradeNodes.forEach(n => {
        const b = n.branch || 'other';
        branchCounts[b] = (branchCounts[b] || 0) + 1;
    });

    // 计算每个年级的已同步数量
    const gradeSyncCounts = {};
    GRADE_LEVELS.forEach(g => {
        if (g.id === 'all') return;
        const gradeNodes = allNodes.filter(n => n.tags && n.tags.includes(g.id));
        const knownCount = quizUserProfile?.knowledge_state ? 
            gradeNodes.filter(n => {
                const state = quizUserProfile.knowledge_state[n.id];
                return state && state.mastery >= 70;
            }).length : 0;
        gradeSyncCounts[g.id] = { total: gradeNodes.length, known: knownCount };
    });

    // 年级按钮行（显示同步进度）
    const gradeBtns = GRADE_LEVELS.filter(g => g.id !== 'all').map(g => {
        const counts = gradeSyncCounts[g.id] || { total: 0, known: 0 };
        const pct = counts.total > 0 ? Math.round(counts.known / counts.total * 100) : 0;
        const syncStatus = counts.known > 0 ? 
            `<span style="color:#10b981;font-size:.7em">✓${counts.known}/${counts.total}</span>` : 
            `<span style="opacity:.5;font-size:.7em">${counts.total}</span>`;
        return `<button class="mini-btn${quizLevel===g.id?' active':''}" onclick="selectQuizLevel('${g.id}')" style="padding:5px 10px;font-size:.8em;display:flex;flex-direction:column;align-items:center;gap:2px">
            <span>${g.name}</span>
            <span>${syncStatus}</span>
        </button>`;
    }).join('');

    // 分支按钮行（仅大学及以上显示）
    let branchBtns = '';
    if (quizLevel === '大学及以上') {
        branchBtns = `<div style="margin-bottom:10px">
            <div style="font-size:.78em;color:var(--text-secondary);margin-bottom:6px;font-weight:500">按分支筛选</div>
            <div style="display:flex;flex-wrap:wrap;gap:5px">
                <button class="mini-btn${quizBranch===''?' active':''}" onclick="selectQuizBranch('')" style="padding:4px 9px;font-size:.78em">全部</button>
                ${Object.entries(branchCounts).sort((a,b)=>b[1]-a[1]).map(([k,c])=>`<button class="mini-btn${quizBranch===k?' active':''}" onclick="selectQuizBranch('${k}')" style="padding:4px 9px;font-size:.78em">${BRANCH_NAMES[k]||k}(${c})</button>`).join('')}
            </div>
        </div>`;
    }

    // 进度信息
    let progressHtml = '';
    if (hasInProgress) {
        const pct = (quizIndex / quizQuestions.length * 100).toFixed(0);
        progressHtml = `<div class="quiz-progress-wrap" style="margin-top:10px">
            <div class="quiz-progress-track"><div class="quiz-progress-fill" style="width:${pct}%"></div></div>
            <div class="quiz-progress-text">${quizIndex}/${quizQuestions.length}</div>
        </div>`;
    }

    // 学习统计
    const statsHtml = renderLearningStats();
    
    // 复习提醒
    const reviewAlertHtml = renderReviewAlert();

    document.getElementById('mainContent').innerHTML = `<div class="quiz-page">
        ${statsHtml}
        ${reviewAlertHtml}
        <div class="quiz-header">
            <div style="font-size:1.1em;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:8px">
                📝 知识点同步
                ${isReviewMode ? '<span style="background:#f97316;color:#fff;padding:2px 8px;border-radius:10px;font-size:.7em">复习模式</span>' : ''}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px">${gradeBtns}</div>
            ${branchBtns}
            <div style="display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap">
                <button class="mini-btn${hasInProgress?' active':''}" onclick="startQuiz()" id="startQuizBtn">${hasInProgress?'▶ 继续同步':'开始同步'}</button>
                ${quizLevel ? `<button class="mini-btn" onclick="syncAll('${quizLevel}')" style="background:#10b981;color:#fff;border:none">⚡ 全部掌握</button>` : ''}
                ${quizReviewQueue.length > 0 ? `<button class="mini-btn" onclick="startReviewMode()" style="background:#f97316;color:#fff;border:none">🔥 复习 (${quizReviewQueue.length})</button>` : ''}
                ${isReviewMode ? `<button class="mini-btn" onclick="exitReviewMode()">退出复习</button>` : ''}
            </div>
            ${progressHtml}
        </div>
        <div id="quizContent"></div>
    </div>`;

    if (hasInProgress) renderQuizContentEnhanced();
}

// 退出复习模式
function exitReviewMode() {
    isReviewMode = false;
    quizQuestions = [];
    quizIndex = 0;
    quizAnswers = {};
    renderQuizPageEnhanced();
}

// 选择年级
async function selectQuizLevelEnhanced(l) {
    quizLevel = l;
    quizBranch = '';
    quizQuestions = [];
    quizIndex = 0;
    quizAnswers = {};
    quizReviewed = new Set();
    isReviewMode = false;
    await renderQuizPageEnhanced();
}

// 选择分支
async function selectQuizBranchEnhanced(b) {
    quizBranch = b;
    quizQuestions = [];
    quizIndex = 0;
    quizAnswers = {};
    quizReviewed = new Set();
    await renderQuizPageEnhanced();
}

// 开始同步
async function startQuizEnhanced() {
    if (!quizLevel) { showToast('请先选择年级'); return; }

    // 从前端过滤
    let pool = allNodes.filter(n => n.tags && n.tags.includes(quizLevel) && !quizReviewed.has(n.id));
    if (quizBranch) pool = pool.filter(n => n.branch === quizBranch);

    if (pool.length === 0) { showToast('该范围内知识点已全部评测'); return; }

    // 随机打乱
    pool.sort(() => Math.random() - 0.5);
    quizQuestions = pool;
    quizIndex = 0;
    quizAnswers = {};
    isReviewMode = false;
    renderQuizContentEnhanced();
}

// 渲染增强版题目内容（4级评估）
async function renderQuizContentEnhanced() {
    const el = document.getElementById('quizContent');
    if (!el) return;

    if (quizQuestions.length === 0 || quizIndex >= quizQuestions.length) {
        if (Object.keys(quizAnswers).length > 0) {
            // 使用详细评估 API 保存
            await saveDetailedAssessments();
            await loadUserKnowledgeProfile();
            await loadReviewQueue();
            
            const done = Object.keys(quizAnswers).length;
            const modeText = isReviewMode ? '复习' : '同步';
            el.innerHTML = `<div class="quiz-card" style="text-align:center;padding:40px 20px">
                <div style="font-size:3em;margin-bottom:16px">🎉</div>
                <div style="font-size:1.2em;font-weight:600;margin-bottom:12px">本轮${modeText}完成！</div>
                <div style="color:var(--text-secondary);margin-bottom:8px">已完成 <strong style="color:var(--primary);font-size:1.2em">${done}</strong> 道题</div>
                <div style="color:var(--text-secondary);margin-bottom:20px;font-size:.9em">数据已保存，掌握度已更新</div>
                <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
                    <button class="quiz-action-btn primary" onclick="startQuizEnhanced()">再测一轮</button>
                    <button class="quiz-action-btn" onclick="renderQuizPageEnhanced()">返回主页</button>
                    <button class="quiz-action-btn" onclick="showPage('stats')">查看统计</button>
                </div>
            </div>`;
        } else {
            el.innerHTML = `<div class="empty-state" style="padding:60px 20px">
                <div class="empty-state-icon" style="font-size:3em">📝</div>
                <div class="empty-state-title" style="font-size:1.1em;margin-top:16px">选择年级开始同步</div>
                <div style="color:var(--text-secondary);margin-top:8px">评估你的知识点掌握情况</div>
            </div>`;
        }
        return;
    }

    const q = quizQuestions[quizIndex];
    const pct = (quizIndex / quizQuestions.length * 100).toFixed(0);
    const gradeTag = q.tags && q.tags.find(t => GRADE_COLOR[t]) || quizLevel;
    const branchName = BRANCH_NAMES[q.branch] || q.branch || '';
    
    // 获取当前知识状态
    const currentState = quizUserProfile?.knowledge_state?.[q.id];
    const currentMastery = currentState?.mastery || 0;
    const lastPractice = currentState?.last_practice;
    const daysSince = lastPractice ? 
        Math.floor((new Date() - new Date(lastPractice)) / (1000 * 60 * 60 * 24)) : null;

    el.innerHTML = `<div class="quiz-card" style="padding:24px">
        <div class="quiz-progress-wrap" style="margin-bottom:16px">
            <div class="quiz-progress-track"><div class="quiz-progress-fill" style="width:${pct}%"></div></div>
            <div class="quiz-progress-text">${quizIndex + 1}/${quizQuestions.length}</div>
        </div>
        
        ${currentMastery > 0 ? `
        <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:12px 16px;margin-bottom:16px;display:flex;align-items:center;gap:12px">
            <span style="font-size:1.5em">📊</span>
            <div style="flex:1">
                <div style="font-size:.85em;color:#166534;font-weight:500">当前掌握度</div>
                <div style="display:flex;align-items:center;gap:10px;margin-top:4px">
                    <div style="flex:1;height:8px;background:#bbf7d0;border-radius:4px;overflow:hidden">
                        <div style="width:${currentMastery}%;height:100%;background:#22c55e;border-radius:4px"></div>
                    </div>
                    <span style="font-weight:600;color:#166534">${currentMastery}%</span>
                </div>
            </div>
            ${daysSince !== null ? `<span style="font-size:.75em;color:#15803d;white-space:nowrap">${daysSince}天前练习</span>` : ''}
        </div>
        ` : ''}
        
        <div class="quiz-question" style="font-size:1.15em;margin-bottom:8px">${q.name?.zh || q.name || ''}</div>
        <div class="quiz-meta" style="margin-bottom:16px">
            <span class="quiz-meta-tag mt-grade">${gradeTag}</span>
            ${branchName ? `<span class="quiz-meta-tag mt-branch">${branchName}</span>` : ''}
        </div>
        
        ${q.detail ? `<div style="margin:16px 0;padding:14px;background:#f8fafc;border-radius:10px;border-left:4px solid #6366f1">
            <div style="font-size:.78em;color:#6366f1;font-weight:600;margin-bottom:6px">📖 定义</div>
            <div style="font-size:.92em;color:#334155;line-height:1.6">${q.detail.definition || ''}</div>
            ${q.detail.explanation ? `<div style="font-size:.85em;color:#64748b;margin-top:10px">💡 ${q.detail.explanation}</div>` : ''}
        </div>` : ''}
        
        ${q.examples && q.examples.length > 0 ? `<div style="margin:16px 0">
            <div style="font-size:.78em;color:#059669;font-weight:600;margin-bottom:8px">📝 例题</div>
            ${q.examples.slice(0,2).map((ex,i) => `<div style="background:#f0fdf4;padding:12px;border-radius:8px;margin-bottom:8px;font-size:.88em">
                <div style="color:#1e293b;font-weight:500">例${i+1}: ${ex.question || ''}</div>
                <div style="color:#16a34a;margin-top:6px;font-weight:500">答案: ${ex.answer || ''}</div>
                ${ex.solution ? `<div style="color:#64748b;font-size:.85em;margin-top:6px">解析: ${ex.solution}</div>` : ''}
            </div>`).join('')}
        </div>` : ''}
        
        <div style="font-size:.85em;color:var(--text-secondary);margin-bottom:12px;font-weight:500">选择你的掌握程度：</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            <button class="quiz-btn" onclick="answerQuizEnhanced(3)" style="background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;border:none;padding:14px;border-radius:10px;font-weight:600">
                <div style="font-size:1.3em;margin-bottom:4px">⭐⭐⭐</div>
                <div>完全掌握</div>
                <div style="font-size:.75em;opacity:.9;font-weight:400">可以教别人</div>
            </button>
            <button class="quiz-btn" onclick="answerQuizEnhanced(2)" style="background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;border:none;padding:14px;border-radius:10px;font-weight:600">
                <div style="font-size:1.3em;margin-bottom:4px">⭐⭐</div>
                <div>基本掌握</div>
                <div style="font-size:.75em;opacity:.9;font-weight:400">能做题但偶尔错</div>
            </button>
            <button class="quiz-btn" onclick="answerQuizEnhanced(1)" style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;padding:14px;border-radius:10px;font-weight:600">
                <div style="font-size:1.3em;margin-bottom:4px">⭐</div>
                <div>有点模糊</div>
                <div style="font-size:.75em;opacity:.9;font-weight:400">需要复习</div>
            </button>
            <button class="quiz-btn" onclick="answerQuizEnhanced(0)" style="background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;border:none;padding:14px;border-radius:10px;font-weight:600">
                <div style="font-size:1.3em;margin-bottom:4px">❓</div>
                <div>完全不会</div>
                <div style="font-size:.75em;opacity:.9;font-weight:400">需要重新学习</div>
            </button>
        </div>
    </div>`;
}

// 4级评估答题
async function answerQuizEnhanced(level) {
    const q = quizQuestions[quizIndex];
    const id = q.id;
    
    // 保存答案（使用 level 而不是 known）
    quizAnswers[id] = level;
    quizReviewed.add(id);
    quizIndex++;
    
    renderQuizContentEnhanced();
}

// 保存详细评估结果
async function saveDetailedAssessments() {
    const assessments = Object.entries(quizAnswers).map(([id, level]) => ({
        node_id: id,
        level: level,
        notes: isReviewMode ? '复习模式评估' : '同步评估'
    }));
    
    try {
        const r = await fetch(`${API}/users/${USER_ID}/detailed-assess`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(assessments)
        });
        
        if (!r.ok) {
            console.error('Failed to save assessments:', await r.text());
        } else {
            const result = await r.json();
            console.log('Assessments saved:', result);
        }
    } catch (e) {
        console.error('Error saving assessments:', e);
    }
}

// 覆盖原有函数
const originalRenderQuizPage = renderQuizPage;
const originalSelectQuizLevel = selectQuizLevel;
const originalSelectQuizBranch = selectQuizBranch;
const originalStartQuiz = startQuiz;
const originalAnswerQuiz = answerQuiz;

renderQuizPage = renderQuizPageEnhanced;
selectQuizLevel = selectQuizLevelEnhanced;
selectQuizBranch = selectQuizBranchEnhanced;
startQuiz = startQuizEnhanced;
answerQuiz = answerQuizEnhanced;

// 添加复习模式标志
let isReviewMode = false;

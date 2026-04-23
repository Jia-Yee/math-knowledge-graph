async function renderQuizPage(){
    // 如果已有进行中的评测，先恢复状态
    const hasInProgress = quizQuestions.length > 0 && quizIndex < quizQuestions.length;

    // 获取当前年级的分支列表
    const gradeNodes = quizLevel ? allNodes.filter(n => n.tags && n.tags.includes(quizLevel)) : [];
    const branchCounts = {};
    gradeNodes.forEach(n => {
        const b = n.branch || 'other';
        branchCounts[b] = (branchCounts[b] || 0) + 1;
    });

    // 年级按钮行
    const gradeBtns = GRADE_LEVELS.filter(g => g.id !== 'all').map(g => {
        const total = allNodes.filter(n => n.tags && n.tags.includes(g.id)).length;
        const known = userKnowledge ? allNodes.filter(n => n.tags && n.tags.includes(g.id) && userKnowledge[n.id]).length : 0;
        const syncStatus = known > 0 ? `<span style="color:#10b981;font-size:.7em">✓${known}</span>` : '';
        return `<button class="mini-btn${quizLevel===g.id?' active':''}" onclick="selectQuizLevel('${g.id}')" style="padding:5px 10px;font-size:.8em">${g.name}<span style="opacity:.6;margin-left:3px">${total}${syncStatus}</span></button>`;
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

    document.getElementById('mainContent').innerHTML = `<div class="quiz-page">
        <div class="quiz-header">
            <div style="font-size:1.1em;font-weight:600;margin-bottom:10px">📝 知识点同步</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px">${gradeBtns}</div>
            ${branchBtns}
            <div style="display:flex;gap:8px;align-items:center;margin-top:8px">
                <button class="mini-btn${hasInProgress?' active':''}" onclick="startQuiz()" id="startQuizBtn">${hasInProgress?'▶ 继续同步':'开始同步'}</button>
                ${quizLevel ? `<button class="mini-btn" onclick="syncAll('${quizLevel}')" style="background:#10b981;color:#fff;border:none">⚡ 全部同步</button>` : ''}
            </div>
            ${progressHtml}
        </div>
        <div id="quizContent"></div>
    </div>`;

    if (hasInProgress) renderQuizContent();
}

function selectQuizLevel(l) {
    quizLevel = l;
    quizBranch = '';
    quizQuestions = [];
    quizIndex = 0;
    quizAnswers = {};
    quizReviewed = new Set();
    renderQuizPage();
}

function selectQuizBranch(b) {
    quizBranch = b;
    quizQuestions = [];
    quizIndex = 0;
    quizAnswers = {};
    quizReviewed = new Set();
    renderQuizPage();
}

async function startQuiz() {
    if (!quizLevel) { showToast('请先选择年级'); return; }

    // 从前端过滤（用 quizReviewed 排除本轮已同步的，不依赖 userKnowledge）
    let pool = allNodes.filter(n => n.tags && n.tags.includes(quizLevel) && !quizReviewed.has(n.id));
    if (quizBranch) pool = pool.filter(n => n.branch === quizBranch);

    if (pool.length === 0) { showToast('该范围内知识点已全部评测'); return; }

    // 随机打乱，取最多50题
    pool.sort(() => Math.random() - 0.5);
    quizQuestions = pool; // 全部知识点
    quizIndex = 0;
    quizAnswers = {};
    renderQuizContent();
}

async function renderQuizContent() {
    const el = document.getElementById('quizContent');
    if (!el) return;

    if (quizQuestions.length === 0 || quizIndex >= quizQuestions.length) {
        if (Object.keys(quizAnswers).length > 0) {
            // 保存到后端
            const assessments = Object.entries(quizAnswers).map(([id, k]) => ({ node_id: id, known: k }));
            await fetch(`${API}/users/${USER_ID}/assess`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: USER_ID, assessments })
            }).catch(() => {});
            await loadUserKnowledge();
            const done = Object.keys(quizAnswers).length;
            el.innerHTML = `<div class="quiz-card" style="text-align:center">
                <div style="font-size:2em;margin-bottom:12px">🎉</div>
                <div style="font-size:1.1em;font-weight:600;margin-bottom:8px">本轮评测完成！</div>
                <div style="color:var(--text-secondary);margin-bottom:6px">已完成 <strong>${done}</strong> 道题，已保存</div>
                <div style="color:var(--text-secondary);margin-bottom:16px;font-size:.85em">（如需继续同步同年级其他分支，可再次点击"开始同步"）</div>
                <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
                    <button class="quiz-action-btn primary" onclick="startQuiz()">再测一轮</button>
                    <button class="quiz-action-btn" onclick="renderQuizPage()">更换年级/分支</button>
                    <button class="quiz-action-btn" onclick="showPage('stats')">查看统计</button>
                </div>
            </div>`;
        } else {
            el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📝</div><div class="empty-state-title">选择年级和分支开始同步</div></div>`;
        }
        return;
    }

    const q = quizQuestions[quizIndex];
    const pct = (quizIndex / quizQuestions.length * 100).toFixed(0);
    const gradeTag = q.tags && q.tags.find(t => GRADE_COLOR[t]) || quizLevel;
    const branchName = BRANCH_NAMES[q.branch] || q.branch || '';

    el.innerHTML = `<div class="quiz-card">
        <div class="quiz-progress-wrap" style="margin-bottom:14px">
            <div class="quiz-progress-track"><div class="quiz-progress-fill" style="width:${pct}%"></div></div>
            <div class="quiz-progress-text">${quizIndex + 1}/${quizQuestions.length}</div>
        </div>
        <div class="quiz-question">${q.name?.zh || q.name || ''}</div>
        <div class="quiz-meta">
            <span class="quiz-meta-tag mt-grade">${gradeTag}</span>
            ${branchName ? `<span class="quiz-meta-tag mt-branch">${branchName}</span>` : ''}
        </div>
        ${q.detail ? `<div style="margin:12px 0;padding:10px;background:#f8fafc;border-radius:8px;border-left:3px solid #6366f1">
            <div style="font-size:.75em;color:#6366f1;font-weight:600;margin-bottom:4px">📖 定义</div>
            <div style="font-size:.9em;color:#334155;line-height:1.5">${q.detail.definition || ''}</div>
            ${q.detail.explanation ? `<div style="font-size:.85em;color:#64748b;margin-top:8px">💡 ${q.detail.explanation}</div>` : ''}
        </div>` : ''}
        ${q.examples && q.examples.length > 0 ? `<div style="margin:12px 0">
            <div style="font-size:.75em;color:#059669;font-weight:600;margin-bottom:6px">📝 例题</div>
            ${q.examples.slice(0,2).map((ex,i) => `<div style="background:#f0fdf4;padding:10px;border-radius:6px;margin-bottom:6px;font-size:.85em">
                <div style="color:#1e293b">例${i+1}: ${ex.question || ''}</div>
                <div style="color:#16a34a;margin-top:4px">答案: ${ex.answer || ''}</div>
                ${ex.solution ? `<div style="color:#64748b;font-size:.8em;margin-top:4px">解析: ${ex.solution}</div>` : ''}
            </div>`).join('')}
        </div>` : ''}
        <div class="quiz-btn-group">
            <button class="quiz-btn quiz-btn-known" onclick="answerQuiz(true)">✅ 掌握</button>
            <button class="quiz-btn quiz-btn-unknown" onclick="answerQuiz(false)">❌ 不熟悉</button>
        </div>
    </div>`;
}

async function answerQuiz(known) {
    const q = quizQuestions[quizIndex];
    const id = q.id;
    quizAnswers[id] = known;
    quizReviewed.add(id);
    quizIndex++;
    renderQuizContent();
}

// ============================================================

// ============================================================
// 数学前沿问题页面
// ============================================================
let conjectureFilter = 'all';
let conjectureSort = 'difficulty';


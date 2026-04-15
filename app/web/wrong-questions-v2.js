// ============================================================
// 错题本页面 - 支持记录、复习、统计错题
// ============================================================

let wrongQuestions = [];
let wrongQuestionStats = null;
let todayReviewList = [];
let wrongQuestionImages = [];

// 加载错题数据
async function loadWrongQuestions(status = 'active') {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions?status=${status}&limit=50`);
        const data = await r.json();
        wrongQuestions = data.wrong_questions || [];
        return data;
    } catch (e) {
        console.error('Failed to load wrong questions:', e);
        wrongQuestions = [];
        return null;
    }
}

// 加载错题统计
async function loadWrongQuestionStats() {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/stats`);
        wrongQuestionStats = await r.json();
        return wrongQuestionStats;
    } catch (e) {
        console.error('Failed to load wrong question stats:', e);
        wrongQuestionStats = null;
        return null;
    }
}

// 加载今日复习列表
async function loadTodayReview() {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/today`);
        const data = await r.json();
        todayReviewList = data.wrong_questions || [];
        return data;
    } catch (e) {
        console.error('Failed to load today review:', e);
        todayReviewList = [];
        return null;
    }
}

// 渲染错题本页面
async function renderWrongQuestionsPage() {
    // 加载数据
    await Promise.all([
        loadWrongQuestions(),
        loadWrongQuestionStats(),
        loadTodayReview()
    ]);
    
    const stats = wrongQuestionStats || {};
    
    document.getElementById('mainContent').innerHTML = `
    <div style="max-width:1200px;margin:0 auto">
        <div style="margin-bottom:20px">
            <h2 style="font-size:1.5em;font-weight:700;margin-bottom:6px;display:flex;align-items:center;gap:10px">
                📚 错题本
                <button onclick="showAddWrongQuestionModal()" style="padding:8px 16px;background:#6366f1;color:#fff;border:none;border-radius:8px;font-size:.65em;font-weight:600;cursor:pointer">
                    + 记录错题
                </button>
                <button onclick="showPhotoUploadModal()" style="padding:8px 16px;background:#10b981;color:#fff;border:none;border-radius:8px;font-size:.65em;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:6px">
                    📷 拍照上传
                </button>
            </h2>
            <p style="color:var(--text-secondary);font-size:.9em">记录错题，定期复习，针对性提高</p>
        </div>
        
        <!-- 统计卡片 -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px">
            <div style="background:linear-gradient(135deg,#6366f1,#818cf8);border-radius:14px;padding:20px;color:#fff">
                <div style="font-size:2.2em;font-weight:700">${stats.total_wrong || 0}</div>
                <div style="font-size:.85em;opacity:.9">总错题</div>
            </div>
            <div style="background:linear-gradient(135deg,#ef4444,#f87171);border-radius:14px;padding:20px;color:#fff">
                <div style="font-size:2.2em;font-weight:700">${stats.active || 0}</div>
                <div style="font-size:.85em;opacity:.9">未掌握</div>
            </div>
            <div style="background:linear-gradient(135deg,#f97316,#fb923c);border-radius:14px;padding:20px;color:#fff">
                <div style="font-size:2.2em;font-weight:700">${stats.needs_review_today || 0}</div>
                <div style="font-size:.85em;opacity:.9">今日需复习</div>
            </div>
            <div style="background:linear-gradient(135deg,#10b981,#34d399);border-radius:14px;padding:20px;color:#fff">
                <div style="font-size:2.2em;font-weight:700">${stats.mastered || 0}</div>
                <div style="font-size:.85em;opacity:.9">已掌握</div>
            </div>
        </div>
        
        <!-- 今日复习提醒 -->
        ${todayReviewList.length > 0 ? `
        <div style="background:linear-gradient(135deg,#f97316,#fb923c);border-radius:14px;padding:16px;color:#fff;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between">
            <div style="display:flex;align-items:center;gap:12px">
                <div style="font-size:2em">🔥</div>
                <div>
                    <div style="font-weight:600">今日有 ${todayReviewList.length} 道错题需要复习</div>
                    <div style="font-size:.85em;opacity:.9">预计 ${todayReviewList.length * 5} 分钟完成</div>
                </div>
            </div>
            <button onclick="startWrongQuestionReview()" style="padding:10px 20px;background:#fff;color:#f97316;border:none;border-radius:10px;font-weight:600;cursor:pointer">
                开始复习
            </button>
        </div>
        ` : ''}
        
        <!-- 错误类型分布 -->
        ${stats.by_error_type && Object.keys(stats.by_error_type).length > 0 ? `
        <div style="background:var(--surface);border-radius:14px;padding:20px;margin-bottom:24px;box-shadow:var(--shadow)">
            <h3 style="font-size:1em;font-weight:600;margin-bottom:16px">📊 错误类型分布</h3>
            <div style="display:flex;flex-wrap:wrap;gap:10px">
                ${Object.entries(stats.by_error_type).map(([type, count]) => `
                    <div style="padding:8px 16px;background:#f1f5f9;border-radius:20px;font-size:.85em">
                        <span style="font-weight:600">${getErrorTypeName(type)}</span>
                        <span style="color:var(--text-secondary);margin-left:6px">${count}道</span>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
        
        <!-- 筛选栏 -->
        <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;align-items:center">
            <select id="wqStatusFilter" onchange="filterWrongQuestions()" style="padding:8px 12px;border:1px solid var(--border);border-radius:8px;background:var(--surface)">
                <option value="active">未掌握</option>
                <option value="mastered">已掌握</option>
                <option value="all">全部</option>
            </select>
            <select id="wqErrorTypeFilter" onchange="filterWrongQuestions()" style="padding:8px 12px;border:1px solid var(--border);border-radius:8px;background:var(--surface)">
                <option value="">全部错误类型</option>
                <option value="concept_error">概念理解错误</option>
                <option value="calculation_error">计算错误</option>
                <option value="formula_error">公式记错</option>
                <option value="misunderstanding">审题错误</option>
                <option value="careless">粗心大意</option>
                <option value="wrong_approach">思路错误</option>
                <option value="confusion">知识点混淆</option>
                <option value="other">其他</option>
            </select>
            <input type="text" id="wqSearch" placeholder="搜索题目..." onkeyup="filterWrongQuestions()" style="padding:8px 12px;border:1px solid var(--border);border-radius:8px;flex:1;min-width:200px">
        </div>
        
        <!-- 错题列表 -->
        <div id="wrongQuestionsList">
            ${renderWrongQuestionsList()}
        </div>
    </div>`;
}

// 获取错误类型名称
function getErrorTypeName(type) {
    const names = {
        'concept_error': '概念理解错误',
        'calculation_error': '计算错误',
        'formula_error': '公式记错',
        'misunderstanding': '审题错误',
        'careless': '粗心大意',
        'wrong_approach': '思路错误',
        'confusion': '知识点混淆',
        'other': '其他'
    };
    return names[type] || type;
}

// 渲染错题列表
function renderWrongQuestionsList() {
    if (wrongQuestions.length === 0) {
        return `
        <div style="text-align:center;padding:60px 20px;background:var(--surface);border-radius:14px">
            <div style="font-size:3em;margin-bottom:16px">📚</div>
            <div style="font-size:1.1em;font-weight:600;color:var(--text)">暂无错题记录</div>
            <div style="color:var(--text-secondary);margin-top:8px">在做题时记录错题，系统会帮你安排复习</div>
            <button onclick="showAddWrongQuestionModal()" style="margin-top:20px;padding:10px 20px;background:#6366f1;color:#fff;border:none;border-radius:8px;cursor:pointer">
                记录第一道错题
            </button>
        </div>`;
    }
    
    return wrongQuestions.map(wq => {
        const schedule = wq.review_schedule || {};
        const isMastered = schedule.mastered;
        const nextReview = schedule.next_review;
        const daysUntil = nextReview ? 
            Math.ceil((new Date(nextReview) - new Date()) / (1000 * 60 * 60 * 24)) : null;
        const hasImages = wq.images && wq.images.length > 0;
        
        return `
        <div style="background:var(--surface);border-radius:14px;padding:20px;margin-bottom:16px;box-shadow:var(--shadow);border-left:4px solid ${isMastered ? '#10b981' : daysUntil !== null && daysUntil <= 0 ? '#f97316' : '#6366f1'}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
                <div style="flex:1">
                    <div style="font-weight:600;font-size:1.05em;margin-bottom:6px">${wq.question?.content || '无题目内容'}</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
                        <span style="padding:3px 10px;background:#fee2e2;color:#dc2626;border-radius:20px;font-size:.75em">错: ${wq.wrong_answer}</span>
                        <span style="padding:3px 10px;background:#dcfce7;color:#16a34a;border-radius:20px;font-size:.75em">对: ${wq.correct_answer}</span>
                        ${hasImages ? `<span style="padding:3px 10px;background:#fef3c7;color:#d97706;border-radius:20px;font-size:.75em">📷 ${wq.images.length}张图</span>` : ''}
                    </div>
                </div>
                <div style="display:flex;gap:6px">
                    ${!isMastered ? `
                        <button onclick="markWrongQuestionMastered('${wq.id}')" style="padding:6px 12px;background:#10b981;color:#fff;border:none;border-radius:6px;font-size:.75em;cursor:pointer">标记掌握</button>
                    ` : ''}
                    <button onclick="deleteWrongQuestion('${wq.id}')" style="padding:6px 12px;background:#ef4444;color:#fff;border:none;border-radius:6px;font-size:.75em;cursor:pointer">删除</button>
                </div>
            </div>
            
            <div id="wq-images-${wq.id}"></div>
            
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
                <span style="padding:4px 10px;background:#f1f5f9;border-radius:6px;font-size:.78em;color:var(--text-secondary)">${getErrorTypeName(wq.error_type)}</span>
                ${wq.tags?.map(tag => `<span style="padding:4px 10px;background:#e0e7ff;border-radius:6px;font-size:.78em;color:#4338ca">${tag}</span>`).join('') || ''}
            </div>
            
            ${wq.error_analysis ? `
            <div style="padding:10px;background:#fef3c7;border-radius:8px;margin-bottom:10px;font-size:.85em;color:#92400e">
                <strong>错误分析:</strong> ${wq.error_analysis}
            </div>
            ` : ''}
            
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:.8em;color:var(--text-secondary)">
                <span>📅 ${formatDate(wq.created_at)}</span>
                ${isMastered ? 
                    '<span style="color:#10b981;font-weight:500">✅ 已掌握</span>' : 
                    daysUntil !== null ? 
                        `<span style="color:${daysUntil <= 0 ? '#f97316' : 'var(--text-secondary)'};font-weight:500">${daysUntil <= 0 ? '🔥 今天复习' : `⏰ ${daysUntil}天后复习`}</span>` : 
                        ''
                }
            </div>
        </div>`;
    }).join('');
}

// 格式化日期
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-CN');
    } catch {
        return dateStr;
    }
}

// 筛选错题
async function filterWrongQuestions() {
    const status = document.getElementById('wqStatusFilter')?.value || 'active';
    const errorType = document.getElementById('wqErrorTypeFilter')?.value || '';
    const search = document.getElementById('wqSearch')?.value || '';
    
    let url = `${API}/users/${USER_ID}/wrong-questions?status=${status}`;
    if (errorType) url += `&error_type=${errorType}`;
    
    try {
        const r = await fetch(url);
        const data = await r.json();
        wrongQuestions = data.wrong_questions || [];
        
        // 本地搜索过滤
        if (search) {
            wrongQuestions = wrongQuestions.filter(wq => 
                wq.question?.content?.includes(search) ||
                wq.error_analysis?.includes(search)
            );
        }
        
        document.getElementById('wrongQuestionsList').innerHTML = renderWrongQuestionsList();
        
        // 加载错题图片
        wrongQuestions.forEach(wq => {
            if (wq.images && wq.images.length > 0) {
                showWrongQuestionImages(wq.id, `wq-images-${wq.id}`);
            }
        });
    } catch (e) {
        console.error('Failed to filter wrong questions:', e);
    }
}

// 显示添加错题弹窗
function showAddWrongQuestionModal() {
    const modal = document.createElement('div');
    modal.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000;padding:20px';
    modal.onclick = (e) => { if(e.target===modal) modal.remove(); };
    
    modal.innerHTML = `
    <div style="background:var(--surface);border-radius:16px;max-width:600px;width:100%;max-height:85vh;overflow-y:auto">
        <div style="padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
            <h3 style="font-size:1.2em;font-weight:600">记录新错题</h3>
            <button onclick="this.closest('.modal').remove()" style="background:none;border:none;font-size:1.5em;cursor:pointer;padding:4px">×</button>
        </div>
        <div style="padding:20px">
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">知识点</label>
                <select id="wqNodeId" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px">
                    <option value="">选择知识点...</option>
                    ${allNodes.slice(0, 100).map(n => `<option value="${n.id}">${n.name?.zh || n.id}</option>`).join('')}
                </select>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">题目内容</label>
                <textarea id="wqContent" rows="3" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;resize:vertical" placeholder="输入题目内容..."></textarea>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
                <div>
                    <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">你的答案</label>
                    <input type="text" id="wqWrongAnswer" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px" placeholder="错误答案">
                </div>
                <div>
                    <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">正确答案</label>
                    <input type="text" id="wqCorrectAnswer" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px" placeholder="正确答案">
                </div>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">错误类型</label>
                <select id="wqErrorType" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px">
                    <option value="concept_error">概念理解错误</option>
                    <option value="calculation_error">计算错误</option>
                    <option value="formula_error">公式记错</option>
                    <option value="misunderstanding">审题错误</option>
                    <option value="careless">粗心大意</option>
                    <option value="wrong_approach">思路错误</option>
                    <option value="confusion">知识点混淆</option>
                    <option value="other">其他</option>
                </select>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">错误分析</label>
                <textarea id="wqErrorAnalysis" rows="2" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;resize:vertical" placeholder="分析错误原因..."></textarea>
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end">
                <button onclick="this.closest('.modal').remove()" style="padding:10px 20px;border:1px solid var(--border);background:var(--surface);border-radius:8px;cursor:pointer">取消</button>
                <button onclick="saveWrongQuestion()" style="padding:10px 20px;background:#6366f1;color:#fff;border:none;border-radius:8px;cursor:pointer">保存</button>
            </div>
        </div>
    </div>`;
    modal.className = 'modal';
    document.body.appendChild(modal);
}

// 保存错题
async function saveWrongQuestion() {
    const nodeId = document.getElementById('wqNodeId')?.value;
    const content = document.getElementById('wqContent')?.value;
    const wrongAnswer = document.getElementById('wqWrongAnswer')?.value;
    const correctAnswer = document.getElementById('wqCorrectAnswer')?.value;
    const errorType = document.getElementById('wqErrorType')?.value;
    const errorAnalysis = document.getElementById('wqErrorAnalysis')?.value;
    
    if (!content || !wrongAnswer || !correctAnswer) {
        showToast('请填写完整信息');
        return;
    }
    
    const data = {
        node_id: nodeId || 'unknown',
        question: {
            content: content,
            type: 'calculation',
            difficulty: 5,
            source: 'manual'
        },
        wrong_answer: wrongAnswer,
        correct_answer: correctAnswer,
        error_type: errorType,
        error_analysis: errorAnalysis,
        tags: []
    };
    
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (r.ok) {
            showToast('错题已记录');
            document.querySelector('.modal')?.remove();
            await renderWrongQuestionsPage();
        } else {
            showToast('保存失败');
        }
    } catch (e) {
        console.error('Failed to save wrong question:', e);
        showToast('保存失败');
    }
}

// 标记掌握
async function markWrongQuestionMastered(wqId) {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/${wqId}/master`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({notes: '手动标记为已掌握'})
        });
        
        if (r.ok) {
            showToast('已标记为掌握');
            await renderWrongQuestionsPage();
        }
    } catch (e) {
        console.error('Failed to mark mastered:', e);
        showToast('操作失败');
    }
}

// 删除错题
async function deleteWrongQuestion(wqId) {
    if (!confirm('确定要删除这道错题吗？')) return;
    
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/${wqId}`, {
            method: 'DELETE'
        });
        
        if (r.ok) {
            showToast('已删除');
            await renderWrongQuestionsPage();
        }
    } catch (e) {
        console.error('Failed to delete wrong question:', e);
        showToast('删除失败');
    }
}

// 开始错题复习
let currentReviewIndex = 0;
let currentReviewList = [];

async function startWrongQuestionReview() {
    if (todayReviewList.length === 0) {
        showToast('今天没有需要复习的错题');
        return;
    }
    
    currentReviewList = todayReviewList;
    currentReviewIndex = 0;
    renderWrongQuestionReview();
}

// 渲染错题复习
function renderWrongQuestionReview() {
    if (currentReviewIndex >= currentReviewList.length) {
        // 复习完成
        document.getElementById('mainContent').innerHTML = `
        <div style="max-width:600px;margin:100px auto;text-align:center">
            <div style="font-size:4em;margin-bottom:20px">🎉</div>
            <h2 style="font-size:1.5em;font-weight:600;margin-bottom:12px">今日复习完成！</h2>
            <p style="color:var(--text-secondary);margin-bottom:24px">已完成 ${currentReviewList.length} 道错题的复习</p>
            <button onclick="renderWrongQuestionsPage()" style="padding:12px 24px;background:#6366f1;color:#fff;border:none;border-radius:10px;cursor:pointer">返回错题本</button>
        </div>`;
        return;
    }
    
    const wq = currentReviewList[currentReviewIndex];
    const progress = ((currentReviewIndex + 1) / currentReviewList.length * 100).toFixed(0);
    
    document.getElementById('mainContent').innerHTML = `
    <div style="max-width:700px;margin:0 auto;padding:20px">
        <div style="background:var(--surface);border-radius:16px;padding:24px;box-shadow:var(--shadow)">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
                <h2 style="font-size:1.2em;font-weight:600">🔥 错题复习 (${currentReviewIndex + 1}/${currentReviewList.length})</h2>
                <button onclick="renderWrongQuestionsPage()" style="padding:6px 12px;border:1px solid var(--border);background:var(--surface);border-radius:6px;cursor:pointer;font-size:.85em">退出</button>
            </div>
            
            <div style="height:6px;background:#e2e8f0;border-radius:3px;margin-bottom:24px;overflow:hidden">
                <div style="width:${progress}%;height:100%;background:linear-gradient(90deg,#f97316,#fb923c);border-radius:3px;transition:width .3s"></div>
            </div>
            
            <div style="margin-bottom:20px">
                <div style="font-size:.85em;color:var(--text-secondary);margin-bottom:8px">题目</div>
                <div style="font-size:1.15em;font-weight:500;padding:16px;background:#f8fafc;border-radius:10px">${wq.question?.content || '无题目内容'}</div>
            </div>
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px">
                <div style="padding:14px;background:#fee2e2;border-radius:10px">
                    <div style="font-size:.78em;color:#dc2626;margin-bottom:4px">上次错答</div>
                    <div style="font-size:1.1em;font-weight:600;color:#991b1b">${wq.wrong_answer}</div>
                </div>
                <div style="padding:14px;background:#dcfce7;border-radius:10px">
                    <div style="font-size:.78em;color:#16a34a;margin-bottom:4px">正确答案</div>
                    <div style="font-size:1.1em;font-weight:600;color:#166534">${wq.correct_answer}</div>
                </div>
            </div>
            
            ${wq.error_analysis ? `
            <div style="padding:14px;background:#fef3c7;border-radius:10px;margin-bottom:20px">
                <div style="font-size:.78em;color:#92400e;margin-bottom:4px">错误分析</div>
                <div style="color:#78350f">${wq.error_analysis}</div>
            </div>
            ` : ''}
            
            <div style="font-size:.85em;color:var(--text-secondary);margin-bottom:16px">这次你做对了吗？</div>
            <div style="display:flex;gap:12px">
                <button onclick="submitWrongQuestionReview(true)" style="flex:1;padding:14px;background:#10b981;color:#fff;border:none;border-radius:10px;font-weight:600;cursor:pointer;font-size:1.05em">✅ 做对了</button>
                <button onclick="submitWrongQuestionReview(false)" style="flex:1;padding:14px;background:#ef4444;color:#fff;border:none;border-radius:10px;font-weight:600;cursor:pointer;font-size:1.05em">❌ 又错了</button>
            </div>
        </div>
    </div>`;
}

// 提交复习结果
async function submitWrongQuestionReview(correct) {
    const wq = currentReviewList[currentReviewIndex];
    
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/${wq.id}/review`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                correct: correct,
                notes: correct ? '复习时做对' : '复习时仍做错'
            })
        });
        
        if (r.ok) {
            const result = await r.json();
            if (result.mastered) {
                showToast('🎉 恭喜！此错题已完全掌握');
            } else {
                showToast(correct ? '✅ 正确！继续加油' : '❌ 继续练习，下次一定能对');
            }
            
            currentReviewIndex++;
            renderWrongQuestionReview();
        }
    } catch (e) {
        console.error('Failed to submit review:', e);
        showToast('提交失败');
    }
}

// ============================================================
// 拍照上传功能
// ============================================================

let pendingUploadResult = null;

// 显示拍照上传弹窗
function showPhotoUploadModal() {
    const modal = document.createElement('div');
    modal.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000;padding:20px';
    modal.onclick = (e) => { if(e.target===modal) modal.remove(); };
    
    modal.innerHTML = `
    <div style="background:var(--surface);border-radius:16px;max-width:700px;width:100%;max-height:85vh;overflow-y:auto">
        <div style="padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
            <h3 style="font-size:1.2em;font-weight:600">📷 拍照上传错题</h3>
            <button onclick="this.closest('.modal').remove()" style="background:none;border:none;font-size:1.5em;cursor:pointer;padding:4px">×</button>
        </div>
        <div style="padding:20px">
            <div style="border:2px dashed var(--border);border-radius:12px;padding:40px;text-align:center;margin-bottom:20px;cursor:pointer" onclick="document.getElementById('photoInput').click()" id="uploadArea">
                <div style="font-size:3em;margin-bottom:12px">📷</div>
                <div style="font-weight:500;margin-bottom:8px">点击上传错题图片</div>
                <div style="font-size:.85em;color:var(--text-secondary)">支持 JPG、PNG 格式</div>
                <input type="file" id="photoInput" accept="image/*" capture="environment" style="display:none" onchange="handlePhotoSelect(this)">
            </div>
            
            <div id="previewArea" style="display:none;margin-bottom:20px">
                <img id="previewImage" style="max-width:100%;max-height:300px;border-radius:12px;border:1px solid var(--border)">
                <div style="margin-top:10px;text-align:center">
                    <button onclick="clearPhotoPreview()" style="padding:8px 16px;border:1px solid var(--border);background:var(--surface);border-radius:8px;cursor:pointer;font-size:.85em">清除图片</button>
                </div>
            </div>
            
            <div id="uploadStatus" style="display:none;padding:16px;background:#f0fdf4;border-radius:12px;margin-bottom:20px">
                <div style="display:flex;align-items:center;gap:12px">
                    <div id="uploadSpinner" style="width:20px;height:20px;border:2px solid #10b981;border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite"></div>
                    <span id="uploadStatusText">正在识别中...</span>
                </div>
            </div>
            
            <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
            
            <div id="ocrResult" style="display:none;margin-bottom:20px">
                <h4 style="font-size:1em;font-weight:600;margin-bottom:12px">🔍 识别结果</h4>
                <div id="ocrResultContent"></div>
            </div>
            
            <div style="display:flex;gap:10px;justify-content:flex-end">
                <button onclick="this.closest('.modal').remove()" style="padding:10px 20px;border:1px solid var(--border);background:var(--surface);border-radius:8px;cursor:pointer">取消</button>
                <button id="confirmSaveBtn" onclick="confirmAndSaveWrongQuestion()" style="padding:10px 20px;background:#6366f1;color:#fff;border:none;border-radius:8px;cursor:pointer;opacity:.5;pointer-events:none">保存错题</button>
            </div>
        </div>
    </div>`;
    modal.className = 'modal';
    document.body.appendChild(modal);
}

// 处理照片选择
async function handlePhotoSelect(input) {
    const file = input.files[0];
    if (!file) return;
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('previewArea').style.display = 'block';
        document.getElementById('uploadArea').style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // 显示上传状态
    document.getElementById('uploadStatus').style.display = 'block';
    document.getElementById('uploadStatusText').textContent = '正在上传并识别...';
    document.getElementById('ocrResult').style.display = 'none';
    document.getElementById('confirmSaveBtn').style.opacity = '0.5';
    document.getElementById('confirmSaveBtn').style.pointerEvents = 'none';
    
    // 上传并识别
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API}/users/${USER_ID}/wrong-questions/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('上传失败');
        }
        
        const result = await response.json();
        pendingUploadResult = result;
        
        // 显示识别结果
        document.getElementById('uploadStatus').style.display = 'none';
        document.getElementById('ocrResult').style.display = 'block';
        
        const ocrData = result.parsed || result.ocr_result || {};
        const confidence = ocrData.confidence || 0;
        
        document.getElementById('ocrResultContent').innerHTML = `
        <div style="background:#f8fafc;border-radius:10px;padding:16px">
            ${ocrData.question ? `
            <div style="margin-bottom:12px">
                <div style="font-size:.78em;color:var(--text-secondary);margin-bottom:4px">识别题目</div>
                <div style="font-weight:500">${ocrData.question}</div>
            </div>
            ` : '<div style="color:#f97316;margin-bottom:12px">⚠️ 未识别到题目，请手动输入</div>'}
            
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
                <div>
                    <div style="font-size:.78em;color:var(--text-secondary);margin-bottom:4px">识别错答</div>
                    <div style="color:#dc2626;font-weight:500">${ocrData.wrong_answer || '未识别到'}</div>
                </div>
                <div>
                    <div style="font-size:.78em;color:var(--text-secondary);margin-bottom:4px">识别正答</div>
                    <div style="color:#16a34a;font-weight:500">${ocrData.correct_answer || '未识别到'}</div>
                </div>
            </div>
            
            <div style="display:flex;justify-content:space-between;align-items:center;padding-top:12px;border-top:1px solid var(--border)">
                <div style="font-size:.78em;color:var(--text-secondary)">
                    识别置信度: <span style="font-weight:600;color:${confidence > 0.7 ? '#16a34a' : confidence > 0.4 ? '#f97316' : '#dc2626'}">${(confidence * 100).toFixed(0)}%</span>
                </div>
            </div>
        </div>`;
        
        // 启用保存按钮
        document.getElementById('confirmSaveBtn').style.opacity = '1';
        document.getElementById('confirmSaveBtn').style.pointerEvents = 'auto';
        
    } catch (error) {
        console.error('Upload error:', error);
        document.getElementById('uploadStatus').innerHTML = `
        <div style="background:#fef2f2;color:#dc2626;padding:16px;border-radius:12px">
            上传失败: ${error.message}
        </div>`;
    }
}

// 清除图片预览
function clearPhotoPreview() {
    document.getElementById('photoInput').value = '';
    document.getElementById('previewArea').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('uploadStatus').style.display = 'none';
    document.getElementById('ocrResult').style.display = 'none';
    document.getElementById('confirmSaveBtn').style.opacity = '0.5';
    document.getElementById('confirmSaveBtn').style.pointerEvents = 'none';
    pendingUploadResult = null;
}

// 确认并保存错题
async function confirmAndSaveWrongQuestion() {
    if (!pendingUploadResult) {
        showToast('请先上传图片');
        return;
    }
    
    const ocrData = pendingUploadResult.parsed || {};
    
    // 显示编辑弹窗，预先填充识别结果
    const modal = document.createElement('div');
    modal.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:2000;padding:20px';
    modal.onclick = (e) => { if(e.target===modal) modal.remove(); };
    
    modal.innerHTML = `
    <div style="background:var(--surface);border-radius:16px;max-width:600px;width:100%;max-height:85vh;overflow-y:auto">
        <div style="padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
            <h3 style="font-size:1.2em;font-weight:600">确认并保存错题</h3>
            <button onclick="this.closest('.modal').remove()" style="background:none;border:none;font-size:1.5em;cursor:pointer;padding:4px">×</button>
        </div>
        <div style="padding:20px">
            <div style="margin-bottom:16px">
                <img src="${pendingUploadResult.image_url}" style="max-width:100%;max-height:150px;border-radius:8px;border:1px solid var(--border)">
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">知识点</label>
                <select id="wqNodeId" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px">
                    <option value="">选择知识点...</option>
                    ${allNodes.slice(0, 100).map(n => `<option value="${n.id}">${n.name?.zh || n.id}</option>`).join('')}
                </select>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">题目内容</label>
                <textarea id="wqContent" rows="3" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;resize:vertical">${ocrData.question || ''}</textarea>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
                <div>
                    <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">你的答案</label>
                    <input type="text" id="wqWrongAnswer" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px" value="${ocrData.wrong_answer || ''}">
                </div>
                <div>
                    <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">正确答案</label>
                    <input type="text" id="wqCorrectAnswer" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px" value="${ocrData.correct_answer || ''}">
                </div>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">错误类型</label>
                <select id="wqErrorType" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px">
                    <option value="">选择错误类型...</option>
                    <option value="concept_error">概念理解错误</option>
                    <option value="calculation_error">计算错误</option>
                    <option value="formula_error">公式记错</option>
                    <option value="misunderstanding">审题错误</option>
                    <option value="careless" selected>粗心大意</option>
                    <option value="wrong_approach">思路错误</option>
                    <option value="confusion">知识点混淆</option>
                    <option value="other">其他</option>
                </select>
            </div>
            <div style="margin-bottom:16px">
                <label style="display:block;font-size:.85em;font-weight:500;margin-bottom:6px">错误分析</label>
                <textarea id="wqErrorAnalysis" rows="2" style="width:100%;padding:10px;border:1px solid var(--border);border-radius:8px;resize:vertical" placeholder="分析错误原因..."></textarea>
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end">
                <button onclick="this.closest('.modal').remove()" style="padding:10px 20px;border:1px solid var(--border);background:var(--surface);border-radius:8px;cursor:pointer">取消</button>
                <button onclick="saveWrongQuestionWithImage('${pendingUploadResult.image_id}')" style="padding:10px 20px;background:#6366f1;color:#fff;border:none;border-radius:8px;cursor:pointer">保存</button>
            </div>
        </div>
    </div>`;
    modal.className = 'modal';
    document.body.appendChild(modal);
    
    // 关闭上传弹窗
    document.querySelectorAll('.modal')[0]?.remove();
}

// 保存带图片的错题
async function saveWrongQuestionWithImage(imageId) {
    const nodeId = document.getElementById('wqNodeId')?.value;
    const content = document.getElementById('wqContent')?.value;
    const wrongAnswer = document.getElementById('wqWrongAnswer')?.value;
    const correctAnswer = document.getElementById('wqCorrectAnswer')?.value;
    const errorType = document.getElementById('wqErrorType')?.value;
    const errorAnalysis = document.getElementById('wqErrorAnalysis')?.value;
    
    if (!content) {
        showToast('请填写题目内容');
        return;
    }
    
    const data = {
        node_id: nodeId || 'unknown',
        question: {
            content: content,
            type: 'calculation',
            difficulty: 5,
            source: 'photo_upload'
        },
        wrong_answer: wrongAnswer,
        correct_answer: correctAnswer,
        error_type: errorType || 'other',
        error_analysis: errorAnalysis,
        tags: ['拍照上传']
    };
    
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (r.ok) {
            const result = await r.json();
            
            // 关联图片
            if (imageId) {
                await fetch(`${API}/users/${USER_ID}/wrong-questions/images/${imageId}/link`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({wrong_question_id: result.wrong_question_id})
                });
            }
            
            showToast('错题已保存');
            document.querySelectorAll('.modal').forEach(m => m.remove());
            await renderWrongQuestionsPage();
        } else {
            showToast('保存失败');
        }
    } catch (e) {
        console.error('Failed to save wrong question:', e);
        showToast('保存失败');
    }
}

// 加载错题图片
async function loadWrongQuestionImages(wqId) {
    try {
        const r = await fetch(`${API}/users/${USER_ID}/wrong-questions/images?wq_id=${wqId}`);
        const data = await r.json();
        return data.images || [];
    } catch (e) {
        console.error('Failed to load images:', e);
        return [];
    }
}

// 显示错题图片
function showWrongQuestionImages(wqId, containerId) {
    loadWrongQuestionImages(wqId).then(images => {
        const container = document.getElementById(containerId);
        if (!container || images.length === 0) return;
        
        container.innerHTML = `
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
            ${images.map(img => `
                <div style="position:relative;width:80px;height:80px">
                    <img src="${img.thumbnail_url || img.image_url}" 
                         style="width:100%;height:100%;object-fit:cover;border-radius:8px;cursor:pointer;border:1px solid var(--border)"
                         onclick="showImageViewer('${img.image_url}')">
                    <button onclick="deleteWrongQuestionImage('${img.id}', '${wqId}')" 
                            style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#ef4444;color:#fff;border:none;border-radius:50%;font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center">×</button>
                </div>
            `).join('')}
        </div>`;
    });
}

// 图片查看器
function showImageViewer(imageUrl) {
    const viewer = document.createElement('div');
    viewer.style = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.9);display:flex;align-items:center;justify-content:center;z-index:3000;cursor:zoom-out';
    viewer.onclick = () => viewer.remove();
    viewer.innerHTML = `
    <img src="${imageUrl}" style="max-width:95%;max-height:95%;object-fit:contain;border-radius:8px">
    <button onclick="this.parentElement.remove()" style="position:absolute;top:20px;right:20px;width:40px;height:40px;background:rgba(255,255,255,.2);color:#fff;border:none;border-radius:50%;font-size:20px;cursor:pointer">×</button>`;
    document.body.appendChild(viewer);
}

// 删除错题图片
async function deleteWrongQuestionImage(imageId, wqId) {
    if (!confirm('确定要删除这张图片吗？')) return;
    
    try {
        await fetch(`${API}/users/${USER_ID}/wrong-questions/images/${imageId}`, {method: 'DELETE'});
        showWrongQuestionImages(wqId, `wq-images-${wqId}`);
        showToast('图片已删除');
    } catch (e) {
        console.error('Failed to delete image:', e);
        showToast('删除失败');
    }
}

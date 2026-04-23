async function renderWrongQuestionsPage(){
    document.getElementById('mainContent').innerHTML = `
        <div style="padding:20px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
                <h2 style="margin:0">📚 错题本</h2>
                <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                    <select id="wqFilter" onchange="wqCurrentPage=1;renderWrongQuestionsList()" style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);font-size:.9em;background:var(--surface)">
                        <option value="all">全部</option>
                        <option value="active">未掌握</option>
                        <option value="needs_review">待复习</option>
                        <option value="mastered">已掌握</option>
                    </select>
                    <button onclick="openWQUpload()" style="padding:8px 16px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;cursor:pointer;font-weight:500;font-size:.9em">
                        📷 上传错题图片
                    </button>
                </div>
            </div>
            <div id="wqStats" style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px"></div>
            <div id="wqList"></div>
            <div id="wqPagination" style="display:flex;justify-content:center;gap:6px;margin-top:20px;flex-wrap:wrap"></div>
        </div>
        <div id="wqUploadModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:1000;align-items:center;justify-content:center;padding:20px">
            <div style="background:var(--surface);border-radius:16px;padding:28px;max-width:500px;width:100%">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
                    <h3 style="margin:0">📷 上传错题图片</h3>
                    <button onclick="closeWQUpload()" style="background:none;border:none;font-size:1.4em;cursor:pointer;color:var(--text-secondary)">×</button>
                </div>
                <div id="wqUploadDrop" style="border:2px dashed var(--border);border-radius:12px;padding:40px;text-align:center;cursor:pointer;transition:all .2s" onclick="document.getElementById('wqUploadInput').click()" ondragover="event.preventDefault();this.style.borderColor='#6366f1'" ondrop="handleWQDrop(event)" ondragleave="this.style.borderColor='var(--border)'">
                    <div style="font-size:2.5em;margin-bottom:12px">📷</div>
                    <div style="color:var(--text-secondary);font-size:.9em">点击上传或拖拽图片到这里</div>
                    <div style="color:#94a3b8;font-size:.8em;margin-top:6px">支持 JPG/PNG/PDF</div>
                </div>
                <input type="file" id="wqUploadInput" accept="image/*" multiple style="display:none" onchange="handleWQUploadFiles(this.files)">
                <div id="wqUploadPreview" style="margin-top:16px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px"></div>
                <div id="wqUploadStatus" style="margin-top:12px;font-size:.85em;color:var(--text-secondary);min-height:20px"></div>
                <div style="margin-top:16px;display:flex;gap:10px">
                    <button onclick="closeWQUpload()" style="flex:1;padding:12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);cursor:pointer">取消</button>
                    <button id="wqSaveBtn" onclick="saveWQWithImages()" style="flex:1;padding:12px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;cursor:pointer;font-weight:600">保存错题</button>
                </div>
            </div>
        </div>
        <div id="wqImgModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:1000;align-items:center;justify-content:center;cursor:pointer" onclick="this.style.display='none'">
            <img id="wqImgFull" style="max-width:90vw;max-height:90vh;border-radius:12px">
        </div>
    `;
    await renderWrongQuestionsList();
}

let wqCurrentPage = 1;
let wqAllData = [];
let wqUploadFiles = [];

function openWQUpload(){
    document.getElementById('wqUploadModal').style.display='flex';
    wqUploadFiles = [];
    document.getElementById('wqUploadPreview').innerHTML='';
    document.getElementById('wqUploadStatus').innerHTML='';
}
function closeWQUpload(){
    document.getElementById('wqUploadModal').style.display='none';
}
function handleWQDrop(e){
    e.preventDefault();
    e.target.style.borderColor='var(--border)';
    handleWQUploadFiles(e.dataTransfer.files);
}
function handleWQUploadFiles(files){
    for(const f of files){
        if(!f.type.startsWith('image/')) continue;
        wqUploadFiles.push(f);
        const reader = new FileReader();
        reader.onload = e => {
            const div = document.createElement('div');
            div.style.cssText='position:relative;border-radius:8px;overflow:hidden;aspect-ratio:1';
            div.innerHTML='<img src="'+e.target.result+'" style="width:100%;height:100%;object-fit:cover"><button onclick="this.parentElement.remove();removeWQFile(\''+f.name+'\')" style="position:absolute;top:4px;right:4px;background:rgba(0,0,0,.6);border:none;color:#fff;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:.8em;line-height:1">×</button>';
            document.getElementById('wqUploadPreview').appendChild(div);
        };
        reader.readAsDataURL(f);
    }
    document.getElementById('wqUploadStatus').innerHTML='已选择 '+wqUploadFiles.length+' 张图片';
}
function removeWQFile(name){wqUploadFiles=wqUploadFiles.filter(f=>f.name!==name)}

async function saveWQWithImages(){
    if(!wqUploadFiles.length){alert('请先上传至少一张图片');return;}
    const btn = document.getElementById('wqSaveBtn');
    btn.disabled=true; btn.innerText='上传中...';
    document.getElementById('wqUploadStatus').innerHTML='正在上传...';
    try {
        const uploaded = [];
        for(const f of wqUploadFiles){
            const fd = new FormData();
            fd.append('file', f);
            const r = await fetch(API+'/users/'+USER_ID+'/wq-upload', {method:'POST', body:fd});
            if(r.ok){
                const d = await r.json();
                uploaded.push(d.image_id);
            }
        }
        document.getElementById('wqUploadStatus').innerHTML='✅ 上传成功！已上传 '+uploaded.length+' 张图片';
        btn.innerText='完成'; btn.disabled=false;
        setTimeout(()=>{closeWQUpload();renderWrongQuestionsList();},1200);
    } catch(e){
        document.getElementById('wqUploadStatus').innerHTML='❌ 上传失败：'+e.message;
        btn.disabled=false; btn.innerText='保存错题';
    }
}

async function renderWrongQuestionsList(){
    const list = document.getElementById('wqList');
    const statsEl = document.getElementById('wqStats');
    const filter = document.getElementById('wqFilter').value;
    let url = API+'/users/'+USER_ID+'/wrong-questions?limit=100';
    const [statsRes, listRes] = await Promise.all([
        fetch(API+'/users/'+USER_ID+'/wrong-questions/stats').catch(()=>null),
        fetch(url).catch(()=>null)
    ]);
    const stats = statsRes?await statsRes.json():{};
    const data = listRes?await listRes.json():{};
    let wqs = data.wrong_questions||[];
    
    // 过滤
    if(filter==='active') wqs=wqs.filter(w=>!w.review_schedule?.mastered);
    else if(filter==='needs_review') wqs=wqs.filter(w=>{const n=w.review_schedule?.next_review;return n&&new Date(n)<=new Date()&&!w.review_schedule?.mastered;});
    else if(filter==='mastered') wqs=wqs.filter(w=>w.review_schedule?.mastered);
    
    wqAllData = wqs.slice().reverse(); // 最新优先（倒序）
    wqCurrentPage = Math.min(wqCurrentPage, Math.ceil(wqAllData.length/WQ_PAGE_SIZE)||1);
    renderWQPage(wqCurrentPage);
    
    statsEl.innerHTML = '<div style="background:linear-gradient(135deg,#ef4444,#f87171);color:#fff;padding:16px;border-radius:12px;text-align:center"><div style="font-size:2em;font-weight:700">'+(stats.total_wrong||stats.total_count||0)+'</div><div style="font-size:.85em;opacity:.9">错题总数</div></div>'+
        '<div style="background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#fff;padding:16px;border-radius:12px;text-align:center"><div style="font-size:2em;font-weight:700">'+(stats.active||stats.active_count||0)+'</div><div style="font-size:.85em;opacity:.9">未掌握</div></div>'+
        '<div style="background:linear-gradient(135deg,#8b5cf6,#a78bfa);color:#fff;padding:16px;border-radius:12px;text-align:center"><div style="font-size:2em;font-weight:700">'+(stats.needs_review_today||0)+'</div><div style="font-size:.85em;opacity:.9">待复习</div></div>'+
        '<div style="background:linear-gradient(135deg,#10b981,#34d399);color:#fff;padding:16px;border-radius:12px;text-align:center"><div style="font-size:2em;font-weight:700">'+(stats.mastered||stats.mastered_count||0)+'</div><div style="font-size:.85em;opacity:.9">已掌握</div></div>';
}

function renderWQPage(page){
    const list = document.getElementById('wqList');
    const total = Math.ceil(wqAllData.length/WQ_PAGE_SIZE)||1;
    const start = (page-1)*WQ_PAGE_SIZE;
    const pageWQs = wqAllData.slice(start, start+WQ_PAGE_SIZE);
    
    if(!pageWQs.length){
        list.innerHTML='<div style="text-align:center;padding:60px 20px;color:var(--text-secondary)"><div style="font-size:3em;margin-bottom:12px">✅</div><div>暂无错题</div></div>';
        document.getElementById('wqPagination').innerHTML='';
        return;
    }
    
    list.innerHTML = pageWQs.map(wq => {
        const q = wq.question||{};
        const content = q.content||'';
        const grade = wq._grade||'';
        const concept = wq._concept||'';
        const errors = wq._common_errors||[];
        const mastered = wq.review_schedule&&wq.review_schedule.mastered;
        const stage = wq.review_schedule?wq.review_schedule.stage:1;
        const reviewCount = wq.review_schedule?wq.review_schedule.review_count:0;
        const errorTypeLabel = (ERROR_TYPES||{})[wq.error_type]||wq.error_type||'其他';
        const priority = wq._review_priority||'medium';
        const borderColor = mastered?'#10b981':priority==='high'?'#ef4444':'#f59e0b';
        const images = (wq.wrong_question_images||[]);
        const ansCorrect = (wq.correct_answer||'').replace(/</g,'&lt;').slice(0,300);
        const ansWrong = (wq.wrong_answer||'—').replace(/</g,'&lt;');
        const imgGallery = images.length?'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">'+
            images.map(img=>'<img src="'+API+'/users/'+USER_ID+'/wrong-question-images/'+img.id+'/thumb" style="width:72px;height:72px;object-fit:cover;border-radius:8px;cursor:pointer;border:2px solid #e2e8f0" onclick="document.getElementById(\x27wqImgFull\x27).src=this.src;document.getElementById(\x27wqImgModal\x27).style.display=\'flex\x27" onerror="this.style.display=\'none\x27">').join('')+
            '<button onclick="uploadImgForWQ(\''+wq.id+'\')" style="width:72px;height:72px;border-radius:8px;border:2px dashed #cbd5e0;background:#f8fafc;cursor:pointer;font-size:1.8em;color:#94a3b8;display:flex;align-items:center;justify-content:center">+</button>'+
            '</div>':'<div style="margin-bottom:12px"><button onclick="uploadImgForWQ(\''+wq.id+'\')" style="padding:8px 16px;border-radius:8px;border:1px dashed var(--border);background:#f8fafc;cursor:pointer;font-size:.85em;color:#64748b">📷 添加图片</button></div>';
        return '<div style="background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;border-left:4px solid '+borderColor+'">'+
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;flex-wrap:wrap;gap:8px">'+
                '<div>'+
                    '<span style="background:'+(mastered?'#dcfce7':'#fef2f2')+';color:'+(mastered?'#16a34a':'#dc2626')+';padding:3px 10px;border-radius:20px;font-size:.8em;font-weight:600;margin-right:6px">'+(mastered?'✅ 已掌握':stage+'轮复习')+'</span>'+
                    (grade?'<span style="background:#f1f5f9;color:#64748b;padding:3px 10px;border-radius:20px;font-size:.8em;margin-right:6px">'+grade+'</span>':'')+
                    '<span style="background:#ede9fe;color:#7c3aed;padding:3px 10px;border-radius:20px;font-size:.8em">'+errorTypeLabel+'</span>'+
                '</div>'+
                '<div style="font-size:.8em;color:#94a3b8">复习 '+reviewCount+' 次</div>'+
            '</div>'+
            '<div style="font-size:1em;font-weight:600;color:var(--text);margin-bottom:8px">'+(concept||'未分类')+'</div>'+
            imgGallery+
            '<div style="font-size:.9em;line-height:1.7;color:var(--text-secondary);background:#f8fafc;padding:14px;border-radius:10px;margin-bottom:14px;white-space:pre-wrap;max-height:150px;overflow-y:auto">'+
                content.replace(/</g,'&lt;')+'</div>'+
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">'+
                '<div><div style="font-size:.8em;color:#64748b;margin-bottom:4px">❌ 错误答案</div><div style="background:#fef2f2;color:#dc2626;padding:10px;border-radius:8px;font-size:.9em">'+ansWrong+'</div></div>'+
                '<div><div style="font-size:.8em;color:#64748b;margin-bottom:4px">✅ 正确答案</div><div style="background:#f0fdf4;color:#16a34a;padding:10px;border-radius:8px;font-size:.9em;white-space:pre-wrap">'+ansCorrect+'</div></div>'+
            '</div>'+
            (errors.length?'<div style="margin-bottom:14px"><div style="font-size:.8em;color:#64748b;margin-bottom:6px">⚠️ 易错提醒</div><div style="display:flex;flex-wrap:wrap;gap:6px">'+
                errors.map(e=>'<span style="background:#fff7ed;color:#c2410c;padding:4px 10px;border-radius:20px;font-size:.8em;border:1px solid #fed7aa">'+e.replace(/</g,'&lt;')+'</span>').join('')+'</div></div>':'')+
            (wq.error_analysis?'<div style="margin-bottom:14px"><div style="font-size:.8em;color:#64748b;margin-bottom:4px">💡 关键点</div><div style="color:#7c3aed;font-size:.9em;padding:10px;background:#f5f3ff;border-radius:8px">'+wq.error_analysis.replace(/</g,'&lt;')+'</div></div>':'')+
            '<div style="display:flex;gap:10px;flex-wrap:wrap">'+
                '<button onclick="reviewWQ(\''+wq.id+'\')" style="flex:1;padding:10px;border-radius:8px;border:1px solid var(--border);background:var(--bg);cursor:pointer;font-weight:500;font-size:.9em">🎯 复习这道题</button>'+
                (mastered?
                    '<button onclick="unmarkWQMastered(\''+wq.id+'\')" style="flex:1;padding:10px;border-radius:8px;border:1px solid #94a3b8;background:#f8fafc;color:#64748b;cursor:pointer;font-size:.9em">🔄 取消掌握</button>':
                    '<button onclick="markWQMastered(\''+wq.id+'\')" style="flex:1;padding:10px;border-radius:8px;border:1px solid #10b981;background:#f0fdf4;color:#16a34a;cursor:pointer;font-weight:500;font-size:.9em">✅ 标记已掌握</button>'
                )+
                '<button onclick="deleteWQ(\''+wq.id+'\')" style="padding:10px 16px;border-radius:8px;border:1px solid #fca5a5;background:#fef2f2;color:#dc2626;cursor:pointer;font-size:.9em">🗑️</button>'+
            '</div></div>';
    }).join('');
    
    // 分页按钮
    const totalPages = Math.ceil(wqAllData.length/WQ_PAGE_SIZE)||1;
    let pBtns = '';
    if(totalPages>1){
        pBtns += '<button onclick="wqGoPage('+(page-1)+')" '+(page<=1?'disabled':'')+' style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--surface);cursor:'+(page<=1?'not-allowed':'pointer')+';opacity:'+(page<=1?.5:1)+'">‹ 上一页</button>';
        const maxBtns=5, start=Math.max(1,page-Math.floor(maxBtns/2)), end=Math.min(totalPages,start+maxBtns-1);
        for(let i=start;i<=end;i++) pBtns+='<button onclick="wqGoPage('+i+')" style="padding:8px 14px;border-radius:8px;border:1px solid '+(i===page?'#6366f1':'var(--border)')+';background:'+(i===page?'#6366f1':'var(--surface)')+';color:'+(i===page?'#fff':'var(--text)')+';cursor:pointer;font-weight:'+(i===page?600:400)+'">'+i+'</button>';
        pBtns += '<button onclick="wqGoPage('+(page+1)+')" '+(page>=totalPages?'disabled':'')+' style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--surface);cursor:'+(page>=totalPages?'not-allowed':'pointer')+';opacity:'+(page>=totalPages?.5:1)+'">下一页 ›</button>';
        pBtns += '<span style="padding:8px 12px;font-size:.85em;color:var(--text-secondary)">'+page+'/'+totalPages+'页 共'+wqAllData.length+'条</span>';
    }
    document.getElementById('wqPagination').innerHTML=pBtns;
}

function wqGoPage(p){
    const total=Math.ceil(wqAllData.length/WQ_PAGE_SIZE)||1;
    wqCurrentPage=Math.max(1,Math.min(p,total));
    renderWQPage(wqCurrentPage);
}

let wqUploadForId = null;
function uploadImgForWQ(wqId){
    wqUploadForId = wqId;
    const inp = document.createElement('input');
    inp.type='file'; inp.accept='image/*'; inp.multiple=true;
    inp.onchange = async e => {
        const files = Array.from(e.target.files);
        for(const f of files){
            const fd = new FormData();
            fd.append('file', f);
            const r = await fetch(API+'/users/'+USER_ID+'/wq-upload', {method:'POST', body:fd});
            if(r.ok){
                const d = await r.json();
                // 关联到错题
                // TODO: 如果需要关联图片到错题，取消下面的注释
                // await fetch(API+'/users/'+USER_ID+'/wq-images', {
                //     method:'POST', headers:{'Content-Type':'application/json'},
                //     body:JSON.stringify({wrong_question_id: wqId, image_url: d.url})
                // });
            }
        }
        renderWrongQuestionsList();
    };
    inp.click();
}

async function reviewWQ(wqId){
    const correct = confirm('你做对了吗？\n\n确定 = 做对了（推进复习）\n取消 = 做错了（继续复习）');
    try {
        await fetch(API+'/users/'+USER_ID+'/wrong-questions/'+wqId+'/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({correct,notes:''})});
        if(correct) await fetch(API+'/users/'+USER_ID+'/wrong-questions/'+wqId+'/master',{method:'POST'}).catch(()=>{});
        await renderWrongQuestionsList();
    } catch(e){alert('操作失败');}
}

async function markWQMastered(wqId){
    try {await fetch(API+'/users/'+USER_ID+'/wrong-questions/'+wqId+'/master',{method:'POST'});await renderWrongQuestionsList();} catch(e){alert('操作失败');}
}

async function unmarkWQMastered(wqId){
    try {await fetch(API+'/users/'+USER_ID+'/wrong-questions/'+wqId+'/master',{method:'DELETE'}).catch(()=>{});await renderWrongQuestionsList();} catch(e){alert('操作失败');}
}

async function deleteWQ(wqId){
    if(!confirm('确定删除这条错题？')) return;
    try {await fetch(API+'/users/'+USER_ID+'/wrong-questions/'+wqId,{method:'DELETE'});await renderWrongQuestionsList();} catch(e){alert('删除失败');}
}


function renderGraphPage(){
    document.getElementById('mainContent').innerHTML=`
    <div class="graph-wrap">
        <div class="graph-toolbar">
            <div style="display:flex;gap:5px">
                <button class="mini-btn${graphMode==='all'?' active':''}" onclick="setGraphMode('all')">全局</button>
                <button class="mini-btn${graphMode==='grade'?' active':''}" onclick="setGraphMode('grade')">按年级</button>
                <button class="mini-btn${graphMode==='branch'?' active':''}" onclick="setGraphMode('branch')">按分支</button>
            </div>
            <button class="mini-btn" onclick="resetGraph()">🔄 重置</button>
            <span id="graphFocusLabel" style="display:none;font-size:.82em;padding:4px 10px;background:#fce7f3;color:#db2777;border-radius:20px;font-weight:500"></span>
            <button class="mini-btn" onclick="graphZoom(1.3)">➕ 放大</button>
            <button class="mini-btn" onclick="graphZoom(0.7)">➖ 缩小</button>
        </div>
        <div class="graph-container">
            <div class="graph-info" id="graphInfo">节点: <strong id="graphNodeCount">0</strong> / 边: <strong id="graphEdgeCount">0</strong></div>
            <div class="graph-legend" id="graphLegend"></div>
            <svg id="graphSvg" style="width:100%;height:100%"></svg>
            <div class="graph-tooltip" id="graphTooltip" style="display:none"></div>
        </div>
    </div>`;
    renderGraph();
}

function setGraphMode(m){graphMode=m;renderGraph();}

function renderGraph(){
    // getPrereqIds 已移至全局作用域 (index.html 顶部)
    const svgEl=document.getElementById('graphSvg');
    if(!svgEl)return;
    const container=svgEl.parentElement;
    const W=container.clientWidth,H=container.clientHeight;
    const svg=d3.select(svgEl).attr('width',W).attr('height',H);
    svg.selectAll('*').remove();
    if(currentSimulation){currentSimulation.stop();currentSimulation=null}

    // 准备数据
    let displayCount, nodes;
    
    // 如果有聚焦节点，显示该节点及其关联知识（最多50个）
    if(graphFocusNodeId){
        const focusNode=allNodes.find(n=>n.id===graphFocusNodeId);
        if(!focusNode){graphFocusNodeId=null;renderGraph();return}
        
        const neighborIds=new Set([graphFocusNodeId]);
        // 加入前置知识
        (getPrereqIds(focusNode.prerequisites)||[]).forEach(pid=>neighborIds.add(pid));
        // 加入后续知识
        allNodes.forEach(n=>{if(getPrereqIds(n.prerequisites).includes(graphFocusNodeId))neighborIds.add(n.id)});
        // 限制邻居节点数
        const allNeighborIds=[...neighborIds];
        nodes=allNodes.filter(n=>neighborIds.has(n.id)).slice(0,50).map(n=>({...n,rid:n.id,isFocus:n.id===graphFocusNodeId}));
        displayCount=nodes.length;
    } else {
        displayCount=Math.min(filteredNodes.length,500);
        nodes=filteredNodes.slice(0,displayCount).map(n=>({...n,rid:n.id,isFocus:false}));
    }
    const nodeIds=new Set(nodes.map(n=>n.rid));

    // 建立边的双向映射
    const links=[];
    const outLinks=new Map(); // source -> [targets]
    inLinks=new Map();  // target -> [sources] (全局变量)
    nodes.forEach(n=>{
        if(n.prerequisites)for(const p of getPrereqIds(n.prerequisites)){
            if(nodeIds.has(p)){
                links.push({source:p,target:n.id});
                outLinks.set(p,(outLinks.get(p)||[]).concat([n.id]));
                inLinks.set(n.id,(inLinks.get(n.id)||[]).concat([p]));
            }
        }
    });

    // 对只显示子节点但父节点不在的情况，创建聚合边(虚拟根)
    const virtualNodes=[];
    const virtualRootId='_vr_';
    let virtualCount=0;
    const prereqsOutside=new Map(); // nid -> count of outside prereqs
    nodes.forEach(n=>{
        const prereqs=getPrereqIds(n.prerequisites)||[];
        const outside=prereqs.filter(p=>!nodeIds.has(p));
        if(outside.length>0){
            virtualCount++;
            prereqsOutside.set(n.id, outside.length);
            if(!nodeIds.has(virtualRootId)){
                virtualNodes.push({rid:virtualRootId,name:{zh:'前置知识'},branch:n.branch,tags:n.tags,level:n.level,difficulty:1,importance:1,isVirtual:true});
                nodeIds.add(virtualRootId);
            }
            links.push({source:virtualRootId,target:n.id,isVirtual:true});
        }
    });

    document.getElementById('graphNodeCount').textContent=nodes.length+virtualNodes.length;
    // 显示/隐藏聚焦标签
    const focusLabel=document.getElementById('graphFocusLabel');
    if(graphFocusNodeId){
        const fn=allNodes.find(n=>n.id===graphFocusNodeId);
        focusLabel.textContent='🎯 聚焦: '+(fn?.name?.zh||graphFocusNodeId);
        focusLabel.style.display='inline-block';
    } else {
        focusLabel.style.display='none';
    }
    document.getElementById('graphEdgeCount').textContent=links.length;

    // 节点颜色
    function nodeColor(d){
        if(d.isVirtual)return '#e2e8f0';
        // 聚焦节点高亮
        if(d.isFocus)return '#db2777';
        if(graphMode==='grade'){
            const g=d.tags&&d.tags.find(t=>GRADE_COLOR[t]);
            return g?GRADE_COLOR[g]:'#94a3b8';
        } else if(graphMode==='branch'){
            const colors={arithmetic:'#10b981',algebra:'#6366f1',geometry:'#f59e0b',analysis:'#ef4444',probability:'#8b5cf6',statistics:'#06b6d4',discrete:'#84cc16',number_theory:'#ec4899',logic:'#14b8a6',topology:'#f97316',other:'#94a3b8',
            // 中文分支
            '小学数学':'#f97316','高等数学':'#ef4444','拓扑学':'#f97316','图论':'#84cc16','博弈论':'#ec4899','范畴论':'#14b8a6','随机过程':'#8b5cf6','算术':'#10b981','控制论':'#06b6d4','线性代数':'#6366f1','复分析':'#ef4444','概率论':'#8b5cf6','统计学':'#06b6d4','组合数学':'#84cc16','离散数学':'#84cc16','逻辑学':'#14b8a6','优化理论':'#f59e0b','动力系统':'#f97316','数值分析':'#ef4444','偏微分方程':'#ef4444','集合论':'#14b8a6','三角学':'#f59e0b','数论':'#ec4899','泛函分析':'#ef4444','微分几何':'#f59e0b','抽象代数':'#6366f1',
            // 详细分支
            '抽象代数(详细)':'#8b5cf6','微分几何(详细)':'#8b5cf6','复分析(详细)':'#8b5cf6',
            // 英文分支
            'functional_analysis':'#ef4444','differential_geometry':'#f59e0b','abstract_algebra':'#6366f1','category_theory':'#14b8a6','stochastic_processes':'#8b5cf6','graph_theory':'#84cc16','game_theory':'#ec4899','control_theory':'#06b6d4'};
            return colors[d.branch]||'#94a3b8';
        }
        const known=userKnowledge[d.id]?.status==='known';
        return known?'#10b981':'#cbd5e0';
    }

    // 图例
    const legendEl=document.getElementById('graphLegend');
    if(graphMode==='grade'){
        legendEl.innerHTML=GRADE_LEVELS.slice(1).map(g=>`<div class="legend-row"><div class="legend-circle" style="background:${g.color}"></div><span>${g.name}</span></div>`).join('');
    } else if(graphMode==='branch'){
        const used=new Set(nodes.map(n=>n.branch));
        legendEl.innerHTML=Object.entries(BRANCH_NAMES).filter(([k])=>used.has(k)).map(([k,v])=>`<div class="legend-row"><div class="legend-circle" style="background:${{arithmetic:'#10b981',algebra:'#6366f1',geometry:'#f59e0b',analysis:'#ef4444',probability:'#8b5cf6',statistics:'#06b6d4',discrete:'#84cc16',number_theory:'#ec4899',logic:'#14b8a6',topology:'#f97316',other:'#94a3b8','小学数学':'#f97316','高等数学':'#ef4444','拓扑学':'#f97316','图论':'#84cc16','博弈论':'#ec4899','范畴论':'#14b8a6','随机过程':'#8b5cf6','算术':'#10b981','控制论':'#06b6d4','线性代数':'#6366f1','复分析':'#ef4444','概率论':'#8b5cf6','统计学':'#06b6d4','组合数学':'#84cc16','离散数学':'#84cc16','逻辑学':'#14b8a6','优化理论':'#f59e0b','动力系统':'#f97316','数值分析':'#ef4444','偏微分方程':'#ef4444','集合论':'#14b8a6','三角学':'#f59e0b','数论':'#ec4899','泛函分析':'#ef4444','微分几何':'#f59e0b','抽象代数':'#6366f1','抽象代数(详细)':'#8b5cf6','微分几何(详细)':'#8b5cf6','复分析(详细)':'#8b5cf6','functional_analysis':'#ef4444','differential_geometry':'#f59e0b','abstract_algebra':'#6366f1','category_theory':'#14b8a6','stochastic_processes':'#8b5cf6','graph_theory':'#84cc16','game_theory':'#ec4899','control_theory':'#06b6d4'}[k]||'#94a3b8'}"></div><span>${v}</span></div>`).join('');
    } else {
        legendEl.innerHTML=`<div class="legend-row"><div class="legend-circle" style="background:#10b981"></div><span>已掌握</span></div><div class="legend-row"><div class="legend-circle" style="background:#cbd5e0"></div><span>未同步</span></div>`;
    }

    const allGraphNodes=[...nodes,...virtualNodes];
    const sim=d3.forceSimulation(allGraphNodes)
        .force('link',d3.forceLink(links).id(n=>n.rid).distance(d=>d.isVirtual?20:(d.source.branch===d.target.branch?40:60)).strength(d=>d.isVirtual?0.1:0.5))
        .force('charge',d3.forceManyBody().strength(-200))
        .force('center',d3.forceCenter(W/2,H/2))
        .force('collision',d3.forceCollide().radius(16))
        .force('x',d3.forceX(W/2).strength(0.03))
        .force('y',d3.forceY(H/2).strength(0.03));

    const g=svg.append('g');
    svg.call(d3.zoom().scaleExtent([.2,3]).on('zoom',e=>g.attr('transform',e.transform)));

    const link=g.append('g').selectAll('line').data(links).enter().append('line').attr('class','graph-link').attr('stroke-width',d=>d.isVirtual?0.5:1).attr('stroke',d=>d.isVirtual?'#94a3b8':'#cbd5e0').attr('stroke-opacity',d=>d.isVirtual?0.2:0.4);
    const node=g.append('g').selectAll('g').data(allGraphNodes).enter().append('g').attr('class','graph-node').call(d3.drag().on('start',function(e,d){if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on('drag',function(e,d){d.fx=e.x;d.fy=d.y}).on('end',function(e,d){if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}));

    node.append('circle').attr('r',d=>d.isVirtual?4:(userKnowledge[d.id]?.status==='known'?9:7)).attr('fill',nodeColor).attr('stroke',d=>d.isVirtual?'none':'#fff').attr('stroke-width',d=>d.isVirtual?0:2);
    node.append('text').attr('dx',11).attr('dy',4).text(d=>d.isVirtual?`前置(+${prereqsOutside.get(d.rid)||0})`:(d.name?.zh||d.name||'').substring(0,8)).attr('font-size',d=>d.isVirtual?'7px':'9px').attr('fill',d=>d.isVirtual?'#94a3b8':'#64748b').attr('font-style',d=>d.isVirtual?'italic':'normal');

    const tip=document.getElementById('graphTooltip');
    node.on('mouseover',function(event,d){
        const gtag=d.tags&&d.tags.find(t=>GRADE_COLOR[t])||'未分类';
        const known=userKnowledge[d.id]?.status==='known';
        tip.style.display='block';tip.style.left=(event.clientX+12)+'px';tip.style.top=(event.clientY-10)+'px';
        tip.innerHTML=`<div class="graph-tooltip-title">${d.name?.zh||d.name||''}</div><div class="graph-tooltip-meta">${gtag} · ${d.branch?(BRANCH_NAMES[d.branch]||d.branch):'其他'}<br>难度: ${d.difficulty}/10 · ${known?'✅ 已掌握':'⚪ 未同步'}</div>`;
    }).on('mousemove',function(event){tip.style.left=(event.clientX+12)+'px';tip.style.top=(event.clientY-10)+'px'}).on('mouseout',function(){tip.style.display='none'}).on('click',function(d){openDetail(d.id)});

    sim.on('tick',()=>{
        link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
        node.attr('transform',d=>`translate(${d.x},${d.y})`);
    });
    currentSimulation=sim;
}

function resetGraph(){graphFocusNodeId=null;renderGraph()}
function graphZoom(factor){const svg=d3.select('#graphSvg');svg.transition().call(d3.zoom().scaleBy,factor)}

// 从猜想弹窗跳转到关联图谱
function viewConjectureGraph(nodeId){
    // 关闭所有弹窗
    document.querySelectorAll('[style*="position:fixed"]').forEach(el=>{
        if(el.style.zIndex>='1000') el.remove();
    });
    // 设置聚焦节点
    graphFocusNodeId = nodeId;
    // 切换到图谱页
    showPage('graph');
    // 稍等 DOM 渲染完再高亮
    setTimeout(()=>{
        // 在图谱中高亮聚焦节点
        const focusNode = allNodes.find(n=>n.id===nodeId);
        if(!focusNode) return;
        // 显示提示
        showToast('🗺️ 已定位到「'+(focusNode.name?.zh||nodeId)+'」的关联图谱');
    }, 400);
}

// ============================================================

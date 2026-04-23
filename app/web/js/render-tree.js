/**
 * 知识树可视化 - 树形结构展示用户知识掌握情况
 */

let treeContainer = null;
let treeData = null;
let treeSvg = null;
let treeZoom = null;

function renderTreePage() {
    const main = document.getElementById('mainContent');
    main.innerHTML = `
        <div class="tree-header">
            <h2>🌳 知识树</h2>
            <div class="tree-controls">
                <button class="btn" onclick="treeExpandAll()">展开全部</button>
                <button class="btn" onclick="treeCollapseAll()">折叠全部</button>
                <button class="btn" onclick="treeResetView()">重置视图</button>
                <select id="tree-grade-filter" onchange="treeFilterByGrade(this.value)">
                    <option value="">全部年级</option>
                    <option value="小学一年级">小学一年级</option>
                    <option value="小学二年级">小学二年级</option>
                    <option value="小学三年级">小学三年级</option>
                    <option value="初中一年级">初中一年级</option>
                    <option value="初中二年级">初中二年级</option>
                    <option value="初中三年级">初中三年级</option>
                    <option value="高中一年级">高中一年级</option>
                    <option value="高中二年级">高中二年级</option>
                    <option value="高中三年级">高中三年级</option>
                </select>
            </div>
        </div>
        <div id="tree-legend">
            <span class="legend-item"><span class="legend-dot" style="background:#ccc"></span>未学习</span>
            <span class="legend-item"><span class="legend-dot" style="background:#4a9eff"></span>学习中</span>
            <span class="legend-item"><span class="legend-dot" style="background:#4caf50"></span>已掌握</span>
            <span class="legend-item"><span class="legend-dot" style="background:#ff5722"></span>未掌握</span>
        </div>
        <div id="tree-container"></div>
    `;
    
    treeContainer = document.getElementById('tree-container');
    loadTreeData();
}

async function loadTreeData() {
    try {
        const headers = AUTH.token ? {'Authorization': 'Bearer ' + AUTH.token} : {};
        
        const [nodesRes, knowledgeRes] = await Promise.all([
            fetch('/nodes'),
            AUTH.token ? fetch('/knowledge', {headers}) : Promise.resolve(null)
        ]);
        
        const nodesData = await nodesRes.json();
        let nodes = nodesData.nodes || [];
        
        // 只显示小学到高中阶段的知识点（~3000个），太多会卡
        const levelFilter = ['小学一年级','小学二年级','小学三年级','小学四年级','小学五年级','小学六年级','初中一年级','初中二年级','初中三年级','高中一年级','高中二年级','高中三年级'];
        nodes = nodes.filter(n => levelFilter.includes(n.grade));
        
        // 构建已掌握节点 map
        const masteryMap = {};
        if (knowledgeRes) {
            const knowledgeData = await knowledgeRes.json();
            (knowledgeData.items || []).forEach(item => {
                masteryMap[item.node_id] = item;
            });
        }
        
        const tree = buildTreeFromGraph(nodes, masteryMap);
        renderTree(tree);
    } catch (e) {
        console.error('加载树数据失败:', e);
        treeContainer.innerHTML = '<p style="padding:20px;color:#ff5722">加载失败: ' + e.message + '</p>';
    }
}

function buildTreeFromGraph(nodes, masteryMap) {
    const nodeMap = {};
    const roots = [];
    
    nodes.forEach(n => {
        nodeMap[n.id] = {
            id: n.id,
            name: n.name_zh || n.name || n.id,
            grade: n.grade || '',
            branch: n.branch || '',
            difficulty: n.difficulty || 1,
            prerequisites: n.prerequisites || [],
            mastery: getMasteryStatus(masteryMap, n.id),
            children: []
        };
    });
    
    nodes.forEach(n => {
        const node = nodeMap[n.id];
        if (!node) return;
        
        if (!n.prerequisites || n.prerequisites.length === 0) {
            roots.push(node);
        } else {
            n.prerequisites.forEach(preId => {
                const preNode = nodeMap[preId];
                if (preNode && !preNode.children.find(c => c.id === node.id)) {
                    preNode.children.push(node);
                }
            });
        }
    });
    
    if (roots.length > 0) {
        const treeRoot = {
            id: 'root',
            name: '数学知识体系',
            grade: '',
            branch: '',
            difficulty: 0,
            mastery: 'learned',
            children: roots
        };
        return treeRoot;
    }
    
    const fallbackRoot = {
        id: 'root',
        name: '数学知识体系',
        grade: '',
        branch: '',
        difficulty: 0,
        mastery: 'learned',
        children: Object.values(nodeMap).slice(0, 50)
    };
    return fallbackRoot;
}

function getMasteryStatus(masteryMap, nodeId) {
    if (!masteryMap || !masteryMap[nodeId]) return 'not_learned';
    const item = masteryMap[nodeId];
    const status = item.status;
    if (status === 'known') return 'mastered';
    if (status === 'learning') return 'learning';
    if (status === 'unknown') return 'not_mastered';
    return 'not_learned';
}

function renderTree(treeData) {
    const container = treeContainer;
    const width = container.clientWidth || 1200;
    const height = container.clientHeight || 800;
    
    d3.select(container).select('svg').remove();
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', '100%')
        .attr('height', height)
        .attr('viewBox', `0 0 ${width} ${height}`);
    
    treeSvg = svg;
    
    const g = svg.append('g').attr('class', 'tree-group');
    
    treeZoom = d3.zoom()
        .scaleExtent([0.1, 3])
        .on('zoom', (event) => g.attr('transform', event.transform));
    
    svg.call(treeZoom);
    
    const root = d3.hierarchy(treeData);
    const treeLayout = d3.tree()
        .nodeSize([180, 120])
        .separation((a, b) => a.parent === b.parent ? 1.2 : 2);
    
    treeLayout(root);
    
    const nodes = root.descendants();
    const links = root.links();
    
    const linkGenerator = d3.linkVertical()
        .x(d => d.x)
        .y(d => d.y);
    
    g.selectAll('.tree-link')
        .data(links)
        .join('path')
        .attr('class', 'tree-link')
        .attr('d', linkGenerator)
        .attr('fill', 'none')
        .attr('stroke', '#ddd')
        .attr('stroke-width', 2);
    
    const nodeGroups = g.selectAll('.tree-node')
        .data(nodes)
        .join('g')
        .attr('class', 'tree-node')
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
            if (d.data.id !== 'root') {
                openDetail(d.data.id);
            }
        });
    
    nodeGroups.append('circle')
        .attr('r', d => d.data.id === 'root' ? 20 : 14)
        .attr('fill', d => getMasteryColor(d.data.mastery))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);
    
    nodeGroups.append('text')
        .attr('dy', d => d.data.id === 'root' ? 35 : 28)
        .attr('text-anchor', 'middle')
        .attr('font-size', d => d.data.id === 'root' ? '14px' : '12px')
        .attr('fill', '#333')
        .text(d => truncateText(d.data.name, 8));
    
    nodeGroups.filter(d => d.data.branch && d.data.id !== 'root')
        .append('text')
        .attr('dy', -20)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', '#888')
        .text(d => d.data.branch);
    
    nodeGroups.filter(d => d.data.id === 'root')
        .append('text')
        .attr('dy', 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .attr('fill', '#fff')
        .attr('font-weight', 'bold')
        .text('🌳');
    
    const bounds = g.node().getBBox();
    const scale = Math.min(width / (bounds.width + 100), height / (bounds.height + 100), 1);
    const translateX = (width - bounds.width * scale) / 2 - bounds.x * scale;
    const translateY = 60;
    
    svg.call(treeZoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
}

function getMasteryColor(status) {
    const colors = {
        'mastered': '#4caf50',
        'learning': '#4a9eff',
        'not_mastered': '#ff5722',
        'not_learned': '#e0e0e0'
    };
    return colors[status] || '#ccc';
}

function truncateText(text, maxLen) {
    if (!text) return '';
    return text.length > maxLen ? text.slice(0, maxLen) + '…' : text;
}

function treeExpandAll() {
    if (treeSvg) {
        treeSvg.selectAll('.tree-node')
            .transition()
            .duration(300)
            .style('opacity', 1);
    }
}

function treeCollapseAll() {
    if (treeSvg) {
        treeSvg.selectAll('.tree-node')
            .filter(d => d.depth > 1)
            .transition()
            .duration(300)
            .style('opacity', 0.3);
    }
}

function treeResetView() {
    if (treeSvg && treeZoom) {
        const container = treeContainer;
        const width = container.clientWidth || 1200;
        const height = container.clientHeight || 800;
        treeSvg.transition().duration(500).call(
            treeZoom.transform,
            d3.zoomIdentity.translate(width / 4, 60).scale(0.8)
        );
    }
}

function treeFilterByGrade(grade) {
    if (treeSvg) {
        treeSvg.selectAll('.tree-node')
            .transition()
            .duration(200)
            .style('opacity', d => {
                if (!grade) return 1;
                return d.data.grade === grade ? 1 : 0.2;
            });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof d3 === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://d3js.org/d3.v7.min.js';
        script.onload = () => console.log('D3 loaded');
        document.head.appendChild(script);
    }
});

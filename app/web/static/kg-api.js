
// 知识图谱API
const KG_API = {
    // 基础路径
    basePath: './data',
    
    // 加载核心节点数据
    async loadNodes() {
        const response = await fetch(`${this.basePath}/core-nodes.json`);
        const data = await response.json();
        return data;
    },
    
    // 加载详情索引
    async loadIndex() {
        const response = await fetch(`${this.basePath}/details/index.json`);
        return await response.json();
    },
    
    // 加载节点详情
    async loadNodeDetail(nodeId, index = null) {
        if (!index) {
            index = await this.loadIndex();
        }
        const filepath = index[nodeId];
        if (!filepath) return null;
        
        const response = await fetch(`${this.basePath}/details/${filepath}`);
        const nodes = await response.json();
        return nodes.find(n => n.id === nodeId);
    }
};

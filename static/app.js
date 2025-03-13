new Vue({
    el: '#app',
    data: {
        networkInitialized: false,
        nodes: [],
        edges: [],
        startNode: null,
        endNode: null,
        weights: {
            latency: 0.4,
            load: 0.4,
            security: 0.2
        },
        currentPath: null,
        currentCost: null,
        chart: null
    },
    mounted() {
        // 初始化ECharts
        this.chart = echarts.init(document.getElementById('networkChart'));
        window.addEventListener('resize', () => this.chart.resize());
    },
    methods: {
        async initNetwork() {
            try {
                // 初始化网络
                await axios.post('http://localhost:5000/api/network/init');
                
                // 获取网络状态
                const response = await axios.get('http://localhost:5000/api/network/status');
                this.nodes = Object.entries(response.data.nodes).map(([id, data]) => ({
                    id: parseInt(id),
                    ...data
                }));
                this.edges = Object.entries(response.data.edges).map(([id, data]) => {
                    const [u, v] = id.split('-').map(Number);
                    return { u, v, ...data };
                });
                
                // 获取可视化数据
                const vizResponse = await axios.get('http://localhost:5000/api/network/visualization');
                this.updateChart(vizResponse.data.image);
                
                this.networkInitialized = true;
                this.$nextTick(() => {
                    this.startNode = this.nodes[0].id;
                    this.endNode = this.nodes[1].id;
                });
            } catch (error) {
                console.error('初始化网络失败:', error);
                alert('初始化网络失败，请检查后端服务是否正常运行');
            }
        },
        
        async findPath() {
            if (!this.startNode || !this.endNode) return;
            
            try {
                const response = await axios.post('http://localhost:5000/api/network/find_path', {
                    start: this.startNode,
                    end: this.endNode,
                    weights: this.weights
                });
                
                this.currentPath = response.data.path;
                this.currentCost = response.data.cost;
                this.updateChart(response.data.image);
            } catch (error) {
                console.error('查找路径失败:', error);
                alert('查找路径失败，请重试');
            }
        },
        
        updateChart(imageBase64) {
            const option = {
                graphic: {
                    elements: [{
                        type: 'image',
                        style: {
                            image: `data:image/png;base64,${imageBase64}`,
                            width: '100%',
                            height: '100%'
                        }
                    }]
                },
                grid: {
                    top: 0,
                    bottom: 0,
                    left: 0,
                    right: 0
                },
                xAxis: {
                    show: false
                },
                yAxis: {
                    show: false
                }
            };
            
            this.chart.setOption(option);
        }
    }
}); 
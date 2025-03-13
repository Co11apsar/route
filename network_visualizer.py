import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

class NetworkVisualizer:
    def __init__(self):
        self.graph = None
        self.pos = None
        self.node_colors = None
        self.edge_colors = None
        
    def create_network_graph(self, nodes, edges):
        """创建网络图"""
        self.graph = nx.Graph()
        
        # 添加节点
        for node_id, node_data in nodes.items():
            self.graph.add_node(node_id, **node_data)
            
        # 添加边
        for edge_id, edge_data in edges.items():
            u, v = edge_id
            self.graph.add_edge(u, v, **edge_data)
            
        # 计算节点位置
        self.pos = nx.spring_layout(self.graph)
        
    def update_node_colors(self, load_ratios):
        """更新节点颜色"""
        # 创建颜色映射
        colors = [(0, 1, 0), (1, 1, 0), (1, 0, 0)]  # 绿->黄->红
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # 根据负载率设置颜色
        self.node_colors = [cmap(ratio) for ratio in load_ratios]
        
    def update_edge_colors(self, security_levels):
        """更新边颜色"""
        # 创建颜色映射
        colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # 红->黄->绿
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # 根据安全等级设置颜色
        self.edge_colors = [cmap((level - 1) / 2) for level in security_levels]
        
    def highlight_path(self, path):
        """高亮显示路径"""
        if not path:
            return None
            
        # 创建边的颜色列表
        edge_colors = ['black'] * len(self.graph.edges())
        
        # 高亮路径上的边
        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            if edge in self.graph.edges():
                edge_idx = list(self.graph.edges()).index(edge)
                edge_colors[edge_idx] = 'red'
                
        return edge_colors
        
    def generate_network_image(self, highlight_path=None):
        """生成网络图图像"""
        plt.figure(figsize=(12, 8))
        
        # 绘制边
        edge_colors = self.highlight_path(highlight_path) if highlight_path else self.edge_colors
        nx.draw_networkx_edges(self.graph, self.pos, edge_color=edge_colors, width=2)
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_color=self.node_colors, 
                             node_size=500, alpha=0.7)
        
        # 添加节点标签
        labels = {node: f"{node}\n{self.graph.nodes[node].get('security_level', '')}" 
                 for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, self.pos, labels, font_size=8)
        
        # 添加边标签
        edge_labels = {(u, v): f"{self.graph.edges[u, v].get('latency', '')}ms" 
                      for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, font_size=8)
        
        # 将图像转换为base64字符串
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64 
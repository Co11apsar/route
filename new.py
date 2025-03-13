import heapq
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from tabulate import tabulate
import platform

plt.ion()

# 设置中文字体
def setup_chinese_font():
    system = platform.system()
    if system == 'Windows':
        font_path = 'C:/Windows/Fonts/msyh.ttc'  # 微软雅黑
    elif system == 'Darwin':  # macOS
        font_path = '/System/Library/Fonts/PingFang.ttc'  # 苹方字体
    else:  # Linux
        font_path = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
    
    # 设置中文字体
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    return font_prop

class SecureNode:
    def __init__(self, node_id, capacity, security_level):
        self.id = node_id
        self.max_capacity = capacity
        self.current_load = 0
        self.security_level = security_level  # 1-3级
        
    @property
    def load_ratio(self):
        return self.current_load / self.max_capacity

class SecureNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes = {}
        self.edge_props = {}
        self.step_records = []
        self.pos = None  # 保存节点位置
        self.font_prop = setup_chinese_font()
        
    def add_node(self, node):
        self.nodes[node.id] = node
        self.graph.add_node(node.id)
        
    def add_edge(self, u, v, latency, bandwidth):
        security = min(self.nodes[u].security_level, self.nodes[v].security_level)
        self.graph.add_edge(u, v)
        self.edge_props[(u, v)] = {
            'latency': latency,
            'bandwidth': bandwidth,
            'security': security
        }
        self.edge_props[(v, u)] = self.edge_props[(u, v)]  # 双向连接
        
    def update_load(self, path):
        for node_id in path:
            self.nodes[node_id].current_load = min(
                self.nodes[node_id].current_load + 3,
                self.nodes[node_id].max_capacity
            )
            
    def path_cost(self, u, v, weights):
        edge = self.edge_props[(u, v)]
        node = self.nodes[v]
        return (edge['latency'] * weights['latency'] + 
        (node.load_ratio ** 2) * 100 * weights['load'] + 
        (4 - edge['security']) * 10 * weights['security'])
    
    def find_path(self, start, end, weights):
        self.step_records = []
        heap = [(0, start, [])]
        costs = {n: float('inf') for n in self.graph.nodes}
        costs[start] = 0
        visited = {}
        
        while heap:
            current_cost, u, path = heapq.heappop(heap)
            
            if u in visited:
                continue
                
            new_path = path + [u]
            self._record_step(u, heap, visited.copy(), costs.copy(), new_path)
            
            if u == end:
                self.update_load(new_path)
                return new_path, current_cost
                
            visited[u] = True
            
            for v in self.graph.neighbors(u):
                if v in visited:
                    continue
                    
                edge_cost = self.path_cost(u, v, weights)
                new_cost = current_cost + edge_cost
                
                if new_cost < costs[v]:
                    costs[v] = new_cost
                    heapq.heappush(heap, (new_cost, v, new_path))
                    
        return None, float('inf')
    
    def _record_step(self, current_node, heap, visited, costs, path):
        record = {
            'current': current_node,
            'candidates': [(cost, n, p) for cost, n, p in heap],
            'visited': list(visited.keys()),
            'costs': costs.copy(),
            'path': path.copy()
        }
        self.step_records.append(record)
        
    def print_final_status(self):
        """输出最终节点状态表格"""
        headers = ["NodeID", "CurrentLoad", "MaxCapacity", "SecurityLevel", "LoadRate"]
        table = []
        
        for node in sorted(self.nodes.values(), key=lambda x: x.id):
            table.append([
                node.id,
                f"{node.current_load}/{node.max_capacity}",
                node.max_capacity,
                node.security_level,
                f"{node.load_ratio:.1%}"
            ])
        
        print("\nFinal Network Status:")
        print(tabulate(table, headers=headers, tablefmt="github"))
        
    def _draw_network(self, highlight_path=None):
        """绘制网络拓扑图"""
        # 创建新的图形
        plt.figure(figsize=(16, 9), dpi=100)
        ax = plt.gca()
        ax.set_position([0.1, 0.1, 0.8, 0.8])
        
        # 如果位置未初始化，创建新的布局
        if self.pos is None:
            self.pos = nx.spring_layout(self.graph, k=1, iterations=50)
            
        # 绘制基础网络结构
        # 1. 首先绘制所有边
        edges = [(u, v) for (u, v) in self.edge_props.keys() if u < v]
        edge_colors = [plt.cm.RdYlGn(self.edge_props[(u, v)]['security'] / 3) 
                      for (u, v) in edges]
        
        nx.draw_networkx_edges(self.graph, self.pos,
                             edgelist=edges,
                             edge_color=edge_colors,
                             width=2)

        # 2. 绘制所有节点
        node_colors = [plt.cm.RdYlGn_r(self.nodes[n].load_ratio) 
                      for n in self.graph.nodes()]
        nx.draw_networkx_nodes(self.graph, self.pos,
                             node_color=node_colors,
                             node_size=1000)

        # 3. 如果有高亮路径，绘制高亮效果
        if highlight_path and len(highlight_path) > 1:
            path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
            nx.draw_networkx_edges(self.graph, self.pos,
                                 edgelist=path_edges,
                                 edge_color='red',
                                 width=4)
            nx.draw_networkx_nodes(self.graph, self.pos,
                                 nodelist=highlight_path,
                                 node_color='lightblue',
                                 node_size=1200)
            
            # 添加路径标签
            path_label = "路径: " + " → ".join(map(str, highlight_path))
            plt.text(0.05, 0.95, path_label,
                    transform=ax.transAxes,
                    fontproperties=self.font_prop,
                    fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.8))

        # 4. 添加节点标签
        labels = {node_id: f"{node_id}\nS{node.security_level}"
                 for node_id, node in self.nodes.items()}
        nx.draw_networkx_labels(self.graph, self.pos,
                              labels,
                              font_family=self.font_prop.get_name(),
                              font_size=12)

        # 5. 添加边标签
        edge_labels = {(u, v): f"{props['latency']}ms"
                      for (u, v), props in self.edge_props.items()
                      if u < v}
        nx.draw_networkx_edge_labels(self.graph, self.pos,
                                   edge_labels,
                                   font_family=self.font_prop.get_name(),
                                   font_size=10)

        plt.title("网络拓扑图", fontproperties=self.font_prop, pad=20, fontsize=14)
        plt.axis('off')

def create_network():
    network = SecureNetwork()
    
    # 创建20个节点
    for i in range(20):
        capacity = random.randint(80, 200)
        security = random.choice([1, 2, 3])
        network.add_node(SecureNode(i, capacity, security))
        
    # 创建随机连接
    for _ in range(35):
        while True:
            u = random.randint(0, 19)
            v = random.randint(0, 19)
            if u != v and not network.graph.has_edge(u, v):
                latency = random.randint(10, 50)
                bandwidth = random.choice([100, 200, 500])
                network.add_edge(u, v, latency, bandwidth)
                break
                
    return network

def main():
    network = create_network()
    weights = {'latency': 0.4, 'load': 0.4, 'security': 0.2}
    
    # 模拟5次路由（无过程输出）
    for _ in range(100):
        src, dst = random.sample(range(20), 2)
        network.find_path(src, dst, weights)
    
    # 仅输出最终状态
    network.print_final_status()


if __name__ == "__main__":
    main()
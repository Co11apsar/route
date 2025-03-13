import networkx as nx
import matplotlib.pyplot as plt

# 创建有向图
G = nx.DiGraph()

# 初始化
nodes = ["Entry", "Node 1", "Node 2", "Node 3", "...", "Node N", "Exit"]
controller = "Controller"
redis = "Redis"

# 节点形状
shapes = {
    "Entry": "s",  # 方块
    "Exit": "s",   # 方块
    "Controller": "8",  # 八角星
    "Redis": "s"   # 方块
}

# 添加节点
G.add_node(controller, shape=shapes[controller], color="red")
G.add_node(redis, shape=shapes[redis], color="orange")
for node in nodes:
    G.add_node(node, shape=shapes.get(node, "o"), color="skyblue")

# 添加边
edges = [
    ("Entry", "Node 1"),
    ("Node 1", "Node 2"),
    ("Node 2", "Node 3"),
    ("Node 3", "..."),
    ("...", "Node N"),
    ("Node N", "Exit"),
    (controller, "Node 1"),
    (controller, "Node 2"),
    (controller, "Node 3"),
    (controller, "..."),
    (controller, "Node N"),
    (controller, redis),
    (redis, controller),
]

# 绘制图形
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)  # 布局

# 设置节点形状
for node, shape in nx.get_node_attributes(G, "shape").items():
    nx.draw_networkx_nodes(G, pos, nodelist=[node], node_shape=shape, node_size=1500, node_color=nx.get_node_attributes(G, "color")[node])

# 绘制边
nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle="->", arrowsize=15, edge_color="black")

# 绘制节点标签
nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")

# 图片标题和显示
plt.title("Network Structure with Controller and Redis")
plt.axis("off")
plt.show()
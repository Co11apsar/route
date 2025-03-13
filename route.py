import numpy as np
import random
import heapq

class Node:
    def __init__(self, node_id):
        self.id = node_id          # 节点ID
        self.load = 0.0           # 当前负载
        self.pheromone = 1.0      # 信息素浓度
        self.request_count = 0    # 被选次数统计

def dijkstra_shortest_path(start, end, delay_matrix):
    """使用Dijkstra算法找到最短延迟路径"""
    num_nodes = len(delay_matrix)
    visited = [False] * num_nodes
    distance = [np.inf] * num_nodes
    distance[start] = 0
    previous = [-1] * num_nodes

    priority_queue = [(0, start)]

    while priority_queue:
        dist_u, u = heapq.heappop(priority_queue)
        if visited[u]:
            continue
        visited[u] = True

        if u == end:
            break

        for v in range(num_nodes):
            if v == u:
                continue
            if not visited[v]:
                new_dist = dist_u + delay_matrix[u][v]
                if new_dist < distance[v]:
                    distance[v] = new_dist
                    previous[v] = u
                    heapq.heappush(priority_queue, (new_dist, v))

    # 重构路径
    path = []
    u = end
    while u != -1:
        path.append(u)
        u = previous[u]
    path.reverse()

    return path

def select_next_node(current_node_id, nodes, delay_matrix, alpha, beta, gamma, delta, epsilon=1e-5):
    """使用改进蚁群算法选择下一个节点"""
    epsilon = 1e-5  # 防止除以零
    probabilities = []
    total = 0.0

    candidates = [node for node in nodes if node.id != current_node_id]
    if not candidates:
        return None

    for node in candidates:
        network_delay = delay_matrix[current_node_id][node.id]
        heuristic = (alpha / (network_delay + epsilon)) + (beta / (node.load + 1 + epsilon))
        prob = (node.pheromone ** gamma) * (heuristic ** delta)
        probabilities.append(prob)
        total += prob

    if total == 0:
        return random.choice(candidates)

    probabilities = [p / total for p in probabilities]
    selected = np.random.choice(len(candidates), p=probabilities)
    selected_node = candidates[selected]
    selected_node.request_count += 1  # 确保这一行被正确执行
    return selected_node

def update_pheromone(node, Q, delay, load):
    """动态更新信息素"""
    delta_pheromone = Q / (delay + load + 1)
    node.pheromone += delta_pheromone

def evaporate_pheromone(nodes, rho):
    """全局信息素挥发"""
    for node in nodes:
        node.pheromone = max(node.pheromone * rho, 0.1)

# 算法参数配置
alpha = 0.8   # 延迟权重
beta = 1.0    # 负载权重
gamma = 0.5     # 信息素重要性指数
delta = 3     # 启发因子重要性指数
rho = 0.8     # 信息素挥发率
Q = 100       # 信息素增强系数
num_nodes = 8 # 网络节点数量（包括入口和出口）
num_requests = 5000  # 总请求数

# 初始化随机种子
random.seed(42)
np.random.seed(42)

# 创建网络节点
nodes = [Node(i) for i in range(num_nodes)]

# 定义入口和出口节点
entry_node = 0
exit_node = num_nodes - 1
all_nodes = [node for node in nodes if node.id != entry_node and node.id != exit_node]

# 初始化网络延迟矩阵（模拟真实网络探测）
delay_matrix = np.zeros((num_nodes, num_nodes))
print("正在初始化网络延迟矩阵...")
for i in range(num_nodes):
    for j in range(i+1, num_nodes):
        if i != j:
            delay_matrix[i][j] = random.randint(50, 200)
            delay_matrix[j][i] = delay_matrix[i][j]
    delay_matrix[i][i] = 0  # 节点到自身延迟为0

# 模拟请求处理过程
print("\n开始模拟负载均衡...")
total_time = 0.0

for req_id in range(num_requests):
    # 固定入口节点
    current_node_id = entry_node
    nodes[current_node_id].load += 1  # 入口节点负载增加
    
    # 记录路径
    path = [current_node_id]
    
    # 使用蚁群算法和最短路径算法结合选择路径
    while current_node_id != exit_node:
        # 获取当前节点对象
        current_node = next((node for node in nodes if node.id == current_node_id), None)
        
        # 使用Dijkstra算法获取最短路径
        shortest_path = dijkstra_shortest_path(current_node_id, exit_node, delay_matrix)
        next_node_id = shortest_path[1] if len(shortest_path) > 1 else exit_node
        
        # 使用蚁群算法选择下一个节点
        next_node = select_next_node(current_node_id, nodes, delay_matrix, 
                                      alpha, beta, gamma, delta)
        
        # 权衡最短路径和蚁群算法选择
        if next_node.id != next_node_id:
            # 如果蚁群算法选择的节点与最短路径不同，比较延迟和负载
            acl_delay = delay_matrix[current_node_id][next_node.id]
            sp_delay = delay_matrix[current_node_id][next_node_id]
            
            if (acl_delay <= sp_delay * 1.2) and (next_node.load < nodes[next_node_id].load):
                # 蚁群算法选择的节点延迟和负载更优
                next_node_id = next_node.id
        
        # 更新路径和当前节点
        path.append(next_node_id)
        current_node_id = next_node_id
    
    # 更新负载和信息素
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i+1]
        nodes[next_node].load += 1
        update_pheromone(nodes[next_node], Q, delay_matrix[current][next_node], nodes[next_node].load)
    
    # 计算总用时
    total_delay = sum(delay_matrix[path[i]][path[i+1]] for i in range(len(path)-1))
    total_time += total_delay
    
    # 定期挥发信息素
    if req_id % 10 == 0:
        evaporate_pheromone(nodes, rho)
    
    # 模拟负载自然衰减
    for node in nodes:
        if node.id not in (entry_node, exit_node):
            node.load = max(node.load - 0.3, 0)  # 每秒处理0.3个请求

# 结果输出
# 结果输出
print("\n节点状态统计结果：")
print("节点ID | 负载 | 请求次数 | 平均延迟 ")
print("------------------------------------------------")
avg_delays = []
for node in nodes:
    if node.id == entry_node or node.id == exit_node:
        avg_delays.append(0)
    else:
        outgoing_delays = [delay_matrix[node.id][j] for j in range(num_nodes) if j != node.id]
        avg_delay = np.mean(outgoing_delays) if outgoing_delays else 0
        avg_delays.append(avg_delay)

for node_idx, node in enumerate(nodes):
    if node.id == entry_node or node.id == exit_node:
        print(f"{node.id:^6} | {'入口' if node.id == entry_node else '出口'}    "
              f" | {node.request_count:^8} | {avg_delays[node_idx]:^8.2f}ms")
    else:
        print(f"{node.id:^6} | {node.load:^8.2f} | {node.request_count:^8} | {avg_delays[node_idx]:^8.2f}ms")

print(f"\n总用时: {total_time:.2f}ms")
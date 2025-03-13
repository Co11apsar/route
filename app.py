from flask import Flask, render_template, jsonify, request
from new import SecureNetwork, create_network
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # 设置matplotlib后端
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

network = None

@app.route('/')
def index():
    # 添加初始空数据
    return render_template('index.html', nodes=[], edges=[])

@app.route('/api/network/init', methods=['POST'])
def init_network():
    global network
    network = create_network()
    return jsonify({'message': 'Network initialized successfully'})

@app.route('/api/network/status', methods=['GET'])
def get_network_status():
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 400
    
    nodes_status = {
        node_id: {
            'security_level': node.security_level,
            'max_capacity': node.max_capacity,
            'current_load': node.current_load,
            'load_ratio': node.load_ratio
        }
        for node_id, node in network.nodes.items()
    }
    
    edges_status = {
        f"{u}-{v}": {
            'latency': props['latency'],
            'bandwidth': props['bandwidth'],
            'security': props['security']
        }
        for (u, v), props in network.edge_props.items()
        if u < v  # 只返回一个方向的边
    }
    
    return jsonify({
        'nodes': nodes_status,
        'edges': edges_status
    })

@app.route('/api/network/find_path', methods=['POST'])
def find_path():
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 400
    
    data = request.json
    start = data.get('start')
    end = data.get('end')
    weights = data.get('weights', {'latency': 0.4, 'load': 0.4, 'security': 0.2})
    
    try:
        path, cost = network.find_path(start, end, weights)
        
        # 生成可视化
        network._draw_network(highlight_path=path)
        
        # 添加图例
        legend_elements = [
            plt.Line2D([0], [0], color='red', lw=2, label='选中路径'),
            plt.scatter([0], [0], c='lightblue', s=100, label='路径节点'),
            plt.scatter([0], [0], c='g', s=100, label='低负载'),
            plt.scatter([0], [0], c='y', s=100, label='中负载'),
            plt.scatter([0], [0], c='r', s=100, label='高负载')
        ]
        plt.legend(handles=legend_elements, 
                  prop=network.font_prop,
                  loc='upper right',
                  bbox_to_anchor=(1.15, 1),
                  fontsize=10)
        
        # 将图像转换为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100,
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'path': path,
            'cost': cost,
            'image': image_base64
        })
    except Exception as e:
        plt.close()  # 确保关闭所有图形
        return jsonify({'error': str(e)}), 400

@app.route('/api/network/visualization', methods=['GET'])
def get_visualization():
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 400
    
    try:
        # 生成可视化
        network._draw_network()
        
        # 添加图例
        legend_elements = [
            plt.scatter([0], [0], c='g', s=100, label='低负载'),
            plt.scatter([0], [0], c='y', s=100, label='中负载'),
            plt.scatter([0], [0], c='r', s=100, label='高负载')
        ]
        plt.legend(handles=legend_elements, 
                  prop=network.font_prop,
                  loc='upper right',
                  bbox_to_anchor=(1.15, 1),
                  fontsize=10)
        
        # 将图像转换为base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100,
                    facecolor='white', edgecolor='none')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return jsonify({'image': image_base64})
    except Exception as e:
        plt.close()  # 确保关闭所有图形
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 
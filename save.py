from scapy.all import IP, TCP, UDP, send

# 预定义的参数
TARGET_IP = "192.168.15.131"  # 目标IP地址
TARGET_PORT = 8080  # 目标端口号
PROTOCOL = "tcp"  # 协议类型 ('tcp' 或 'udp')
DATA = "Hello, TCP!"  # 数据负载

def send_packet(ip, port, protocol, data):
    """
    向指定的IP地址发送TCP或UDP数据包
    :param ip: 目标IP地址
    :param port: 目标端口号
    :param protocol: 协议类型 ('tcp' 或 'udp')
    :param data: 数据负载
    """
    if protocol.lower() == 'tcp':
        packet = IP(dst=ip) / TCP(dport=port) / data
    elif protocol.lower() == 'udp':
        packet = IP(dst=ip) / UDP(dport=port) / data
    else:
        print("Unsupported protocol. Use 'tcp' or 'udp'.")
        return

    print(f"Sending {protocol.upper()} packet to {ip}:{port} with data: {data}")
    send(packet, verbose=1)

def main():
    send_packet(TARGET_IP, TARGET_PORT, PROTOCOL, DATA)

if __name__ == "__main__":
    main()
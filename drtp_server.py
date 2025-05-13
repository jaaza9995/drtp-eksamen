import socket
import time
from header import parse_header, create_packet
from datetime import datetime

def run_server(ip, port):
    buffer_size = 1472
    expected_seq = 1
    file_data = b''

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))

    while True:
        packet, addr = server_socket.recvfrom(buffer_size)
        seq, ack, flags, win = parse_header(packet[:12])
        data = packet[12:]

        if flags == 0b0001:
            print("SYN packet is received")
            synack = create_packet(0, seq + 1, 0b0011, 0, b'')
            server_socket.sendto(synack, addr)
            print("SYN-ACK packet is sent")
            continue

        elif flags == 0b0010:
            print("ACK packet is received")
            print("Connection established")
            start_time = time.time()
            continue

        elif flags == 0b1000:
            print("FIN packet is received")
            fin_ack = create_packet(0, seq + 1, 0b0010, 0, b'')
            server_socket.sendto(fin_ack, addr)
            print("FIN ACK packet is sent")
            break

        if seq == expected_seq:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{timestamp} -- packet {seq} is received")
            print(f"{timestamp} -- sending ack for the received {seq}")
            file_data += data
            ack_pkt = create_packet(0, seq + 1, 0b0010, 0, b'')
            server_socket.sendto(ack_pkt, addr)
            expected_seq += 1
            continue

    end_time = time.time()
    duration = end_time - start_time
    throughput = (len(file_data) * 8) / (duration * 1_000_000)

    with open("received_file", "wb") as f:
        f.write(file_data)

    print(f"The throughput is {throughput:.2f} Mbps")
    print("Connection Closes")
    server_socket.close()

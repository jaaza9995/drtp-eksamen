import socket
import time
from header import create_packet, parse_header
from datetime import datetime

def run_client(ip, port, filename, window_size):
    buffer_size = 1472
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.4)
    server_addr = (ip, port)

    # === 3-WAY HANDSHAKE ===
    seq = 0
    syn = create_packet(seq, 0, 0b0001, 0, b'')
    client_socket.sendto(syn, server_addr)
    print("SYN packet is sent")

    while True:
        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, r_win = parse_header(response[:12])
            if r_flags == 0b0011:
                window_size = min(window_size, r_win)
                print(f"SYN-ACK packet is received, server window = {r_win}, using window size = {window_size}")
                ack = create_packet(seq, r_seq + 1, 0b0010, 0, b'')
                client_socket.sendto(ack, server_addr)
                print("ACK packet is sent")
                break
        except socket.timeout:
            client_socket.sendto(syn, server_addr)

    print("Connection established")
    time.sleep(0.2)

    with open(filename, "rb") as f:
        file_data = f.read()
    chunks = [file_data[i:i+992] for i in range(0, len(file_data), 992)]

    base = 1
    next_seq = 1
    packets = {}
    total_chunks = len(chunks)

    for i in range(total_chunks):
        pkt = create_packet(i + 1, 0, 0b0000, 0, chunks[i])
        packets[i + 1] = pkt

    while base <= total_chunks:
        # Send nye pakker innenfor vinduet
        while next_seq < base + window_size and next_seq <= total_chunks:
            client_socket.sendto(packets[next_seq], server_addr)
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{timestamp} -- packet with seq = {next_seq} is sent")
            next_seq += 1

        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, _ = parse_header(response[:12])
            if r_flags == 0b0010:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"{timestamp} -- ACK for packet = {r_ack - 1} is received")
                base = r_ack
        except socket.timeout:
            print("Timeout occurred. Resending window...")
            for i in range(base, next_seq):
                client_socket.sendto(packets[i], server_addr)
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"{timestamp} -- RESEND packet with seq = {i}")

    # === TEARDOWN ===
    fin = create_packet(next_seq, 0, 0b1000, 0, b'')
    client_socket.sendto(fin, server_addr)
    print("FIN packet is sent")

    while True:
        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, _ = parse_header(response[:12])
            if r_flags == 0b1010:  # FIN + ACK
                print("FIN-ACK packet is received")
                break
        except socket.timeout:
            client_socket.sendto(fin, server_addr)

    client_socket.close()
    print("Connection Closes")

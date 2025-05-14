# drtp_client.py
from datetime import datetime
import socket
import time
from header import create_packet, parse_header, get_header_size

def run_client(ip, port, filename, window_size):
    buffer_size = 1000  # 8 bytes header + 992 bytes data
    header_size = get_header_size()
    seq = 1
    ack = 0
    flags = 0
    win = window_size

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.4)
    server_addr = (ip, port)

    # === 3-WAY HANDSHAKE ===
    print("Connection Establishment Phase:")
    print("SYN packet is sent")
    syn_packet = create_packet(seq, ack, 0b1000, win)  # SYN
    client_socket.sendto(syn_packet, server_addr)

    while True:
        try:
            syn_ack_packet, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, r_win = parse_header(syn_ack_packet)
            if r_flags & (1 << 3) and r_flags & (1 << 2):  # SYN + ACK
                print("SYN-ACK packet is received")
                ack_packet = create_packet(seq, r_seq, 0b0100, win)
                client_socket.sendto(ack_packet, server_addr)
                print("ACK packet is sent")
                print("Connection established")
                break
        except socket.timeout:
            client_socket.sendto(syn_packet, server_addr)  # Retry SYN

    # === FILE TRANSFER PHASE ===
    with open(filename, "rb") as f:
        file_data = f.read()
    chunks = [file_data[i:i + (buffer_size - header_size)] for i in range(0, len(file_data), buffer_size - header_size)]

    base = 1
    next_seq = 1
    total_sent = 0
    start_time = time.time()

    while base <= len(chunks):
        # Send within window
        while next_seq < base + window_size and next_seq <= len(chunks):
            data = chunks[next_seq - 1]
            pkt = create_packet(next_seq, 0, 0, 0, data)
            client_socket.sendto(pkt, server_addr)
            print(f"{datetime.now()} -- packet with seq = {next_seq} is sent, sliding window = {{{', '.join(str(i) for i in range(base, next_seq + 1))}}}")
            next_seq += 1

        try:
            ack_pkt, _ = client_socket.recvfrom(buffer_size)
            _, ack_num, flags, _ = parse_header(ack_pkt)
            if flags & (1 << 2):  # ACK
                print(f"{datetime.now()} -- ACK for packet = {ack_num} is received")
                base = ack_num + 1
        except socket.timeout:
            next_seq = base  # Go-back-N: resend all from base

    # === CONNECTION TERMINATION ===
    fin_pkt = create_packet(0, 0, 0b0010, 0)  # FIN
    client_socket.sendto(fin_pkt, server_addr)
    print("DATA Finished")
    print("\nConnection Teardown:")
    print("\nFIN packet is sent")

    while True:
        try:
            fin_ack, _ = client_socket.recvfrom(buffer_size)
            _, _, flags, _ = parse_header(fin_ack)
            if flags & (1 << 2) and flags & (1 << 1):  # FIN+ACK
                print("FIN ACK packet is received")
                
                break
        except socket.timeout:
            client_socket.sendto(fin_pkt, server_addr)  # Resend FIN

    end_time = time.time()
    total_mb = len(file_data) / 1_000_000
    duration = end_time - start_time
    throughput = total_mb * 8 / duration
    print(f"\nThe throughput is {throughput:.2f} Mbps")
    print("Connection closes")
    client_socket.close()

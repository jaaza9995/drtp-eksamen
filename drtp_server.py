# drtp_server.py
from datetime import datetime
import socket
import time
from header import parse_header, create_packet, get_header_size

def run_server(ip, port, destination_file, discard_seq=None):
    dropped = False
    buffer_size = 1000  # 8 byte header + 992 byte data
    expected_seq = 1
    total_bytes = 0
    header_size = get_header_size()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))

    print("SYN packet is received")

    # === 3-WAY HANDSHAKE ===
    syn_msg, client_addr = server_socket.recvfrom(buffer_size)
    seq, ack, flags, win = parse_header(syn_msg)
    syn_ack_packet = create_packet(0, 0, 0b1100, 15)  # SYN+ACK, win=15
    server_socket.sendto(syn_ack_packet, client_addr)
    print("SYN-ACK packet is sent")

    # wait for final ACK from client
    final_ack, _ = server_socket.recvfrom(buffer_size)
    print("ACK packet is received")
    print("Connection established")

    # === Start timer ===
    start_time = time.time()

    with open(destination_file, "wb") as f:
        while True:
            try:
                packet, _ = server_socket.recvfrom(buffer_size)
                if len(packet) >= header_size:
                    seq, ack, flags, win = parse_header(packet)

                    # Handle FIN
                    if flags & (1 << 1):  # FIN flag
                        print("FIN packet is received")
                        fin_ack = create_packet(0, 0, 0b0110, 0)  # FIN+ACK
                        server_socket.sendto(fin_ack, client_addr)
                        print("FIN ACK packet is sent")
                        break

                    # Drop specific packet (if -d used)
                    if discard_seq is not None and seq == discard_seq and not dropped:
                            dropped = True
                            print(f"{datetime.now()} --- deliberately dropping packet {seq}")
                            continue

                    if seq == expected_seq:
                        data = packet[header_size:]
                        f.write(data)
                        total_bytes += len(data)

                        from datetime import datetime
                        print(f"{datetime.now()} -- sending ack for the received {seq}")
                        ack_pkt = create_packet(0, seq, 0b0100, 0)
                        server_socket.sendto(ack_pkt, client_addr)
                        print(f"{datetime.now()} -- packet {seq} is received")

                        expected_seq += 1
                    else:
                        # Out-of-order packets ignored (Go-Back-N)
                        continue
            except socket.timeout:
                continue

    # === End timer ===
    end_time = time.time()
    duration = end_time - start_time
    mb_received = total_bytes / 1_000_000
    throughput = mb_received * 8 / duration

    print(f"\nThe throughput is {throughput:.2f} Mbps")
    print("Connection Closes")
    server_socket.close()
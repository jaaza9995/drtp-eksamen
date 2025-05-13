import socket
import time
from header import create_packet, parse_header

def run_client(ip, port, filename):
    buffer_size = 1472
    syn_seq = 0
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(0.4)
    server_addr = (ip, port)

    print("SYN packet is sent")
    syn = create_packet(syn_seq, 0, 0b0001, 0, b'')
    client_socket.sendto(syn, server_addr)
    time.sleep(0.1)

    while True:
        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, _ = parse_header(response[:12])
            if r_flags == 0b0011:
                print("SYN-ACK packet is received")
                ack = create_packet(syn_seq, r_seq + 1, 0b0010, 0, b'')
                client_socket.sendto(ack, server_addr)
                print("ACK packet is sent")
                break
        except socket.timeout:
            client_socket.sendto(syn, server_addr)

    print("Connection established")
    seq = 1  # Første datapakke starter med seq=1
    time.sleep(0.2)


    with open(filename, "rb") as f:
        file_data = f.read()

    chunks = [file_data[i:i+992] for i in range(0, len(file_data), 992)]

    for chunk in chunks:
        while True:
            pkt = create_packet(seq, 0, 0b0000, 0, chunk)
            client_socket.sendto(pkt, server_addr)
            timestamp = time.time()
            window = list(range(seq, seq + 5))
            window_str = ', '.join(str(n) for n in window)
            print(f"{timestamp:.6f} -- packet with seq = {seq} is sent, sliding window = {{{window_str}}}")

            try:
                response, _ = client_socket.recvfrom(buffer_size)
                r_seq, r_ack, r_flags, _ = parse_header(response[:12])
                print(f"[DEBUG] Received ACK header: seq={r_seq}, ack={r_ack}, flags={r_flags}")
                if r_flags == 0b0010 and r_ack == seq + 1:
                    print(f"{timestamp:.6f} -- ACK for packet = {seq} is received")
                    seq += 1
                    break
            except socket.timeout:
                print(f"[DEBUG] Timeout waiting for ACK for seq={seq}")
                pass

    print("....")
    print("DATA Finished")

    fin = create_packet(seq, 0, 0b1000, 0, b'')
    client_socket.sendto(fin, server_addr)
    print("FIN packet is sent")

    while True:
        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, _ = parse_header(response[:12])
            if r_flags == 0b0010:
                print("FIN ACK packet is received")
                break
        except socket.timeout:
            client_socket.sendto(fin, server_addr)

    client_socket.close()
    print("Connection Closes")

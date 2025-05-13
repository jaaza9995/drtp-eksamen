import socket
import time
from header import parse_header, create_packet
from datetime import datetime

def run_server(ip, port, destination_file, discard=False):
    buffer_size = 1472
    expected_seq = 1
    file_data = b''

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))

    dropped_once = False  # Vi dropper kun én gang

    while True:
        packet, addr = server_socket.recvfrom(buffer_size)
        seq, ack, flags, win = parse_header(packet[:12])
        data = packet[12:]

        if flags == 0b0001:
            print("SYN packet is received")
            synack = create_packet(0, seq + 1, 0b0011, 15, b'')  # sender vindu = 15
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
            fin_ack = create_packet(0, seq + 1, 0b1010, 0, b'')  # FIN + ACK
            server_socket.sendto(fin_ack, addr)
            print("FIN ACK packet is sent")
            break

        # === DROP PAKKE EN GANG HVIS --discard ER AKTIV ===
        if discard and not dropped_once and seq == 3:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{timestamp} -- packet {seq} is intentionally dropped (discard test)")
            dropped_once = True
            continue

        # === NORMAL MOTTAGELSE ===
        if seq == expected_seq:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{timestamp} -- packet {seq} is received")
            file_data += data
            ack_pkt = create_packet(0, seq + 1, 0b0010, 0, b'')
            server_socket.sendto(ack_pkt, addr)
            print(f"{timestamp} -- sending ack for the received {seq}")
            expected_seq += 1
        else:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{timestamp} -- packet {seq} is discarded (expected {expected_seq})")
            continue

    # === FILE WRITING OG THROUGHPUT ===
    end_time = time.time()
    duration = end_time - start_time
    throughput = (len(file_data) * 8) / (duration * 1_000_000)

    try:
        with open(destination_file, "wb") as f:
            f.write(file_data)
        print(f"File successfully written to '{destination_file}'")
    except Exception as e:
        print(f"Error writing to file '{destination_file}': {e}")


    print(f"The throughput is {throughput:.2f} Mbps")
    print("Connection Closes")
    server_socket.close()

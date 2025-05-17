from datetime import datetime
import socket
import time
from header import parse_header, create_packet, get_header_size

def run_server(ip, port, destination_file, discard_seq=None):
    """
    Kjører en DRTP-server som mottar en fil. Dette skjer over UDP og lagres til filsystemet.


    ip: IP-adressen serveren skal lytte på.
    port: Porten serveren skal lytte på.
    destination_file: Filen vi skal lagre dataen i.
    discard_seq: Hvis du skriver inn et tall her, dropper serveren pakken med det nummeret én gang (for å teste pakkedropp).

    Input:
        - Får DRTP-pakker fra klienten over UDP
        - Hver pakke har 8 bytes header og 992 bytes data

        Output:
        - Dataen lagres i den valgte filen 
        - Skriver ut til terminalen hva som skjer underveis

        Returnerer:
        - Ingenting
        - Lagrer fil og skriver meldinger

        Feilhåndtering:
        - Hvis det tar for lang tid (timeout), så bare venter den videre
    """

    dropped = False  # Sjekker om discard_seq allerede er droppet én gang
    buffer_size = 1000  # 8 bytes header + 992 bytes data
    expected_seq = 1  # Hvilket sekvensnummer vi venter på
    total_bytes = 0  # Hvor mye data vi har fått totalt
    header_size = get_header_size()  # Hvor stor headeren er (skal være 8 bytes)

    # Setter opp UDP socket og binder den til IP og port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print("SYN packet is received")

    # 3-veis håndtrykk 
    syn_msg, client_addr = server_socket.recvfrom(buffer_size)  # Venter på SYN
    seq, ack, flags, win = parse_header(syn_msg)  # Leser header
    syn_ack_packet = create_packet(0, 0, 0b1100, 15)  # Lager SYN-ACK (flagg 0b1100)
    server_socket.sendto(syn_ack_packet, client_addr)  # Sender tilbake til klient
    print("SYN-ACK packet is sent")

    final_ack, _ = server_socket.recvfrom(buffer_size)  # Venter på siste ACK
    print("ACK packet is received")
    print("Connection established")

    # Starter timer for throughput
    start_time = time.time()

    # Åpner filen for å lagre det vi mottar
    with open(destination_file, "wb") as f:
        while True:
            try:
                packet, _ = server_socket.recvfrom(buffer_size)  # Mottar en pakke
                if len(packet) >= header_size:  # Sjekker at den har header
                    seq, ack, flags, win = parse_header(packet)

                    # Hvis det er en FIN-pakke, avslutt forbindelsen
                    if flags & (1 << 1):
                        print("FIN packet is received")
                        fin_ack = create_packet(0, 0, 0b0110, 0)  # Lager FIN-ACK
                        server_socket.sendto(fin_ack, client_addr)
                        print("FIN ACK packet is sent")
                        break

                    # Hvis vi skal droppe denne pakken (bare én gang)
                    if discard_seq is not None and seq == discard_seq and not dropped:
                        dropped = True
                        print(f"{datetime.now()} --- deliberately dropping packet {seq}")
                        continue  # Hopper over denne pakken

                    # Hvis vi fikk riktig pakke ( Go-Back-N )
                    if seq == expected_seq:
                        data = packet[header_size:]  # Tar ut datadelen
                        f.write(data)  # Skriver data til fil
                        total_bytes += len(data)  # Teller hvor mye vi har fått

                        print(f"{datetime.now()} -- sending ack for the received {seq}")
                        ack_pkt = create_packet(0, seq, 0b0100, 0)  # Lager ACK
                        server_socket.sendto(ack_pkt, client_addr)  # Sender ACK
                        print(f"{datetime.now()} -- packet {seq} is received")

                        expected_seq += 1  # Venter på neste
                        
                    else: # Hvis pakken er ute av rekkefølge, ignorer den (Go-Back-N)
                        continue

            except socket.timeout: # Hvis det tar for lang tid, bare prøv igjen
                continue

    # Stopper tidtaking og regner ut throughput
    end_time = time.time()
    duration = end_time - start_time
    mb_received = total_bytes / 1_000_000
    throughput = mb_received * 8 / duration

    print(f"\nThe throughput is {throughput:.2f} Mbps")
    print("Connection Closes")
    server_socket.close()

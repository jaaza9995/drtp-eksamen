import socket
import time
from header import create_packet, parse_header  # Funksjoner for å lage og lese DRTP-pakker
from datetime import datetime

def run_client(ip, port, filename, window_size):
    """
    ip: IP-en til serveren vi skal koble oss til.
    port: Porten serveren lytter på.
    filename: Filen vi skal sende til serveren.
    window_size: Hvor mange pakker vi kan sende før vi må vente på ACK (Go-Back-N).

    Hva funksjonen gjør:
    - Lager forbindelse med server via 3-way handshake
    - Leser filen og deler den i biter (maks 992 bytes hver)
    - Sender bitene med DRTP-pakker og håndterer retransmisjon
    - Regner ut throughput når alt er sendt
    - Avslutter forbindelsen med FIN

    Input:
    - Filnavn og innholdet i filen som sendes som data

    Output:
    - Skriver status til terminalen underveis
    - Returnerer ingenting
    - Lukker forbindelsen til slutt

    Feilhåndtering:
    - Hvis en pakke ikke blir ACK'et i tide (timeout), sendes den på nytt
    - Ved timeout i håndtrykk eller avslutning prøver klienten igjen
    """

    buffer_size = 1000  # Maks pakke: 8 bytes header + 992 bytes data
    syn_seq = 1  # Sekvensnummeret vi starter med
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Setter opp UDP socket
    client_socket.settimeout(0.4)  # Setter timeout for svar
    server_addr = (ip, port)  # Adresse til serveren

    # === 3-WAY HANDSHAKE ===
    print("SYN packet is sent")
    syn = create_packet(syn_seq, 0, 0b0001, window_size, b'')  # Lager SYN-pakke med riktig flagg
    client_socket.sendto(syn, server_addr)  # Sender SYN

    # Venter på SYN-ACK fra serveren
    while True:
        try:
            syn_ack, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, r_win = parse_header(syn_ack)
            if r_flags & 0b1000:  # Hvis det er SYN-ACK
                print("SYN-ACK packet is received")
                break
        except socket.timeout:
            # Hvis vi ikke får svar, prøver vi å sende SYN igjen
            print("SYN-ACK timeout, sending SYN again")
            client_socket.sendto(syn, server_addr)

    # Sender siste ACK for å etablere forbindelsen
    ack_pkt = create_packet(0, 0, 0b0100, window_size, b'')
    client_socket.sendto(ack_pkt, server_addr)
    print("ACK packet is sent")
    print("Connection established")

    # === Leser fil og deler opp i chunks ===
    with open(filename, "rb") as f:
        data_chunks = []  # Liste med alle databitene
        while True:
            chunk = f.read(992)  # Leser maks 992 bytes (plass til 8 byte header)
            if not chunk:
                break
            data_chunks.append(chunk)

    # Variabler for Go-Back-N
    base = 1              # Første pakke i vinduet
    next_seq = 1          # Neste pakke vi skal sende
    total_packets = len(data_chunks)  # Antall pakker å sende
    acked = 0             # Hvor langt vi har fått bekreftelse

    start_time = time.time()  # Starter klokka for throughput-beregning

    # === Sender pakker med sliding window ===
    while acked < total_packets:
        # Så lenge vi er innenfor vinduet og har flere pakker, send dem
        while next_seq < base + window_size and next_seq <= total_packets:
            pkt = create_packet(
                next_seq, 0, 0b0000, window_size, data_chunks[next_seq - 1]
            )
            client_socket.sendto(pkt, server_addr)
            print(f"{datetime.now()} -- packet with seq = {next_seq} is sent, sliding window = {{{', '.join(str(i) for i in range(base, next_seq + 1))}}}")
            next_seq += 1

        try:
            ack_pkt, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, r_win = parse_header(ack_pkt)

            if r_flags & 0b0100:  # Hvis det er en ACK
                print(f"{datetime.now()} -- ack {r_ack} is received")
                base = r_ack + 1  # Flytter vinduet fremover
                acked = r_ack     # Oppdaterer antall ACKed pakker

        except socket.timeout:
            # Hvis timeout – resend hele vinduet fra base
            print("Timeout! Resending window")
            next_seq = base  # Starter fra base igjen

    # === Når alt er sendt, avslutt med FIN ===
    fin_pkt = create_packet(0, 0, 0b0010, 0, b'')  # Lager FIN-pakke
    client_socket.sendto(fin_pkt, server_addr)
    print("FIN is sent")

    # Venter på FIN-ACK fra serveren
    while True:
        try:
            response, _ = client_socket.recvfrom(buffer_size)
            r_seq, r_ack, r_flags, r_win = parse_header(response)
            if r_flags & 0b0110:  # Hvis FIN-ACK
                print("FIN ACK is received")
                break
        except socket.timeout:
            print("Timeout on FIN, sending FIN again")
            client_socket.sendto(fin_pkt, server_addr)

    # === Gjør ferdig og regner ut throughput ===
    end_time = time.time()
    duration = end_time - start_time
    mb_sent = sum(len(chunk) for chunk in data_chunks) / 1_000_000  # Bytes til MB
    throughput = mb_sent * 8 / duration  # Mbps

    print(f"\nThe throughput is {throughput:.2f} Mbps")
    print("Connection closed")
    client_socket.close()

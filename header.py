from struct import *

# DRTP header: sequence number (4 bytes), ack number (2 bytes), flags (1 byte), window size (1 byte)
header_format = '!IHBb'  # total 8 bytes

# Valgfritt: skriv ut headerstørrelse
print(f"size of the header = {calcsize(header_format)}")

def create_packet(seq, ack, flags, win, data):
    header = pack(header_format, seq, ack, flags, win)
    packet = header + data
    return packet

def parse_header(header):
    return unpack(header_format, header[:8])

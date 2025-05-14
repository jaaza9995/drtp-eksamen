# header.py

from struct import pack, unpack, calcsize

# 8-byte DRTP header: 2 bytes each
# Sequence Number, Acknowledgment Number, Flags, Receiver Window
header_format = '!HHHH'

def create_packet(seq, ack, flags, win, data=b''):
    header = pack(header_format, seq, ack, flags, win)
    return header + data

def parse_header(packet):
    return unpack(header_format, packet[:8])

def parse_flags(flags):
    syn = flags & (1 << 3)
    ack = flags & (1 << 2)
    fin = flags & (1 << 1)
    return syn, ack, fin

def get_header_size():
    return calcsize(header_format)

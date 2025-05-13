from struct import *

# DRTP header: sequence number, ack number, flags, window size
# I = 4 bytes (unsigned int), H = 2 bytes (unsigned short)
header_format = '!IIHH'  # total 12 bytes

# Optional: print header size
print(f"size of the header = {calcsize(header_format)}")

def create_packet(seq, ack, flags, win, data):
    header = pack(header_format, seq, ack, flags, win)
    packet = header + data
    
    return packet

def parse_header(header):
    return unpack(header_format, header[:12])

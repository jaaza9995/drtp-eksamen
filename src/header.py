from struct import pack, unpack, calcsize

# DRTP-header på 8 byte: 2 byte per felt
# Rekkefølge: Sekvensnummer, ACK-nummer, flagg, mottakervindu
header_format = '!HHHH'

def create_packet(seq, ack, flags, win, data=b''):
    # Lager en pakke ved å pakke header og legge til data
    header = pack(header_format, seq, ack, flags, win)
    return header + data

def parse_header(packet):
    # Leser de første 8 bytene og returnerer som 4 verdier
    return unpack(header_format, packet[:8])

def parse_flags(flags):
    # Tolker flaggene: bruker bitmasker for å hente ut SYN, ACK og FIN
    syn = flags & (1 << 3)
    ack = flags & (1 << 2)
    fin = flags & (1 << 1)
    return syn, ack, fin

def get_header_size():
    # Returnerer hvor mange byte headeren er
    return calcsize(header_format)

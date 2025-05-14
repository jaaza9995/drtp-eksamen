# application.py

import argparse
from drtp_client import run_client
from drtp_server import run_server

def main():
    parser = argparse.ArgumentParser(description="DRTP File Transfer Protocol")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-s", "--server", action="store_true", help="Run as DRTP server")
    mode.add_argument("-c", "--client", action="store_true", help="Run as DRTP client")

    parser.add_argument("-i", "--ip", type=str, required=True, help="IP address to bind/connect")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port number")
    parser.add_argument("-f", "--file", type=str, required=False, help="File to send/receive")
    parser.add_argument("-w", "--window", type=int, default=5, help="Sender window size (client only)")
    parser.add_argument("-d", "--discard", type=int, default=None, help="Drop packet with sequence number (server only)")

    args = parser.parse_args()

    if args.server:
        run_server(ip=args.ip, port=args.port, destination_file="received.jpg", discard_seq=args.discard)

    elif args.client:
        filename = args.file if args.file else "iceland-safiqul.jpg"
        run_client(ip=args.ip, port=args.port, filename=filename, window_size=args.window)


if __name__ == "__main__":
    main()

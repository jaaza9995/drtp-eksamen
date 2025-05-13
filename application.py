import argparse
from drtp_client import run_client
from drtp_server import run_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--client", action="store_true", help="Run as client")
    parser.add_argument("-s", "--server", action="store_true", help="Run as server")
    parser.add_argument("-i", "--ip", type=str, required=True, help="IP address")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port")
    parser.add_argument("-f", "--file", type=str, help="File to send (client only)")
    parser.add_argument("-w", "--window", type=int, default=4, help="Window size (client only)")

    args = parser.parse_args()

    if args.client:
        run_client(args.ip, args.port, args.file, args.window)
    elif args.server:
        run_server(args.ip, args.port)

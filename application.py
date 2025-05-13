import argparse
from drtp_client import run_client
from drtp_server import run_server

def main():
    parser = argparse.ArgumentParser(description="DRTP File Transfer")
    parser.add_argument('-s', '--server', action='store_true', help='Start server mode')
    parser.add_argument('-c', '--client', action='store_true', help='Start client mode')
    parser.add_argument('-i', '--ip', type=str, required=True, help='IP address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port number')
    parser.add_argument('-f', '--file', type=str, help='File to send (client only)')

    args = parser.parse_args()

    if args.server:
        run_server(args.ip, args.port)
    elif args.client:
        if not args.file:
            print("Error: client mode requires -f <filename>")
            return
        run_client(args.ip, args.port, args.file)
    else:
        print("Error: Must specify either --server or --client")

if __name__ == '__main__':
    main()

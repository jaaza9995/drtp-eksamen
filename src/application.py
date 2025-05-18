import argparse
from drtp_client import run_client
from drtp_server import run_server

def main():
    # Oppretter en parser for kommandolinjeargumenter
    parser = argparse.ArgumentParser(description="DRTP File Transfer Protocol")

    # Brukeren må velge enten server eller klient (ikke begge)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-s", "--server", action="store_true", help="Kjør som DRTP-server")
    mode.add_argument("-c", "--client", action="store_true", help="Kjør som DRTP-klient")

    # Felles argumenter
    # IP-adressen klienten skal koble til eller serveren skal binde seg til
    parser.add_argument("-i", "--ip", type=str, required=True, help="IP-adresse for binding/tilkobling")

    # Portnummeret som skal brukes for kommunikasjon
    parser.add_argument("-p", "--port", type=int, required=True, help="Portnummer")

    # Navn på fil som skal sendes (klient) eller mottas (server)
    parser.add_argument("-f", "--file", type=str, required=False, help="Fil som skal sendes/mottas")

    # Hvor mange pakker klienten kan sende uten å vente på ACK (vindusstørrelse)
    parser.add_argument("-w", "--window", type=int, default=5, help="Senderens vindusstørrelse (kun klient)")

    # Hvis oppgitt: serveren dropper pakken med dette sekvensnummeret én gang
    parser.add_argument("-d", "--discard", type=int, default=None, help="Dropp pakke med sekvensnummer (kun server)")

    # Parser kommandolinjeargumentene og lagrer dem i 'args'
    args = parser.parse_args()


    # Kjører som server
    if args.server:
        run_server(ip=args.ip, port=args.port, destination_file="received.jpg", discard_seq=args.discard)

    # Kjører som klient
    elif args.client:
        filename = args.file if args.file else "iceland-safiqul.jpg"
        run_client(ip=args.ip, port=args.port, filename=filename, window_size=args.window)


# Kjører main-funksjonen hvis scriptet startes direkte
if __name__ == "__main__":
    main()

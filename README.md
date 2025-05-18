 ## Hvordan kjøre application.py:

 application.py fungerer som startpunktet for både klient og server. Du må spesifisere om du vil starte som klient eller server med kommandolinjeflagg.

  ## Kjøring i vanlig terminal ##

**Starte som server**
    python3 application.py -s -i <egen_ip> -p <port> -d <sekvensnummer>

    Parametere:
        -s eller --server: Angir at du vil kjøre som server
        -i: IP-adressen serveren skal binde seg til (f.eks. 10.0.1.1)
        -p: Portnummer som serveren skal lytte på
        -d eller --discard: (valgfri) Sekvensnummer som skal droppes én gang for testformål


 **Starte som klient**
    python3 application.py -c -i <server_ip> -p <port> -f <filnavn> -w <vindusstørrelse>
    
    Parametere:  
        -c eller --client: Angir at du vil kjøre som klient
        -i: IP-adressen til serveren (f.eks. 10.0.1.2)
        -p: Portnummer som serveren lytter på
        -f: Filen som skal sendes (standard: iceland-safiqul.jpg)
        -w: (valgfri) Sliding window-størrelse (standard: 5)

    
     Output
        Klienten skriver status til terminalen og viser throughput til slutt.
        Serveren lagrer filen som received.jpg og viser hvilke pakker som mottas og bekreftes.


## Kjøring i Mininet ##
For å teste løsningen din i et simulert nettverk bruker vi Mininet sammen med `simple-topo.py`. Følg disse stegene:

1. **Plasser alle nødvendige filer i Mininet-miljøet.**  
   Du må sørge for at følgende filer ligger i samme mappe:
   - `application.py`
   - `drtp_client.py`
   - `drtp_server.py`
   - `header.py`
   - `simple-topo.py`
   - `README.md`
   - En eksempel-fil som skal overføres (`iceland-safiqul.jpg`)

2. **Start Mininet-topologien.**  
   Åpne terminal og naviger til mappen som inneholder `simple-topo.py`. Kjør følgende kommando:
   sudo mn
   
    -- Om du ikke vet ip-adressen din kan du skrive inn i minint terminalen:
        ifconfig 
    
    -- Videre skal du åpne terminalene for klienten og serveren slikt:
        xterm h1 h2

    -- start ved å skrive inn på serveren:
    python3 application.py -s -i <egen_ip> -p <port> -d <sekvensnummer>

    -- Når du har fått svar som indikerer at den er klar kan du starte klienten: 
    python3 application.py -c -i <server_ip> -p <port> -f <filnavn> -w <vindusstørrelse>
      
**Husk**
    -- Klienten skal skrives inn på h1 og serveren på h2
>**Tips:** Husk at serveren må startes før klienten, ellers får du timeout.



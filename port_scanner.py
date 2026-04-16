import socket
import threading
import argparse
from queue import Queue
import time

# -- Codes de couleur --
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"

# Dictionnaire des ports communs et de leurs services associes
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    445: "SMB", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Proxy"
}


def print_banner():
    """Affiche une banniere stylisee au demarrage du scanneur."""
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|           SCANNEUR DE PORTS TCP                     |" + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|             Formation Ingenieur                     |" + COLOR_RESET)
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)


def scan_port(target, port, timeout, open_ports, lock):
    """
    Tente de se connecter a un port specifique sur la cible.

    Args:
        target (str)    : L'adresse IP de la cible (deja resolue).
        port (int)      : Le numero du port a scanner.
        timeout (float) : Le delai d'attente maximum pour la connexion (secondes).
        open_ports (list): Liste partagee pour stocker les ports ouverts.
        lock (Lock)     : Verrou pour eviter les conflits d'ecriture entre threads.
    """
    try:
        # Creation d'un socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # connect_ex retourne 0 si la connexion reussit (port ouvert)
        result = sock.connect_ex((target, port))

        if result == 0:
            service = COMMON_PORTS.get(port, "Inconnu")
            with lock:
                print(f"{COLOR_GREEN}[+] Port {port:5d}/TCP  OUVERT  (Service: {service}){COLOR_RESET}")
            open_ports.append(port)

        sock.close()
    except Exception:
        pass


def worker(target, port_queue, timeout, open_ports, lock):
    """
    Fonction executee par chaque thread.
    Recupere des ports dans la file d'attente et les scanne jusqu'a epuisement.
    """
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(target, port, timeout, open_ports, lock)
        port_queue.task_done()


def parse_ports(ports_arg):
    """
    Analyse l'argument de plage de ports.
    Accepte le format 'debut-fin' (ex: 1-1024) ou un port unique (ex: 80).

    Returns:
        tuple: (start_port, end_port)
    Raises:
        ValueError: si le format est invalide.
    """
    if '-' in ports_arg:
        parts = ports_arg.split('-')
        start_port = int(parts[0])
        end_port = int(parts[1])
    else:
        start_port = int(ports_arg)
        end_port = int(ports_arg)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        raise ValueError("Plage de ports hors limites (1-65535).")

    return start_port, end_port


def main():
    # --- Configuration des arguments en ligne de commande ---
    parser = argparse.ArgumentParser(
        description="Scanneur de ports TCP multi-thread a but educatif.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "target",
        help="Adresse IP ou nom de domaine a scanner\n(ex: 127.0.0.1 ou scanme.nmap.org)"
    )
    parser.add_argument(
        "-p", "--ports",
        help="Plage de ports a scanner (ex: 1-1024 ou 80). Par defaut: 1-1024",
        default="1-1024"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        help="Nombre de threads a utiliser. Par defaut: 100",
        default=100
    )
    parser.add_argument(
        "--timeout",
        type=float,
        help="Delai d'attente par connexion en secondes. Par defaut: 1.0",
        default=1.0
    )

    args = parser.parse_args()

    # --- Validation de la plage de ports ---
    try:
        start_port, end_port = parse_ports(args.ports)
    except (ValueError, IndexError):
        print(f"{COLOR_RED}Erreur: Format de plage de ports invalide. Utilisez 'debut-fin' (ex: 1-1024).{COLOR_RESET}")
        return

    # --- Resolution DNS ---
    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"{COLOR_RED}Erreur: Impossible de resoudre le nom d'hote '{args.target}'.{COLOR_RESET}")
        return

    # --- Affichage des informations de scan ---
    print_banner()
    print(f"  Cible         : {COLOR_YELLOW}{args.target} ({target_ip}){COLOR_RESET}")
    print(f"  Plage de ports: {COLOR_YELLOW}{start_port} - {end_port}{COLOR_RESET}")
    print(f"  Threads       : {COLOR_YELLOW}{args.threads}{COLOR_RESET}")
    print(f"  Timeout       : {COLOR_YELLOW}{args.timeout}s{COLOR_RESET}")
    print(COLOR_CYAN + "-" * 55 + COLOR_RESET)
    print(COLOR_BLUE + "Demarrage du scan...\n" + COLOR_RESET)

    start_time = time.time()

    # --- Remplissage de la file d'attente ---
    port_queue = Queue()
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    open_ports = []
    lock = threading.Lock()  # Verrou pour l'affichage concurrent
    threads_list = []

    # --- Creation et demarrage des threads ---
    for _ in range(min(args.threads, end_port - start_port + 1)):
        t = threading.Thread(
            target=worker,
            args=(target_ip, port_queue, args.timeout, open_ports, lock)
        )
        t.daemon = True  # Le thread s'arrete si le programme principal se termine
        t.start()
        threads_list.append(t)

    # --- Attente de la fin du traitement ---
    port_queue.join()

    duration = time.time() - start_time

    # --- Affichage du resume ---
    print(COLOR_CYAN + "\n" + "-" * 55 + COLOR_RESET)
    print(f"{COLOR_BLUE}Scan termine en {duration:.2f} secondes.{COLOR_RESET}")
    print(f"{COLOR_BLUE}Ports ouverts trouves : {len(open_ports)}{COLOR_RESET}")

    if open_ports:
        print(COLOR_BLUE + "\nResume des ports ouverts :" + COLOR_RESET)
        print(f"  {COLOR_BOLD}{'PORT':<10} {'PROTOCOLE':<10} {'SERVICE'}{COLOR_RESET}")
        print(f"  {COLOR_BOLD}{'-'*8:<10} {'-'*8:<10} {'-'*15}{COLOR_RESET}")
        for port in sorted(open_ports):
            service = COMMON_PORTS.get(port, "Inconnu")
            print(f"  {COLOR_GREEN}{port:<10} {'TCP':<10} {service}{COLOR_RESET}")
    else:
        print(f"{COLOR_YELLOW}Aucun port ouvert detecte dans la plage specifiee.{COLOR_RESET}")

    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)


if __name__ == "__main__":
    main()

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


def estimate_rtt(target_ip, common_ports=[80, 443, 22, 53], default_timeout=1.0):
    """
    Estime le Round Trip Time (RTT) moyen vers la cible en tentant de se connecter
    a quelques ports communs. Utilise le timeout par defaut si aucune connexion
    ne reussit ou si la cible est inaccessible.
    """
    rtts = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            start_time = time.time()
            result = sock.connect_ex((target_ip, port))
            end_time = time.time()
            sock.close()

            if result == 0:
                rtts.append(end_time - start_time)
                break 
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass

    if rtts:
        # On multiplie par 3 pour la tolerance face aux variations reseau
        estimated_timeout = max(0.1, (sum(rtts) / len(rtts)) * 3)
        return min(estimated_timeout, 5.0)
    return default_timeout


def scan_port(target, port, timeout, open_ports, lock):
    """Tente de se connecter a un port specifique sur la cible."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))

        if result == 0:
            service = COMMON_PORTS.get(port, "Inconnu")
            with lock:
                print(f"{COLOR_GREEN}[+] Port {port:5d}/TCP  OUVERT  (Service: {service}){COLOR_RESET}")
            open_ports.append(port)
        sock.close()
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    except Exception as e:
        with lock:
            print(f"{COLOR_RED}[-] Erreur inattendue sur port {port}: {e}{COLOR_RESET}")


def worker(target, port_queue, timeout, open_ports, lock):
    """Fonction executee par chaque thread."""
    while not port_queue.empty():
        try:
            port = port_queue.get(timeout=1.0)
            scan_port(target, port, timeout, open_ports, lock)
            port_queue.task_done()
        except:
            break


def parse_ports(ports_arg):
    """Analyse l'argument de plage de ports."""
    if '-' in ports_arg:
        parts = ports_arg.split('-')
        start_port = int(parts[0])
        end_port = int(parts[1])
    else:
        start_port = int(ports_arg)
        end_port = int(ports_arg)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        raise ValueError("Plage de ports hors limites.")
    return start_port, end_port


def main():
    parser = argparse.ArgumentParser(
        description="Scanneur de ports TCP multi-thread a but educatif.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("target", help="Adresse IP ou nom de domaine")
    parser.add_argument("-p", "--ports", help="Plage de ports (ex: 1-1024)", default="1-1024")
    parser.add_argument("-t", "--threads", type=int, help="Nombre de threads (defaut: 100)", default=100)
    parser.add_argument("--timeout", type=float, help="Timeout manuel (secondes)", default=None)

    args = parser.parse_args()

    try:
        start_port, end_port = parse_ports(args.ports)
    except (ValueError, IndexError):
        print(f"{COLOR_RED}Erreur: Format de ports invalide.{COLOR_RESET}")
        sys.exit(1)

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"{COLOR_RED}Erreur: Impossible de resoudre '{args.target}'.{COLOR_RESET}")
        sys.exit(1)

    scan_timeout = args.timeout
    if scan_timeout is None:
        print(f"{COLOR_BLUE}Estimation du RTT pour un timeout optimal...{COLOR_RESET}")
        scan_timeout = estimate_rtt(target_ip)
        print(f"{COLOR_BLUE}Timeout de scan estime : {scan_timeout:.2f}s{COLOR_RESET}")
    else:
        print(f"{COLOR_BLUE}Timeout defini par l'utilisateur : {scan_timeout:.2f}s{COLOR_RESET}")

    print_banner()
    print(f"  Cible         : {COLOR_YELLOW}{args.target} ({target_ip}){COLOR_RESET}")
    print(f"  Plage de ports: {COLOR_YELLOW}{start_port} - {end_port}{COLOR_RESET}")
    print(f"  Threads       : {COLOR_YELLOW}{args.threads}{COLOR_RESET}")
    print(f"  Timeout       : {COLOR_YELLOW}{scan_timeout:.2f}s{COLOR_RESET}")
    print(COLOR_CYAN + "-" * 55 + COLOR_RESET)
    print(COLOR_BLUE + "Demarrage du scan...\n" + COLOR_RESET)

    start_time = time.time()
    port_queue = Queue()
    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    open_ports = []
    lock = threading.Lock()
    threads_list = []

    num_threads = min(args.threads, end_port - start_port + 1)
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(target_ip, port_queue, scan_timeout, open_ports, lock))
        t.daemon = True
        t.start()
        threads_list.append(t)

    port_queue.join()
    duration = time.time() - start_time

    print(COLOR_CYAN + "\n" + "-" * 55 + COLOR_RESET)
    print(f"{COLOR_BLUE}Scan termine en {duration:.2f} secondes.{COLOR_RESET}")
    print(f"{COLOR_BLUE}Ports ouverts trouves : {len(open_ports)}{COLOR_RESET}")

    if open_ports:
        print(COLOR_BLUE + "\nResume des ports ouverts :" + COLOR_RESET)
        header = f"  {COLOR_BOLD}{'PORT':<10} {'PROTOCOLE':<10} {'SERVICE'}{COLOR_RESET}"
        separator = f"  {COLOR_BOLD}{'-'*8:<10} {'-'*8:<10} {'-'*15}{COLOR_RESET}"
        print(header)
        print(separator)
        for port in sorted(open_ports):
            service = COMMON_PORTS.get(port, "Inconnu")
            print(f"  {COLOR_GREEN}{port:<10} {'TCP':<10} {service}{COLOR_RESET}")
    else:
        print(f"{COLOR_YELLOW}Aucun port ouvert detecte.{COLOR_RESET}")
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)

if __name__ == "__main__":
    main()

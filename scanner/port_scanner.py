import socket
import threading
import argparse
from queue import Queue, Empty
import time

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"

COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
    110: "POP3", 111: "RPC", 119: "NNTP", 123: "NTP", 135: "MS-RPC",
    139: "NetBIOS", 143: "IMAP", 161: "SNMP", 194: "IRC", 389: "LDAP",
    443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog", 587: "SMTP-TLS",
    636: "LDAPS", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
    2181: "Zookeeper", 2375: "Docker", 2376: "Docker-TLS", 3306: "MySQL",
    3389: "RDP", 4444: "Metasploit", 5000: "Flask/UPnP", 5432: "PostgreSQL",
    5672: "RabbitMQ", 5900: "VNC", 6379: "Redis", 6443: "Kubernetes",
    7000: "Cassandra", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "Jupyter",
    9000: "SonarQube", 9090: "Prometheus", 9200: "Elasticsearch",
    27017: "MongoDB", 27018: "MongoDB", 50070: "Hadoop",
}


def print_banner():
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|           SCANNEUR DE PORTS TCP                     |" + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|             Formation Ingenieur                     |" + COLOR_RESET)
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)


def estimate_rtt(target_ip, common_ports=[80, 443, 22, 53], default_timeout=1.0):
    """Estime le timeout optimal en mesurant le RTT vers la cible."""
    rtts = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            start = time.time()
            result = sock.connect_ex((target_ip, port))
            elapsed = time.time() - start
            sock.close()
            if result == 0:
                rtts.append(elapsed)
                break
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
    if rtts:
        return min(max(0.1, (sum(rtts) / len(rtts)) * 3), 5.0)
    return default_timeout


def scan_port(target, port, timeout, open_ports, lock):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((target, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Inconnu")
                with lock:
                    print(f"{COLOR_GREEN}[+] Port {port:5d}/TCP  OUVERT  (Service: {service}){COLOR_RESET}")
                    open_ports.append(port)
        finally:
            sock.close()
    except Exception:
        pass


def worker(target, port_queue, timeout, open_ports, lock):
    while True:
        try:
            port = port_queue.get_nowait()
        except Empty:
            break
        scan_port(target, port, timeout, open_ports, lock)
        port_queue.task_done()


def parse_ports(ports_arg):
    if '-' in ports_arg:
        parts = ports_arg.split('-')
        if len(parts) != 2:
            raise ValueError("Format invalide.")
        start_port = int(parts[0])
        end_port = int(parts[1])
    else:
        start_port = int(ports_arg)
        end_port = int(ports_arg)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        raise ValueError("Plage de ports hors limites (1-65535).")

    return start_port, end_port


def main():
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
        help="Timeout par connexion en secondes. Par defaut: auto (estimation RTT)",
        default=None
    )

    args = parser.parse_args()

    if args.threads < 1:
        print(f"{COLOR_RED}Erreur: Le nombre de threads doit etre >= 1.{COLOR_RESET}")
        return
    if args.timeout is not None and args.timeout <= 0:
        print(f"{COLOR_RED}Erreur: Le timeout doit etre > 0.{COLOR_RESET}")
        return

    try:
        start_port, end_port = parse_ports(args.ports)
    except (ValueError, IndexError):
        print(f"{COLOR_RED}Erreur: Format de plage de ports invalide. Utilisez 'debut-fin' (ex: 1-1024).{COLOR_RESET}")
        return

    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"{COLOR_RED}Erreur: Impossible de resoudre le nom d'hote '{args.target}'.{COLOR_RESET}")
        return

    if args.timeout is None:
        print(f"{COLOR_BLUE}Estimation du RTT pour un timeout optimal...{COLOR_RESET}")
        scan_timeout = estimate_rtt(target_ip)
        print(f"{COLOR_BLUE}Timeout estime : {scan_timeout:.2f}s{COLOR_RESET}")
    else:
        scan_timeout = args.timeout

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
    try:
        for _ in range(num_threads):
            t = threading.Thread(
                target=worker,
                args=(target_ip, port_queue, scan_timeout, open_ports, lock)
            )
            t.daemon = True
            t.start()
            threads_list.append(t)

        port_queue.join()
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Scan interrompu par l'utilisateur.{COLOR_RESET}")

    duration = time.time() - start_time

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

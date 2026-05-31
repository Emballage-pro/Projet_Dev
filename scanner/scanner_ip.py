import subprocess
import threading
import argparse
import ipaddress
from queue import Queue, Empty
import time

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"


def print_banner():
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|           SCANNEUR D'ADRESSES IP                   |" + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|             Formation Ingenieur                     |" + COLOR_RESET)
    print(COLOR_CYAN + "=" * 55 + COLOR_RESET)


def ping_ip(ip_address, active_ips, lock):
    """Ping une adresse IP pour vérifier si elle est active."""
    # Sur macOS/Linux, on utilise 'ping' avec timeout
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1000", str(ip_address)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=3
    )
    if result.returncode == 0:
        with lock:
            print(f"{COLOR_GREEN}[+] {str(ip_address):<15} ACTIVE{COLOR_RESET}")
            active_ips.append(str(ip_address))
    # Removed inactive and error prints


def worker(ip_queue, active_ips, lock):
    """Worker thread pour traiter les IPs de la queue."""
    while True:
        try:
            ip = ip_queue.get_nowait()
        except Empty:
            break
        ping_ip(ip, active_ips, lock)
        ip_queue.task_done()


def parse_network(network_arg):
    """Parse une notation CIDR ou une plage d'IPs."""
    try:
        network = ipaddress.ip_network(network_arg, strict=False)
        return list(network.hosts()) if network.num_addresses > 2 else list(network)
    except ValueError:
        raise ValueError(f"Format reseau invalide: {network_arg}")


def main():
    parser = argparse.ArgumentParser(
        description="Scanneur d'adresses IP pour detecter les machines actives.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "network",
        help="Reseau a scanner en notation CIDR\n(ex: 192.168.1.0/24 ou 10.0.0.0/25)"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        help="Nombre de threads a utiliser. Par defaut: 50",
        default=50
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Mode silencieux (affiche seulement les IPs actives)"
    )

    args = parser.parse_args()

    if args.threads < 1:
        print(f"{COLOR_RED}Erreur: Le nombre de threads doit etre >= 1.{COLOR_RESET}")
        return

    try:
        ips_to_scan = parse_network(args.network)
    except ValueError as e:
        print(f"{COLOR_RED}Erreur: {e}{COLOR_RESET}")
        return

    if not args.quiet:
        print_banner()
        print(f"  Reseau        : {COLOR_YELLOW}{args.network}{COLOR_RESET}")
        print(f"  Nombre d'IPs  : {COLOR_YELLOW}{len(ips_to_scan)}{COLOR_RESET}")
        print(f"  Threads       : {COLOR_YELLOW}{args.threads}{COLOR_RESET}")
        print(COLOR_CYAN + "-" * 55 + COLOR_RESET)
        print(COLOR_BLUE + "Demarrage du scan...\n" + COLOR_RESET)

    start_time = time.time()

    ip_queue = Queue()
    for ip in ips_to_scan:
        ip_queue.put(ip)

    active_ips = []
    lock = threading.Lock()
    threads_list = []

    num_threads = min(args.threads, len(ips_to_scan))
    try:
        for _ in range(num_threads):
            t = threading.Thread(
                target=worker,
                args=(ip_queue, active_ips, lock)
            )
            t.daemon = True
            t.start()
            threads_list.append(t)

        ip_queue.join()
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}Scan interrompu par l'utilisateur.{COLOR_RESET}")

    duration = time.time() - start_time

    if not args.quiet:
        print(COLOR_CYAN + "\n" + "-" * 55 + COLOR_RESET)
    print(f"{COLOR_BLUE}Scan termine en {duration:.2f} secondes.{COLOR_RESET}")
    print(f"{COLOR_BLUE}Machines actives trouvees : {len(active_ips)}{COLOR_RESET}")

    # Removed summary list of active IPs

    if not args.quiet:
        print(COLOR_CYAN + "=" * 55 + COLOR_RESET)


if __name__ == "__main__":
    main()

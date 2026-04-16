#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║         gimme_xmr — Setup Wizard         ║
╚══════════════════════════════════════════╝
"""

import sys
import os
import re
import time
import socket
import subprocess
import platform
import shutil


# ─── ANSI colors ────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    GRAY   = "\033[90m"


# ─── Helpers ────────────────────────────────────────────────────────────────

def banner():
    print(f"""
{C.CYAN}{C.BOLD}
  ██████  ██ ███    ███ ███    ███ ███████      ██   ██ ███    ███ ██████
 ██       ██ ████  ████ ████  ████ ██           ╚██╗██╔╝████  ████ ██   ██
 ██   ███ ██ ██ ████ ██ ██ ████ ██ █████         ╚███╔╝ ██ ████ ██ ██████
 ██    ██ ██ ██  ██  ██ ██  ██  ██ ██            ██╔██╗ ██  ██  ██ ██   ██
  ██████  ██ ██      ██ ██      ██ ███████      ██╔╝╚██╗██      ██ ██   ██
{C.RESET}
{C.GRAY}  ──────────────────────────────────────────────────────────────
  Setup Wizard  v1.0.0
  ──────────────────────────────────────────────────────────────{C.RESET}
""")


def step(num: int, total: int, label: str):
    bar = f"[{num}/{total}]"
    print(f"\n{C.BOLD}{C.CYAN}{bar}{C.RESET} {C.WHITE}{label}{C.RESET}")


def ok(msg: str):
    print(f"  {C.GREEN}✔{C.RESET}  {msg}")


def warn(msg: str):
    print(f"  {C.YELLOW}⚠{C.RESET}  {msg}")


def error(msg: str):
    print(f"  {C.RED}✖{C.RESET}  {msg}")


def info(msg: str):
    print(f"  {C.GRAY}→{C.RESET}  {msg}")


def progress(label: str, duration: float = 1.2, steps: int = 30):
    """Simple ASCII progress bar."""
    print(f"  {C.DIM}{label}{C.RESET}")
    delay = duration / steps
    bar = ""
    for i in range(steps + 1):
        filled = "█" * i
        empty  = "░" * (steps - i)
        pct    = int(i / steps * 100)
        print(f"\r  [{C.CYAN}{filled}{C.RESET}{empty}] {pct:3d}%", end="", flush=True)
        time.sleep(delay)
    print()


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{C.GRAY}{default}{C.RESET}]" if default else ""
    try:
        val = input(f"  {C.YELLOW}?{C.RESET}  {prompt}{hint}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        abort()
    return val if val else default


def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        val = input(f"  {C.YELLOW}?{C.RESET}  {prompt} [{hint}]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        abort()
    if val == "":
        return default
    return val in ("y", "yes", "oui", "o")


def abort():
    print(f"\n{C.RED}  Installation annulée.{C.RESET}\n")
    sys.exit(1)


# ─── Validation ─────────────────────────────────────────────────────────────

def validate_ip(ip: str) -> bool:
    """Validate an IPv4 or IPv6 address."""
    ip = ip.strip()
    # IPv4
    ipv4 = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    if ipv4.match(ip):
        parts = ip.split(".")
        return all(0 <= int(p) <= 255 for p in parts)
    # IPv6
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except (socket.error, OSError):
        pass
    return False


def resolve_hostname(host: str) -> str | None:
    """Try to resolve a hostname to an IP."""
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def test_reachability(ip: str, port: int = 80, timeout: float = 3.0) -> bool:
    """Test if the host is reachable on a given port."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


# ─── System checks ──────────────────────────────────────────────────────────

def check_python_version():
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 8):
        error(f"Python 3.8+ requis (version actuelle : {major}.{minor})")
        sys.exit(1)
    ok(f"Python {major}.{minor} détecté")


def check_dependencies(deps: list[str]) -> list[str]:
    """Return list of missing system commands."""
    missing = []
    for dep in deps:
        if shutil.which(dep) is None:
            missing.append(dep)
        else:
            ok(f"'{dep}' trouvé")
    return missing


def check_disk_space(path: str = ".", min_mb: int = 200) -> bool:
    try:
        stat = shutil.disk_usage(path)
        free_mb = stat.free // (1024 * 1024)
        if free_mb < min_mb:
            warn(f"Espace disque faible : {free_mb} MB disponibles (minimum requis : {min_mb} MB)")
            return False
        ok(f"Espace disque suffisant : {free_mb} MB disponibles")
        return True
    except Exception:
        warn("Impossible de vérifier l'espace disque")
        return True


# ─── Installation steps ─────────────────────────────────────────────────────

def gather_ip() -> str:
    """Interactively ask for and validate the target IP address."""
    print()
    print(f"  {C.DIM}Entrez l'adresse IP (ou le nom d'hôte) de la machine cible.{C.RESET}")
    print(f"  {C.DIM}Exemple : 192.168.1.100  |  10.0.0.5  |  monserveur.local{C.RESET}")
    print()

    while True:
        raw = ask("Adresse IP cible")
        if not raw:
            error("L'adresse IP ne peut pas être vide.")
            continue

        # Try direct IP first
        if validate_ip(raw):
            ok(f"Adresse IP valide : {C.CYAN}{raw}{C.RESET}")
            return raw

        # Try hostname resolution
        info(f"'{raw}' n'est pas une IP brute, tentative de résolution DNS…")
        resolved = resolve_hostname(raw)
        if resolved:
            ok(f"Nom d'hôte résolu : {C.CYAN}{raw}{C.RESET} → {C.CYAN}{resolved}{C.RESET}")
            return resolved

        error(f"'{raw}' n'est pas une adresse IP valide et ne peut pas être résolue.")
        if not confirm("Réessayer ?"):
            abort()


def gather_config(ip: str) -> dict:
    """Collect additional configuration from the user."""
    print()
    print(f"  {C.DIM}Configuration avancée (appuyez sur Entrée pour garder les valeurs par défaut){C.RESET}")
    print()

    port     = ask("Port de connexion", default="22")
    user     = ask("Utilisateur distant", default="root")
    inst_dir = ask("Répertoire d'installation distant", default="/opt/gimme_xmr")
    log_dir  = ask("Répertoire de logs local", default="./logs")

    return {
        "ip":       ip,
        "port":     port,
        "user":     user,
        "inst_dir": inst_dir,
        "log_dir":  log_dir,
    }


def display_summary(cfg: dict):
    print(f"""
{C.BOLD}  Récapitulatif de la configuration :{C.RESET}
  {C.GRAY}┌──────────────────────────────────────────┐{C.RESET}
  {C.GRAY}│{C.RESET}  IP cible       : {C.CYAN}{cfg['ip']:<24}{C.RESET}{C.GRAY}│{C.RESET}
  {C.GRAY}│{C.RESET}  Port           : {C.CYAN}{cfg['port']:<24}{C.RESET}{C.GRAY}│{C.RESET}
  {C.GRAY}│{C.RESET}  Utilisateur    : {C.CYAN}{cfg['user']:<24}{C.RESET}{C.GRAY}│{C.RESET}
  {C.GRAY}│{C.RESET}  Répertoire     : {C.CYAN}{cfg['inst_dir']:<24}{C.RESET}{C.GRAY}│{C.RESET}
  {C.GRAY}│{C.RESET}  Logs locaux    : {C.CYAN}{cfg['log_dir']:<24}{C.RESET}{C.GRAY}│{C.RESET}
  {C.GRAY}└──────────────────────────────────────────┘{C.RESET}""")


def create_local_dirs(cfg: dict):
    log_dir = cfg["log_dir"]
    os.makedirs(log_dir, exist_ok=True)
    ok(f"Répertoire de logs créé : {log_dir}")


def write_config_file(cfg: dict):
    cfg_path = os.path.join(cfg["log_dir"], "gimme_xmr.conf")
    lines = [
        "# gimme_xmr — configuration générée automatiquement",
        f"TARGET_IP={cfg['ip']}",
        f"TARGET_PORT={cfg['port']}",
        f"REMOTE_USER={cfg['user']}",
        f"INSTALL_DIR={cfg['inst_dir']}",
        f"LOG_DIR={cfg['log_dir']}",
    ]
    with open(cfg_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    ok(f"Fichier de configuration écrit : {cfg_path}")
    return cfg_path


def simulate_remote_install(cfg: dict):
    """
    Placeholder for the actual remote installation logic.
    Replace the body of this function with real SSH / Ansible / API calls.
    """
    tasks = [
        ("Connexion à la machine distante",          0.8),
        ("Vérification de l'environnement distant",  1.0),
        ("Transfert des fichiers",                   1.5),
        ("Installation des dépendances distantes",   2.0),
        ("Configuration du service",                 1.2),
        ("Démarrage du service gimme_xmr",           0.9),
        ("Vérification finale",                      0.7),
    ]

    for label, duration in tasks:
        progress(label, duration=duration)
        ok(label)


# ─── Main flow ───────────────────────────────────────────────────────────────

def main():
    banner()

    TOTAL_STEPS = 5

    # ── Step 1 : system checks ───────────────────────────────────────────────
    step(1, TOTAL_STEPS, "Vérification du système")
    check_python_version()
    check_disk_space()
    sys_deps = ["ssh", "scp"]
    missing = check_dependencies(sys_deps)
    if missing:
        warn(f"Outils manquants : {', '.join(missing)}")
        warn("Certaines fonctionnalités peuvent être limitées.")

    # ── Step 2 : gather IP ───────────────────────────────────────────────────
    step(2, TOTAL_STEPS, "Adresse IP de la machine cible")
    ip = gather_ip()

    # Test reachability (non-blocking warning)
    info(f"Test de connectivité vers {ip}…")
    reachable = test_reachability(ip, port=22)
    if reachable:
        ok("Hôte joignable sur le port 22")
    else:
        warn("L'hôte semble inaccessible sur le port 22.")
        warn("Vérifiez que la machine est allumée et que le pare-feu est ouvert.")
        if not confirm("Continuer quand même ?", default=False):
            abort()

    # ── Step 3 : configuration ───────────────────────────────────────────────
    step(3, TOTAL_STEPS, "Configuration de l'installation")
    cfg = gather_config(ip)
    display_summary(cfg)
    print()
    if not confirm("Confirmer et lancer l'installation ?"):
        abort()

    # ── Step 4 : local setup ─────────────────────────────────────────────────
    step(4, TOTAL_STEPS, "Préparation locale")
    create_local_dirs(cfg)
    cfg_file = write_config_file(cfg)

    # ── Step 5 : remote install ──────────────────────────────────────────────
    step(5, TOTAL_STEPS, "Installation sur la machine distante")
    print(f"\n  {C.DIM}Installation de gimme_xmr sur {C.CYAN}{ip}{C.RESET}{C.DIM}…{C.RESET}\n")
    simulate_remote_install(cfg)

    # ── Done ─────────────────────────────────────────────────────────────────
    print(f"""
{C.GREEN}{C.BOLD}
  ╔══════════════════════════════════════════╗
  ║   ✔  Installation terminée avec succès  ║
  ╚══════════════════════════════════════════╝
{C.RESET}
  {C.GRAY}Application :{C.RESET}  gimme_xmr
  {C.GRAY}Cible        :{C.RESET}  {C.CYAN}{cfg['ip']}:{cfg['port']}{C.RESET}
  {C.GRAY}Config       :{C.RESET}  {cfg_file}

  {C.DIM}Merci d'avoir utilisé le setup gimme_xmr.{C.RESET}
""")


if __name__ == "__main__":
    # Windows : activer les codes ANSI
    if platform.system() == "Windows":
        os.system("color")
    main()
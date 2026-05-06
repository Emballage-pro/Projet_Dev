import os, shutil, random
from pathlib import Path
from datetime import datetime

def get_target_directory():
    """Demande le dossier au début (seule interaction utilisateur)"""
    while True:
        dir_path = input("\n📁 Répertoire de test : ").strip().strip('"')
        if not os.path.isdir(dir_path): continue
        return Path(dir_path)

def create_stealth_backup(target_dir: Path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = target_dir / f".syscache_{timestamp}_{random.randint(1000,9999)}"
    backup_dir.mkdir(exist_ok=True)
    mapping = {}
    for f in target_dir.glob("*"):
        if f.is_file():
            bkp_path = backup_dir / f.name
            shutil.copy2(f, bkp_path)
            mapping[str(f)] = str(bkp_path)
    return backup_dir, mapping

def restore_files(mapping):
    for original, backup in mapping.items():
        shutil.copy2(backup, original)

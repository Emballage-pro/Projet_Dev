import base64

# Liste exacte de tes fichiers dans l'ordre
files = ['evasion.py', 'crypto_manager.py', 'file_system.py', 'ui.py', 'main.py']
full_code = ""

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        # On ajoute le contenu du fichier
        full_code += f.read() + "\n\n"

# On encode en base64 pour éviter les erreurs de caractères lors du transfert
encoded_payload = base64.b64encode(full_code.encode()).decode()

with open("payload.py", "w") as f:
    f.write(f"import base64\n\npayload = '{encoded_payload}'\n")
    f.write("exec(base64.b64decode(payload).decode())")

print("✅ payload.py a été créé ! Utilise ce fichier pour ton agent récursif.")

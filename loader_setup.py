import requests
import os
import sys

SERVER_IP = "1.2.3.4"
SERVER_PORT = 8080
FILE_NAME = "placeholder.replace"
DOWNLOAD_URL = f"http://{SERVER_IP}:{SERVER_PORT}/{FILE_NAME}"
SAVE_PATH = os.path.join(os.path.expanduser("~"), "Downloads", FILE_NAME)


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


def main():
    print("=" * 50)
    print("         LOADER SETUP")
    print("=" * 50)

    success = download_file(DOWNLOAD_URL, SAVE_PATH)

    if success:
        print("[+] Téléchargement terminé avec succès.")
        sys.exit(0)
    else:
        print("[-] Échec du téléchargement.")
        sys.exit(1)


if __name__ == "__main__":
    main()

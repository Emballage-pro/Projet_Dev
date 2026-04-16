import struct
import json
import os


PHLD_MAGIC = b"PHLD"
PHLD_VERSION = 1


def load_phld(filepath: str) -> dict:
    """
    Charge un fichier .phld et retourne son contenu sous forme de dictionnaire.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    with open(filepath, "rb") as f:
        # Vérification de l'en-tête magique
        magic = f.read(4)
        if magic != PHLD_MAGIC:
            raise ValueError(f"Format invalide : signature magique incorrecte ({magic})")

        # Lecture de la version
        version = struct.unpack(">H", f.read(2))[0]
        if version != PHLD_VERSION:
            raise ValueError(f"Version non supportée : {version}")

        # Lecture de la taille du payload
        payload_size = struct.unpack(">I", f.read(4))[0]

        # Lecture du payload JSON
        raw = f.read(payload_size)
        if len(raw) != payload_size:
            raise EOFError("Fichier tronqué : payload incomplet")

        data = json.loads(raw.decode("utf-8"))

    print(f"[PHLD] Fichier chargé avec succès : {filepath}")
    print(f"[PHLD] Version : {version} | Payload : {payload_size} octets")
    return data


def save_phld(filepath: str, data: dict) -> None:
    """
    Sauvegarde un dictionnaire dans un fichier .phld.
    """
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    with open(filepath, "wb") as f:
        f.write(PHLD_MAGIC)                          # Signature magique (4 octets)
        f.write(struct.pack(">H", PHLD_VERSION))     # Version (2 octets)
        f.write(struct.pack(">I", len(payload)))     # Taille du payload (4 octets)
        f.write(payload)                             # Données JSON

    print(f"[PHLD] Fichier sauvegardé : {filepath}")


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    sample_data = {
        "nom": "exemple",
        "valeur": 42,
        "tags": ["test", "phld", "loader"]
    }

    save_phld("placeholder.phld", sample_data)
    loaded = load_phld("placeholder.phld")
    print("[PHLD] Contenu chargé :", loaded)

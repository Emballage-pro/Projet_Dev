# Cybersecurity Lab – Network Recon & Malware Simulation PoC

>  FOR EDUCATIONAL PURPOSES ONLY  
> Ce projet a été réalisé dans un cadre scolaire, sur un environnement entièrement isolé (machines virtuelles).  
> Toute utilisation en dehors d'un environnement de test autorisé est strictement interdite.

---

##  Présentation

Ce projet est un logiciel simulant un ransomware (POC) développé laboratoire sécurisé dans le cadre d'un cours d'ingénierie.

L'objectif est de comprendre, de l'intérieur, les mécanismes utilisés par les logiciels malveillants modernes — reconnaissance réseau, chiffrement de fichiers, attaque applicative — afin de mieux les détecter et les contrer.

Le projet couvre deux grandes familles de techniques :
- Reconnaissance & énumération réseau (Blue Team / pentest)
- Simulation d'impact : ransomware PoC + clipboard hijacking (Red Team / awareness)

---

##  Environnement de test

Le projet a été entièrement développé et testé sur un lab VMware isolé :

| VM | Rôle |
|---|---|
| Kali Linux | Machine attaquante |
| Debian | Cible Linux |
| Windows 10 | Cible Windows |

Aucune machine réelle, aucun réseau externe n'a été impliqué.

---

##  Structure du projet

```
Projet_Dev/
├── scanner_ip.py       # Découverte d'hôtes actifs sur un réseau
├── port_scanner.py     # Scan de ports TCP avec détection de services
├── payload.py          # Simulateur de ransomware (chiffrement + UI)
├── iban-replacer.py    # PoC clipboard hijacking (IBAN)
└── Setup/              # Scripts d'installation de l'environnement
```

---

##  Module 1 – Scanner IP (`scanner_ip.py`)

Découverte d'hôtes actifs sur un réseau local via ICMP (ping sweep).

Fonctionnalités :
- Notation CIDR (`192.168.1.0/24`)
- Multi-threading configurable
- Affichage coloré des hôtes actifs
- Mode silencieux (`--quiet`)

Usage :
```bash
python scanner_ip.py 192.168.1.0/24 -t 50
```

Concepts couverts : protocole ICMP, adressage réseau, threading Python, `ipaddress`, `subprocess`

---

##  Module 2 – Scanner de ports (`port_scanner.py`)

Scan TCP multi-threadé avec identification automatique des services.

Fonctionnalités :
- Plage de ports configurable (ex: `1-1024`)
- Estimation automatique du timeout optimal via RTT
- Dictionnaire de ~50 services connus (SSH, HTTP, RDP, SMB, MySQL…)
- Résumé tabulaire des ports ouverts

Usage :
```bash
python port_scanner.py 192.168.1.10 -p 1-1024 -t 100
python port_scanner.py scanme.nmap.org -p 80
```

Concepts couverts : sockets TCP, threading, `argparse`, estimation RTT, reconnaissance de services

---

##  Module 3 – Ransomware Simulator (`payload.py`)

Simulation d'un ransomware sur une cible fixe et connue, avec restauration automatique des fichiers à la fin.

Ce que le simulateur fait :
- Chiffrement AES-GCM d'un fichier cible unique (hardcodé)
- Backup automatique avant chiffrement
- Interface graphique de rançon (Tkinter, plein écran, compte à rebours)
- Restauration complète des fichiers à la fermeture de l'UI
- Log de toutes les actions dans `/tmp/ransom.log`

Ce que le simulateur ne fait PAS :
-  Pas de chiffrement massif ou récursif de fichiers
-  Pas de communication avec un serveur externe
-  Pas de persistance après redémarrage
-  Pas de déploiement sur d'autres machines

Concepts couverts : cryptographie symétrique (AES-GCM), PBKDF2, `pywin32`, Tkinter, gestion de fichiers

Perspective Blue Team :
Ce module illustre pourquoi les sauvegardes hors-ligne, les EDR et la détection comportementale sont essentiels contre les ransomwares réels.

---

##  Module 4 – IBAN Clipboard Hijacker (`iban-replacer.py`)

PoC d'attaque de type *clipboard hijacking* ciblant les virements bancaires.

Fonctionnement :
- Surveillance continue du presse-papiers (Win32 API)
- Détection des IBANs via regex + validation **algorithme MOD-97**
- Remplacement par un IBAN de démonstration

Ce que ce PoC illustre :  
Des malwares financiers réels utilisent cette technique pour rediriger des virements à l'insu de l'utilisateur. La défense passe par la vérification manuelle des coordonnées bancaires avant tout virement.

Concepts couverts : `win32clipboard`, regex, validation MOD-97, monitoring de processus système

---

##  Perspective défensive (Blue Team)

Chaque module a été conçu avec une double lecture offensive/défensive :

| Attaque simulée | Contre-mesure illustrée |
|---|---|
| Scan réseau | Segmentation réseau, IDS/IPS |
| Scan de ports | Firewall, fermeture des ports inutiles |
| Ransomware | Sauvegardes 3-2-1, EDR, moindre privilège |
| Clipboard hijacking | Vérification manuelle des IBANs, antivirus |

---

##  Installation

```bash
git clone https://github.com/Emballage-pro/Projet_Dev.git
cd Projet_Dev
pip install -r requirements.txt  # cryptography, psutil, pywin32, paramiko
```

> Tester uniquement sur une machine personnelle ou une VM isolée.

---

##  Avertissement légal

L'auteur de ce projet décline toute responsabilité en cas d'utilisation malveillante.  
Ce code est fourni à des fins éducatives uniquement.  
L'usage de ces outils sur des systèmes sans autorisation explicite est illégal dans la plupart des pays.

Utilisation autorisée :
-  Recherche en cybersécurité
-  Environnement isolé (VM / sandbox)
-  Démonstrations pédagogiques

Utilisation interdite :
-  Production ou systèmes réels
-  Machines ne vous appartenant pas
-  Usage à des fins frauduleuses ou criminelles

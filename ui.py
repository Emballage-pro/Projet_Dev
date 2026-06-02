import tkinter as tk
from tkinter import messagebox

def fake_action(root):
 choice = messagebox.askyesno(
 "Simulation",
 "🔍 Êtes-vous sûr d'avoir rentré les bonnes coordonnées ?\n\n" 
 "Continuer ?"
 )
 if choice:
 # SI OUI → étape suivante
    messagebox.showerror(
 "Pop-up",
 "💰 L'argent a bien été envoyé à l'adresse indiquée ! 💰\n\n" 
 "Vos informations et dossiers seront débloqués après réception de la transaction.\n"
 "Cette étape prend généralement 30 minutes.\n\n"
 "Merci pour votre coopération.\n"
 "Ne fermez pas cette fenêtre avant la fin de la procédure."
 )
 else:
 # SI ANNULER → retour "home"
    messagebox.showinfo(
 "Annulé",
 "Retour à l'écran principal."
 )
 root.deiconify() # assure que la fenêtre reste ouverte

def create_ui():
 root = tk.Tk()
 root.title("GIMME XMR - Simulation")
 root.attributes('-fullscreen', True)
 root.configure(bg="#0f0f0f")
 root.resizable(False, False)

 ascii_banner = r"""
   ██████╗ ██╗███╗   ███╗███╗   ███╗███████╗
  ██╔════╝ ██║████╗ ████║████╗ ████║██╔════╝
  ██║  ███╗██║██╔████╔██║██╔████╔██║█████╗  
  ██║   ██║██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  
  ╚██████╔╝██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗
   ╚═════╝ ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝

           ╔══════════════════════╗
           ║     GIMME - XMR      ║
           ╚══════════════════════╝"""

 banner = tk.Label(
 root,
 text=ascii_banner,
 font=("Consolas", 10),
 fg="#00ff88",
 bg="#0f0f0f",
 justify="left"
 )
 banner.pack(pady=20)

 title = tk.Label(
 root,
 text="⚠️ Donnée Criptée - Aucune Erreur Détecté ⚠️",
 font=("Arial", 18, "bold"),
 fg="#ff3b3b",
 bg="#0f0f0f"
 )
 title.pack(pady=10)

 desc = tk.Label(
 root,
 text="Vos fichiers sont cryptés !\n" 
 "Bonjour, votre ordinateur a été infecté. Tous vos fichiers sont verrouillés, il n'y a aucun moyen de faire quoi que ce soit par vous-même.\n" 
 "\n"
 "Je vous invite à coopérer afin de récupérer vos données. Vous avez 3 heures pour verser 50 XMR à l'adresse suivante : bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh\n" 
 "\n"
 "Attention, arrêter puis redémarrer le PC est inutile. Au bout de ces 3 heures, toutes vos données (mots de passe, adresse carte bleue, fichiers confidentiels\n"
 "\n"
 "ainsi que chacun de vos secrets) seront leakés sur le dark web où des gens se délecteront de vos données. Y compris moi-même.\n",
 font=("Arial", 12),
 fg="white",
 bg="#0f0f0f",
 justify="center"
 )
 desc.pack(pady=20)

 btn = tk.Button(
 root,
 text="Simuler le paiement",
 command=lambda: fake_action(root),
 font=("Arial", 12, "bold"),
 bg="#ff2e2e",
 fg="white",
 padx=20,
 pady=10
 )
 btn.pack(pady=30)

 footer = tk.Label(
 root,
 text="Educational cybersecurity simulation only",
 font=("Arial", 10, "italic"),
 fg="#888888",
 bg="#0f0f0f"
 )
 footer.pack(side="bottom", pady=10)

 root.mainloop()

if __name__ == "__main__":
 create_ui()

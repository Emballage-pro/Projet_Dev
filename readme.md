# IBAN Clipboard Replacer – Security Awareness Project

> ⚠️ **AVERTISSEMENT IMPORTANT / IMPORTANT WARNING** ⚠️  
> Ce projet est fourni **uniquement à des fins éducatives, de recherche en cybersécurité et de sensibilisation**.  
> **Toute utilisation malveillante, frauduleuse ou non autorisée est strictement interdite.**

---

## 📌 Description

Ce projet est une **preuve de concept (PoC)** démontrant comment une application locale peut surveiller le presse‑papiers du système et détecter des chaînes correspondant au format d’un IBAN valide.

Lorsqu’un IBAN est détecté, le programme illustre comment celui‑ci **pourrait théoriquement être remplacé** par une autre valeur dans le presse‑papiers.

L’objectif de ce projet est de :

- Comprendre les **risques liés à la manipulation du presse‑papiers**
- Sensibiliser aux **attaques de type clipboard hijacking**
- Aider les développeurs et chercheurs à **détecter et prévenir ce type de comportement**

---

## 🛡️ Contexte de sécurité

Les attaques basées sur le presse‑papiers existent réellement et sont parfois utilisées par des logiciels malveillants afin de :

- Modifier des adresses de paiement
- Rediriger des transferts financiers
- Abuser de la confiance de l’utilisateur final

👉 **Ce dépôt n’a pas vocation à encourager ces pratiques**, mais à **les exposer** afin de mieux :
- les reconnaître
- les analyser
- les bloquer

---

## ⚖️ Usage autorisé

✅ Autorisé :
- Recherche en cybersécurité
- Analyse de comportements malveillants
- Tests en environnement **isolé** (VM / sandbox)
- Démonstrations pédagogiques
- Apprentissage Python & sécurité offensive/défensive

❌ Strictement interdit :
- Usage en production
- Usage à l’insu d’un utilisateur
- Usage à des fins financières, frauduleuses ou criminelles
- Diffusion ou intégration dans un malware
- Déploiement sur une machine qui ne vous appartient pas

---

## 🚨 Responsabilité légale

L’auteur de ce projet :

- **N’est en aucun cas responsable** de l’utilisation faite du code
- Décline **toute responsabilité** en cas de dommages financiers, matériels ou légaux
- Rappelle que ce type de comportement peut être **illégal dans de nombreux pays**

✅ Vous êtes **seul responsable** :
- de vos tests
- de votre environnement
- du respect des lois locales et internationales

---

## 🧪 Environnement recommandé

- Système isolé (VM, sandbox)
- Machine de test personnelle
- Aucune donnée réelle
- Aucun IBAN réel utilisé

---

## 🔐 Bonnes pratiques de défense (Blue Team)

Ce projet permet également de mettre en évidence plusieurs moyens de protection :

- Vérification manuelle des IBAN avant validation
- Outils de détection de modifications du presse‑papiers
- Restrictions de permissions applicatives
- Antivirus / EDR à jour
- Sensibilisation des utilisateurs finaux

---

## 📚 Disclaimer éthique

> **Ce projet est un outil de compréhension, pas une arme.**

Si vous êtes intéressé par la cybersécurité :
- utilisez vos compétences pour **protéger**
- pas pour **nuire**

---

## 📄 Licence

Ce projet est fourni **sans aucune garantie**.  
L’usage se fait **à vos propres risques**.

---

## ✉️ Contact

Si vous êtes un étudiant, un chercheur ou un professionnel de la sécurité et que vous souhaitez discuter de ce sujet dans un cadre légal et éthique, n’hésitez pas à ouvrir une issue.

---
# parabox_mobile — Interface Mobile Livreur PARABOX

> **Version 2.0** — Odoo 17 Community | Redesign complet UI/UX + nouvelles API

## Vue d'ensemble

Interface web responsive pour les livreurs PARABOX. Fonctionne sur tout smartphone via navigateur Chrome/Safari — aucune app à installer.

Le livreur s'authentifie via son compte Odoo (type Portal), voit ses BL du jour, envoie l'OTP de signature au client, puis valide la livraison.

---

## Fonctionnalités v2

### Page d'accueil livreur (`/parabox/mobile/livreur`)
- **KPI strip** : BL en cours / Livrés aujourd'hui / Signés
- **Liste "En cours"** : BL confirmed + assigned, triés par date prévue
- **Liste "Livrés"** : BL validés aujourd'hui (référence rapide)
- Badge de statut coloré sur chaque BL
- Détection automatique des BL annulés par le magasinier

### Page détail BL (`/parabox/mobile/livreur/bl/<id>`)
- Infos client + adresse de livraison
- Liste des produits : quantité commandée / livrée / lots
- **Alerte orange** si stock pas encore réservé (`state = confirmed`)
- **Bannière rouge** + message clair si BL annulé (`state = cancel`)
- Polling automatique toutes les 15s : détection d'annulation en temps réel
- Bouton "Envoyer OTP" → animation spinner → URL de signature générée
- Bouton "Valider BL" (après signature client)

---

## Routes HTTP

| Méthode | Route | Auth | Type | Description |
|---------|-------|------|------|-------------|
| GET | `/parabox/mobile/livreur` | user | HTML | Accueil — liste des BL |
| GET | `/parabox/mobile/livreur/bl/<id>` | user | HTML | Détail d'un BL |
| POST | `/parabox/mobile/livreur/bl/<id>/send-otp` | user | JSON | Créer + envoyer OTP |
| POST | `/parabox/mobile/livreur/bl/<id>/validate` | user | JSON | Valider le BL |
| POST | `/parabox/mobile/livreur/bl/<id>/status` | user | JSON | État BL (polling) |
| GET | `/parabox/mobile/livreur/api/bls` | user | JSON | API liste des BL |

### Exemple réponse `/status`
```json
{
  "exists": true,
  "state": "done",
  "state_label": "Livré",
  "cancelled": false,
  "done": true
}
```

---

## États des BL

| État Odoo | Affichage mobile | Couleur |
|-----------|-----------------|---------|
| `confirmed` | En attente de stock | Orange |
| `assigned` | Prêt à livrer | Bleu |
| `done` | Livré | Vert |
| `cancel` | Annulé | Rouge |

---

## Installation

```bash
# 1. Prérequis : parabox_logistics_tracking + parabox_sign installés
# 2. Redémarrer Odoo après ajout du module au dossier addons
# 3. Settings > Apps > Update Apps List
# 4. Installer "PARABOX Mobile Livreur"
# 5. Aller dans Settings > Users > Karim Alami → type : Portail
```

---

## Accès démo avec ngrok

```bash
# Sur le PC qui héberge Odoo :
ngrok http 8069

# Copier l'URL HTTPS générée (ex: https://abc123.ngrok.io)
# Odoo : Settings > Technical > System Parameters
# web.base.url = https://abc123.ngrok.io

# Le livreur ouvre sur son téléphone :
https://abc123.ngrok.io/parabox/mobile/livreur
```

> ⚠️ Sans ngrok, utiliser l'IP locale du PC (`192.168.x.x:8069`) — le livreur doit être sur le même réseau WiFi.

---

## Dépendances

```
stock
parabox_sign
parabox_logistics_tracking
```

---

## Variables de configuration

| Clé système | Valeur | Rôle |
|-------------|--------|------|
| `web.base.url` | `http://192.168.x.x:8069` | URL de base pour les liens OTP |

---

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `controllers/mobile_controller.py` | Toutes les routes HTTP + JSON |
| `views/mobile_templates.xml` | Templates QWeb (design CSS variables) |

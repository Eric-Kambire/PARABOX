# 🗂️ CAP2026 — PARABOX — Master Prompt Claude Coworker
## Index de navigation — LIRE EN PREMIER

> Travaille phase par phase. Ne saute JAMAIS une phase.  
> À la fin de chaque phase, génère un README.md dans le dossier de la phase.  
> Ne génère jamais de code Odoo Enterprise. Tout est Community 17.  
> Si tu doutes d'une API Odoo 17 → dis-le explicitement, ne devine pas.

---

## 📁 Structure du dossier projet

```text
/CAP2026_PARABOX/
  00_INDEX.md
  01_PHASE1_CLEANUP.md
  02_PHASE2_CONFIG.md
  03_PHASE3_USERS.md
  04_PHASE4_CUSTOM.md
  05_PHASE5_SIGN.md
  06_PHASE6_DASHBOARD.md
  07_PHASE7_DEMO.md
  08_PHASE8_HTML.md
  09_PHASE9_DOCS.md
  /odoo_modules/
  /data/
  /scripts/
  /demo/
  /docs/
```

---

## ⚙️ Stack technique — NE JAMAIS DÉVIER

```text
Odoo     : 17 Community (JAMAIS Enterprise)
OS       : Windows local
URL      : http://localhost:8069
DB       : parabox_db
Admin    : eric.kambire@centrale-casablanca.ma / parabox_odoo
Accès ext: ngrok + port 8069 ouvert
Python   : 3.10+
Budget   : ZÉRO — tout open source
```

---

## 🔌 Connexion RPC standard (réutiliser partout)

```python
import xmlrpc.client
url = 'http://localhost:8069'
db, user, pwd = 'parabox_db', 'eric.kambire@centrale-casablanca.ma', 'parabox_odoo'
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, pwd, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
```

---

## 🎯 Problème central

PARABOX facture ce qui est **commandé**, pas ce qui est **livré**.  
→ BC ≠ BL → ~3 MDH/an litiges + ~10 MDH encours à risque

**Projet MATCH** : BC → BL (livré réel) → Facture → Signature sécurisée → Zéro litige

---

## 📋 Ordre d'exécution

| # | Fichier | Contenu | Prérequis |
|---|---------|---------|-----------|
| 1 | 01_PHASE1_CLEANUP.md | Nettoyage + données | Aucun |
| 2 | 02_PHASE2_CONFIG.md | Config Odoo | Phase 1 |
| 3 | 03_PHASE3_USERS.md | Utilisateurs | Phase 2 |
| 4 | 04_PHASE4_CUSTOM.md | Modules Python | Phase 3 |
| 5 | 05_PHASE5_SIGN.md | Sign custom | Phase 4 |
| 6 | 06_PHASE6_DASHBOARD.md | Dashboard | Phase 4 |
| 7 | 07_PHASE7_DEMO.md | Script démo | Phases 1-6 |
| 8 | 08_PHASE8_HTML.md | HTML interactif | Phase 7 |
| 9 | 09_PHASE9_DOCS.md | Doc Word 10p | Tout |


***

## 📱 Phase 10 — Interfaces Web Mobile (ajout)

Lire : **10_PHASE10_MOBILE.md**

Ce fichier couvre les 2 interfaces web mobile nécessaires pour la démo terrain :

### Interface 1 — Espace Livreur
```text
URL     : https://[ngrok-url]/parabox/mobile/livreur
Login   : livreur@parabox.ma / Parabox2026!
Rôle    : voir BL du jour, valider livraison, déclencher OTP client
Accès   : téléphone livreur via ngrok (Chrome mobile)
```

### Interface 2 — Signature Client
```text
URL     : https://[ngrok-url]/parabox/sign/<token>
Login   : aucun (lien unique envoyé par email)
Rôle    : entrer OTP, signer avec le doigt, confirmer livraison
Accès   : téléphone client ou téléphone livreur
```

### Principe technique
```text
PC (Odoo 17)
    ↓ ngrok tunnel
https://abc123.ngrok.io
    ↓ Chrome mobile
Interface livreur / Page signature
    ↓ fetch() / RPC Odoo
Même base PostgreSQL, même données
```

### Prérequis
- Phase 5 (parabox_sign) terminée
- ngrok actif avec URL mise à jour dans System Parameters
- SMTP configuré pour envoi OTP

### Checklist rapide
- [ ] /parabox/mobile/livreur accessible sur mobile
- [ ] /parabox/sign/<token> accessible depuis lien email
- [ ] OTP reçu + vérifié + signature BIC fonctionnelle
- [ ] PDF signé généré + email confirmation envoyé
- [ ] QR code démo généré → /demo/qr_livreur.png

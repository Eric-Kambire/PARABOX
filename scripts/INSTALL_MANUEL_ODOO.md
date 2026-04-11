# Installation manuelle des modules PARABOX dans Odoo

## Si le script .bat ne fonctionne pas — méthode interface web

### Étape 1 — Copie des modules

Copie les 8 dossiers du dossier `odoo_modules/` vers ton dossier `custom_addons` d'Odoo :

```
odoo_modules/parabox_credit_control     → C:\odoo17\custom_addons\parabox_credit_control
odoo_modules/parabox_logistics_tracking → C:\odoo17\custom_addons\parabox_logistics_tracking
odoo_modules/parabox_litige             → C:\odoo17\custom_addons\parabox_litige
odoo_modules/parabox_encaissement       → C:\odoo17\custom_addons\parabox_encaissement
odoo_modules/parabox_product_alias      → C:\odoo17\custom_addons\parabox_product_alias
odoo_modules/parabox_sign               → C:\odoo17\custom_addons\parabox_sign
odoo_modules/parabox_dashboard          → C:\odoo17\custom_addons\parabox_dashboard
odoo_modules/parabox_mobile             → C:\odoo17\custom_addons\parabox_mobile
```

### Étape 2 — Vérifier odoo.conf

Le fichier `odoo.conf` doit contenir le chemin custom_addons :

```ini
addons_path = C:\odoo17\odoo\addons,C:\odoo17\custom_addons
```

### Étape 3 — Installer reportlab

Ouvre un terminal Windows (cmd) et tape :

```cmd
C:\odoo17\python\python.exe -m pip install reportlab
```

### Étape 4 — Activer Mode Développeur dans Odoo

1. Ouvre http://localhost:8069
2. Connecte-toi en admin
3. Paramètres → onglet "Technique" → Activer le mode développeur
   (ou ajoute `?debug=1` dans l'URL)

### Étape 5 — Mettre à jour la liste des apps

Applications → clic sur "Mettre à jour la liste des applications"

### Étape 6 — Installer dans cet ordre EXACT

⚠️ L'ordre est important à cause des dépendances entre modules.

| Ordre | Module | Description |
|-------|--------|-------------|
| 1 | `parabox_credit_control` | Contrôle crédit + dérogations |
| 2 | `parabox_logistics_tracking` | Traçabilité 4 états picking |
| 3 | `parabox_litige` | Kanban SLA litiges |
| 4 | `parabox_encaissement` | Plan paiement multi-modes |
| 5 | `parabox_product_alias` | Alias produits |
| 6 | `parabox_sign` | OTP + signature + SHA-256 |
| 7 | `parabox_dashboard` | Dashboard Direction 10 KPIs |
| 8 | `parabox_mobile` | Interface mobile livreur |

Pour chaque module : Recherche → "parabox_..." → Installer

### Étape 7 — Vérification post-installation

Après installation de tous les modules, vérifie :

- ✅ Menu "PARABOX" visible dans le menu principal
- ✅ Paramètres → Politique de facturation = "Quantités livrées" sur les produits
- ✅ http://localhost:8069/odoo/parabox-dashboard accessible avec direction@parabox.ma
- ✅ http://localhost:8069/parabox/mobile/livreur accessible avec livreur@parabox.ma

### En cas d'erreur d'installation

1. Ouvre le log Odoo (terminal où tourne le serveur)
2. Cherche `ERROR` ou `Traceback`
3. Messages d'erreur courants :

**"Field 'encaissement_count' does not exist"**
→ Reinstalle parabox_encaissement en premier

**"Sequence 'parabox.sign.request' not found"**
→ Reinstalle parabox_sign (la séquence XML est maintenant présente)

**"reportlab not found"**
→ Lance : `pip install reportlab` dans le terminal Python d'Odoo

**"parabox_litige not installed"** (erreur lors de parabox_dashboard)
→ Installe parabox_litige avant parabox_dashboard

### Configuration post-installation

**Politique de facturation (CRITIQUE pour le Projet MATCH) :**
Ventes → Configuration → Paramètres → Facturation → Politique de facturation → **Quantités livrées**

**Entrepôt 2 étapes :**
Inventaire → Configuration → Entrepôts → PARABOX WH → Livraisons : **Envoyer les marchandises en 2 étapes**

**URL de base pour ngrok :**
Paramètres → Technique → Paramètres système → `web.base.url` → coller l'URL ngrok HTTPS

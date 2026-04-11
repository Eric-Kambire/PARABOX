# CAP2026 PARABOX — Dossier projet
## ➡️ Lire 00_INDEX.md en premier

***

## Structure

```text
/CAP2026_PARABOX/
  README.md              ← CE FICHIER
  00_INDEX.md            ← Navigation + stack + RPC (LIRE EN PREMIER)
  01_PHASE1_CLEANUP.md   ← Nettoyage + Master Data
  02_PHASE2_CONFIG.md    ← Configuration Odoo standard
  03_PHASE3_USERS.md     ← Utilisateurs + Droits
  04_PHASE4_CUSTOM.md    ← Modules Python custom (5 modules)
  05_PHASE5_SIGN.md      ← Odoo Sign sécurisé (OTP + BIC + hash)
  06_PHASE6_DASHBOARD.md ← Dashboard Direction (Chart.js)
  07_PHASE7_DEMO.md      ← Script démo 6 scénarios
  08_PHASE8_HTML.md      ← Refonte HTML interactif
  09_PHASE9_DOCS.md      ← Document explicatif 10 pages
  10_PHASE10_MOBILE.md   ← Interfaces web mobile livreur + signature
  /odoo_modules/         ← Code Python modules custom
  /data/                 ← CSV master data
  /scripts/              ← Scripts RPC Python
  /demo/                 ← Données et script démo
  /docs/                 ← Document explicatif final
```

***

## Stack technique

```text
Odoo     : 17 Community (JAMAIS Enterprise)
OS       : Windows local
URL      : http://localhost:8069
Accès ext: ngrok + port 8069 ouvert
Python   : 3.10+
Budget   : ZÉRO — tout open source
```

***

## Ordre d'exécution

| # | Phase | Fichier |
|---|-------|---------|
| 1 | Nettoyage + données | 01_PHASE1_CLEANUP.md |
| 2 | Config Odoo | 02_PHASE2_CONFIG.md |
| 3 | Utilisateurs | 03_PHASE3_USERS.md |
| 4 | Modules custom | 04_PHASE4_CUSTOM.md |
| 5 | Sign sécurisé | 05_PHASE5_SIGN.md |
| 6 | Dashboard | 06_PHASE6_DASHBOARD.md |
| 7 | Script démo | 07_PHASE7_DEMO.md |
| 8 | HTML support | 08_PHASE8_HTML.md |
| 9 | Document Word | 09_PHASE9_DOCS.md |
| 10 | Mobile web | 10_PHASE10_MOBILE.md |

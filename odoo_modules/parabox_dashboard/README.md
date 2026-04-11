# parabox_dashboard — Dashboard Direction PARABOX

> **Version 2.0** — Odoo 17 Community | OWL + Chart.js | Accès Direction uniquement

## Vue d'ensemble

Dashboard de pilotage temps réel pour la Direction PARABOX. Affiche 10 KPIs (5 Finance + 5 Logistique), 4 graphiques, et un bandeau d'alertes actives. Auto-refresh toutes les 60 secondes.

**Accès restreint** : seuls les membres du groupe `Direction` voient ce menu.

---

## Indicateurs Finance

| KPI | Calcul | Seuil d'alerte |
|-----|--------|----------------|
| CA Mois en cours | Factures HT postées depuis le 1er du mois | Évolution vs M-1 |
| Encours clients | Somme `amount_residual` factures non payées | > 500 000 DH |
| DSO | (Encours / CA 90j) × 90 | > 45 jours |
| Litiges ouverts | Montant total litiges ouverts (parabox_litige) | > 50 000 DH |
| Factures en retard | Factures postées + non payées + date due dépassée | > 5 factures |

## Indicateurs Logistique

| KPI | Calcul | Seuil d'alerte | Cible |
|-----|--------|----------------|-------|
| OTIF | BL livrés à temps / total BL (30j) | < 90% | 95% |
| Fill Rate | Lignes livrées complètes / lignes totales (30j) | < 85% | 95% |
| Ruptures stock | Produits avec `qty_available <= 0` | > 0 | 0 |
| BL en cours | BL confirmed + assigned + waiting | — | — |
| Reliquats ouverts | BL en cours avec backorder_id | > 3 | 0 |

---

## Graphiques (Chart.js 4.4.1)

1. **CA mensuel** — 6 derniers mois (barres), dernier mois mis en évidence
2. **Litiges par type** — Donut (parabox.litige)
3. **Top 5 encours clients** — Barres horizontales
4. **Statuts BL 30 jours** — Donut (Livré/Attente/Prêt/Annulé)

---

## Architecture technique

```
OWL Component (Odoo 17)
├── setup() — useService('rpc'), useService('action'), useRef(4 canvas)
├── onWillStart — _loadData() (RPC)
├── onMounted — _startClock(), _startRefresh()
├── onWillUnmount — clearInterval × 2, Chart.destroy × 4
├── _loadData() — RPC → parabox.dashboard.data.get_kpis()
├── _drawAllCharts() — Chart.js (chargé CDN une seule fois)
└── openBLsEnCours() / openFacturesRetard() — navigation Odoo
```

**Modèle Python** : `parabox.dashboard.data` (TransientModel)
- `get_kpis()` — calcule tout, retourne dict JSON
- `_get_finance_kpis()` — 5 KPIs finance
- `_get_logistique_kpis()` — 5 KPIs logistique (compatible Odoo 17 : `move.quantity`)
- `_get_chart_data()` — données 4 graphiques
- `_build_alertes()` — liste des alertes actives

---

## Alertes intelligentes

Le bandeau sous le header affiche les alertes actives en rouge/orange. Si aucune alerte : "Tous les indicateurs sont dans les normes ✅".

Alertes générées automatiquement pour : retards, DSO, litiges, OTIF critique, ruptures, reliquats.

---

## Installation

```bash
# Dépendances obligatoires :
# sale_management, stock, account, parabox_litige

# Settings > Apps > Update Apps List
# Installer "PARABOX Dashboard Direction"
# Assigner le groupe Direction à l'utilisateur concerné
```

---

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `models/dashboard_data.py` | Calcul des KPIs côté serveur |
| `static/src/js/dashboard.js` | Composant OWL + Chart.js + horloge |
| `static/src/xml/dashboard.xml` | Template QWeb/OWL |
| `static/src/css/dashboard.css` | Design (CSS variables, gradient, progress bars) |
| `views/dashboard_views.xml` | Action client + menu (groupe Direction) |

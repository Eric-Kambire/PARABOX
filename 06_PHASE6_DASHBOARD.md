# Phase 6 — Dashboard Direction
## Dossier output : /odoo_modules/parabox_dashboard/

---

## Objectif
Dashboard mixte **Finance + Logistique** pour `direction@parabox.ma`.  
Design soigné, minimaliste, orienté prise de décision rapide.  
Compatible **Odoo Community 17**.

---

## Fichiers à générer

```text
/odoo_modules/parabox_dashboard/
  __manifest__.py
  __init__.py
  models/dashboard_data.py
  views/dashboard_views.xml
  static/
    src/js/dashboard.js
    src/css/dashboard.css
  README.md
```

---

## KPIs Finance

1. CA du mois en cours  
2. Encours clients total  
3. DSO  
4. Montant litiges ouverts  
5. Factures en retard  

---

## KPIs Logistique

6. OTIF  
7. Fill Rate  
8. Produits en rupture  
9. BL en cours  
10. Reliquats ouverts  

---

## Design

```text
Layout : 2 colonnes
Header : logo PARABOX + date/heure + utilisateur
Couleurs :
  Vert   #2ECC71
  Orange #F39C12
  Rouge  #E74C3C
  Bleu   #3498DB
  Fond   #F8F9FA
Graphiques :
  - Barres : CA mensuel
  - Jauge : OTIF
  - Courbe : encours
  - Donut : litiges par type
Refresh : 60 secondes
```

---

## Accès

- `direction@parabox.ma`
- `admin@parabox.ma`

---

## ✅ Checklist Phase 6

- [ ] Module installé
- [ ] 10 KPIs affichés
- [ ] Graphiques fonctionnels
- [ ] Alertes couleur actives
- [ ] Refresh auto
- [ ] Test avec direction
- [ ] README généré

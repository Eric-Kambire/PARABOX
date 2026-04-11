# Phase 2 — Configuration Odoo Standard
## Dossier output : /phase2_configuration/

---

## Tâche 2.1 — Modules à installer (dans cet ordre)

```text
sale_management  → Sales
stock            → Inventory
purchase         → Purchase
account          → Invoicing
crm              → CRM
contacts         → Contacts
point_of_sale    → POS (PARASHOP B2C)
```

> Vérifier si `approvals` est disponible en Community v17 avant d'installer.

---

## Tâche 2.2 — Paramètres critiques

### Sales > Settings
```text
Invoicing Policy     = Invoice what is delivered
Lock Confirmed Sales = ON
Customer Warnings    = ON
Customer Addresses   = ON
```

### Inventory > Settings
```text
Lots & Serial Numbers = ON
Expiration Dates      = ON
Storage Locations     = ON
Multi-Step Routes     = 2 étapes (Pick + Ship)
Backorders            = Ask
Negative Stock        = OFF
```

### Accounting > Settings
```text
Currency = MAD
Fiscal positions = Maroc
```

---

## Tâche 2.3 — Entrepôts & Emplacements

### Entrepôt principal PARABOX
```text
Nom  : PARABOX WH | Code : WH
WH/Stock
WH/Picking
WH/Output
WH/Quality
```

### Entrepôt secondaire PARASHOP
```text
Nom  : PARASHOP | Code : PS
PS/Stock
```

---

## Tâche 2.4 — Catégories produits

```text
Parapharmacie/
  Soins Visage
  Soins Corps
  Cheveux
  Bébé & Maman
  Bucco-dentaire
  Compléments alimentaires
  Bien-être
```

---

## Tâche 2.5 — Listes de prix

```text
1. Tarif Standard MAD
2. Tarif Pharmacie VIP
3. Tarif PARASHOP
```

---

## Tâche 2.6 — Règles réapprovisionnement automatiques

```text
P001 Crème Hydratante  Min:20  Max:100  Déclencheur:Auto
P002 Fluide SPF 50     Min:15  Max:80   Déclencheur:Auto
P009 Sérum Anti-âge    Min:10  Max:60   Déclencheur:Auto
P004 Lotion Hydratante Min:10  Max:75   Déclencheur:Auto
```

---

## Tâche 2.7 — Séquences documents

```text
Commandes clients  : S-PARA-%(year)s-%(seq)05d
Bons de livraison  : BL-PARA-%(year)s-%(seq)05d
Factures clients   : FAC-PARA-%(year)s-%(seq)05d
PO fournisseurs    : PO-PARA-%(year)s-%(seq)05d
Réceptions         : REC-PARA-%(year)s-%(seq)05d
```

---

## ✅ Checklist Phase 2

- [ ] Modules installés
- [ ] Invoicing Policy = Invoice what is delivered
- [ ] Negative Stock = OFF
- [ ] Entrepôts créés
- [ ] Catégories créées
- [ ] Pricelists créées
- [ ] Réappro auto configuré
- [ ] Séquences personnalisées

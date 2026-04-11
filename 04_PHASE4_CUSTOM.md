# Phase 4 — Modules Python Custom
## Dossier output : /odoo_modules/

> Chaque module = 1 dossier dans /odoo_modules/  
> Chaque module a : `__manifest__.py`, `__init__.py`, `models/`, `views/`, `security/`, `data/`  
> Chaque module a son propre `README.md`

---

## Module 1 — parabox_credit_control

### Objectif
Bloquer une commande si le client dépasse sa limite de crédit.
Envoyer une notification à l'ADV pour dérogation.

### Logique métier
```python
# Dans sale.order, surcharger action_confirm()
# 1. Calculer encours actuel du client
# 2. Comparer avec res.partner.credit_limit
# 3. Si dépassement :
#    → state = 'credit_hold'
#    → créer une activité ADV
#    → envoyer email notification
#    → NE PAS confirmer
# 4. L'ADV peut approuver
# 5. Logger la dérogation
```

### Champs à ajouter
```python
# res.partner
credit_limit = fields.Float('Limite crédit (DH)', default=10000)
credit_hold  = fields.Boolean('Compte bloqué', default=False)

# sale.order
credit_derogation = fields.Boolean('Dérogation accordée')
credit_derogation_by = fields.Many2one('res.users', 'Approuvé par')
credit_derogation_dt = fields.Datetime('Date dérogation')
credit_derogation_note = fields.Text('Raison dérogation')
```

---

## Module 2 — parabox_logistics_tracking

### Objectif
Tracer les 4 états logistiques :
**Commandé → Préparé → Chargé → Livré**

### Modèle type
```python
picking_id     = Many2one('stock.picking')
product_id     = Many2one('product.product')
qty_ordered    = Float('Commandé')
qty_prepared   = Float('Préparé')
qty_loaded     = Float('Chargé')
qty_delivered  = Float('Livré réel')
ecart          = Float('Écart', compute=...)
substitution   = Boolean('Substitution')
product_sub_id = Many2one('product.product', 'Produit substitué')
note_ecart     = Text('Raison écart')
```

---

## Module 3 — parabox_litige

### Objectif
Gérer les litiges reliés aux documents :
commande / BL / facture / avoir.

### Étapes kanban
```text
Ouvert → En cours d'analyse → En attente client → Résolu → Clos
```

### SLA
```text
Ouvert > 3 jours → alerte rouge
Ouvert > 7 jours → escalade direction
```

---

## Module 4 — parabox_encaissement

### Objectif
Gérer les paiements multiples sur une facture
(cash + chèque + traite + virement).

### Modèles
```python
# plan
invoice_id     = Many2one('account.move')
client_id      = Many2one('res.partner')
montant_total  = Float(related='invoice_id.amount_total')
montant_recu   = Float(compute=...)
solde_restant  = Float(compute=...)
statut         = Selection([('attente','En attente'),('partiel','Partiel'),('solde','Soldé')])

# lignes
date           = Date
montant        = Float
mode_paiement  = Selection([('cash','Cash'),('cheque','Chèque'),('traite','Traite'),('virement','Virement')])
reference      = Char('N° chèque / référence')
statut         = Selection([('recu','Reçu'),('encaisse','Encaissé'),('rejete','Rejeté')])
```

---

## Module 5 — parabox_product_alias

### Objectif
Table de correspondance entre :
- code PARABOX
- code fournisseur
- code revendeur
- EAN

### Modèle
```python
product_id       = Many2one('product.template')
code_parabox     = Char('Code PARABOX')
code_fournisseur = Char('Code fournisseur')
code_revendeur   = Char('Code revendeur')
ean              = Char('Code-barres EAN')
fournisseur_id   = Many2one('res.partner')
actif            = Boolean(default=True)
note             = Text
```

---

## ✅ Checklist Phase 4

- [ ] parabox_credit_control installé et testé
- [ ] parabox_logistics_tracking installé et testé
- [ ] parabox_litige installé et testé
- [ ] parabox_encaissement installé et testé
- [ ] parabox_product_alias installé et testé
- [ ] README de chaque module
- [ ] README global généré

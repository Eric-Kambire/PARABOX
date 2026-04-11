# parabox_credit_control

## Objectif
Bloquer automatiquement une commande client si le client dépasse sa limite de crédit autorisée.

## Fonctionnalités
- Champ `credit_limit` sur `res.partner` (défaut : 10 000 DH)
- Champ `credit_hold` pour bloquer manuellement un compte
- Calcul de l'encours actuel (factures ouvertes)
- Blocage de `action_confirm()` si `encours + montant_commande > credit_limit`
- Workflow de dérogation : l'ADV peut accorder ou refuser
- Log des dérogations (qui, quand, pourquoi)
- Activité assignée à l'ADV automatiquement en cas de blocage
- Template email notification dérogation

## Installation
```bash
# Copier dans le dossier addons Odoo
cp -r parabox_credit_control /path/to/odoo/addons/
# Mettre à jour la liste des modules
# Installer depuis Paramètres > Modules > parabox_credit_control
```

## Dépendances
- `sale_management`
- `account`
- `mail`

## Champs ajoutés

### res.partner
| Champ | Type | Description |
|-------|------|-------------|
| credit_limit | Float | Limite crédit en DH |
| credit_hold | Boolean | Compte bloqué manuellement |
| encours_actuel | Float (computed) | Factures ouvertes |
| taux_utilisation_credit | Float (computed) | % utilisation |

### sale.order
| Champ | Type | Description |
|-------|------|-------------|
| credit_hold_blocked | Boolean | Commande bloquée |
| credit_derogation | Boolean | Dérogation accordée |
| credit_derogation_by | Many2one(res.users) | Approuvé par |
| credit_derogation_dt | Datetime | Date dérogation |
| credit_derogation_note | Text | Raison |

# parabox_logistics_tracking — Traçabilité + Notifications PARABOX

> **Version 2.0** — Odoo 17 Community | Groupes de sécurité + Notifications IN-APP

## Vue d'ensemble

Module central de la suite PARABOX. Fournit :
1. **Groupes de sécurité** — 5 rôles (Direction, Commercial, Magasinier, Livreur, Comptable)
2. **Modèle de traçabilité** — `parabox.logistics.line` : historique des événements BL
3. **Notifications IN-APP automatiques** — Inbox Odoo (cloche), pas d'email

---

## Groupes de sécurité

Définis dans `security/groups.xml` :

| Groupe | XML ID | Description |
|--------|--------|-------------|
| Direction | `group_parabox_direction` | Accès total : dashboard, tous modules, rapports |
| Commercial | `group_parabox_commercial` | Ventes, litiges, traçabilité |
| Magasinier | `group_parabox_magasinier` | Stock, BL, signatures, alias produits |
| Livreur | `group_parabox_livreur` | Interface mobile uniquement (type Portal) |
| Comptable | `group_parabox_comptable` | Facturation, encaissements, litiges |

### Matrice d'accès aux menus PARABOX

| Menu | Direction | Commercial | Magasinier | Comptable | Livreur |
|------|:---------:|:----------:|:----------:|:---------:|:-------:|
| Dashboard | ✅ | — | — | — | — |
| Traçabilité | ✅ | ✅ | ✅ | — | — |
| Signatures BL | ✅ | — | ✅ | — | — |
| Litiges | ✅ | ✅ | — | ✅ | — |
| Encaissements | ✅ | — | — | ✅ | — |
| Alias Produits | ✅ | — | ✅ | — | — |

---

## Notifications IN-APP (Odoo Inbox)

Les 3 actions automatiques dans `data/automated_actions.xml` envoient des notifications dans la **cloche Odoo** (Inbox), pas d'email :

### 1. Commande confirmée → Magasinier
- **Déclencheur** : `sale.order` passe à `state = sale`
- **Destinataires** : groupe `stock.group_stock_manager` + `group_parabox_magasinier`
- **Message** : "📦 Nouvelle commande à préparer" + détails commande

### 2. BL validé → Commercial + Direction
- **Déclencheur** : `stock.picking` outgoing passe à `state = done`
- **Destinataires** : groupe `group_parabox_commercial` + `group_parabox_direction`
- **Message** : "✅ Bon de livraison validé" + nom BL + client

### 3. BL annulé → Commercial + Livreur
- **Déclencheur** : `stock.picking` outgoing passe à `state = cancel`
- **Destinataires** : groupe `group_parabox_commercial` + `group_parabox_livreur`
- **Message** : "❌ Bon de livraison annulé" + nom BL + client

### Mécanisme technique (Odoo 17)
```python
env['mail.message'].create({
    'message_type': 'notification',
    'body': notif_body,
    'res_id': record.id,
    'model': 'stock.picking',
    'subtype_id': env.ref('mail.mt_comment').id,
    'notification_ids': [(0, 0, {
        'notification_type': 'inbox',
        'res_partner_id': pid,
        'notification_status': 'ready',
    }) for pid in partner_ids],
})
```

---

## Workflow magasinier — 2 étapes expliquées

Le magasinier voit les BL en état `confirmed` ou `assigned`.

**Étape 1 — "Vérifier disponibilité"** : Odoo réserve le stock pour ce BL (`state → assigned`). Le BL passe en "Prêt à livrer". La réservation peut être annulée sans impact sur le BL.

**Étape 2 — "Valider"** : Confirme l'expédition physique (`state → done`). Le stock est consommé définitivement. Déclenche la notification Commercial + Direction.

> 💡 **Pourquoi 2 étapes ?** Séparer la réservation logistique de la validation physique permet de gérer les aléas (le livreur n'est pas encore parti, stock à recompter) sans corrompre les données.

---

## Installation

```bash
# Settings > Apps > Update Apps List
# Installer "PARABOX Logistics Tracking"
# Ce module est un prérequis de tous les autres modules PARABOX
# Après installation : assigner les groupes aux utilisateurs
#   Settings > Users > [user] > onglet Accès > PARABOX : [groupe]
```

---

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `security/groups.xml` | Définition des 5 groupes PARABOX |
| `security/ir.model.access.csv` | Droits CRUD sur parabox.logistics.line |
| `data/automated_actions.xml` | 3 notifications IN-APP Odoo Inbox |
| `models/logistics_tracking.py` | Modèle parabox.logistics.line |
| `views/parabox_logistics_line_views.xml` | Vues + menus (restrictions groupes) |

# Phase 3 — Utilisateurs & Droits
## Dossier output : /phase3_users/ et /scripts/create_users.py

---

## Tâche 3.1 — Utilisateurs à créer

| Login | Rôle | Nom | Mot de passe |
|-------|------|-----|-------------|
| admin@parabox.ma | Administrateur | Eric Kambiré | Parabox2026! |
| commercial@parabox.ma | Commercial | Yassine El Idrissi | Parabox2026! |
| adv@parabox.ma | ADV | Fatima Benali | Parabox2026! |
| magasinier@parabox.ma | Magasinier | Omar Tazi | Parabox2026! |
| livreur@parabox.ma | Livreur | Karim Alami | Parabox2026! |
| comptable@parabox.ma | Comptable | Amina Chraibi | Parabox2026! |
| direction@parabox.ma | DAF/Direction | Karim Haddad | Parabox2026! |

---

## Tâche 3.2 — Matrice des droits

| Module | Admin | Commercial | ADV | Magasinier | Livreur | Comptable | Direction |
|--------|-------|-----------|-----|-----------|---------|-----------|-----------|
| CRM | Full | Full | Read | ✗ | ✗ | Read | Read |
| Sales | Full | Create/Edit | Validate | ✗ | ✗ | Read | Read |
| Inventory | Full | Read | Read | Full | Picking only | Read | Read |
| Purchase | Full | ✗ | Read | Receive | ✗ | Validate | Read |
| Invoicing | Full | Read | Read | ✗ | ✗ | Full | Read |
| Accounting | Full | ✗ | ✗ | ✗ | ✗ | Full | Reports |
| Dashboard | Full | Own KPIs | Ops KPIs | Stock KPIs | ✗ | Finance KPIs | Full |

---

## Tâche 3.3 — Description de chaque rôle

### 🔑 Admin
- Voit et fait tout
- Configure Odoo, installe modules, gère utilisateurs

### 👨‍💼 Commercial
- Crée devis et commandes clients
- Voit son pipeline CRM
- Ne valide pas le crédit final

### 📋 ADV
- Valide les commandes
- Gère dérogations crédit
- Suit les litiges

### 📦 Magasinier
- Prépare les picking
- Réceptionne les fournisseurs
- Assigne lots et DLC

### 🚚 Livreur
- Valide le BL terrain
- Déclenche la signature client

### 💰 Comptable
- Génère les factures
- Enregistre les paiements
- Fait le lettrage

### 📊 Direction
- Voit le dashboard complet
- Approuve les dérogations importantes

---

## Tâche 3.4 — Générer /scripts/create_users.py

Le script doit :
1. créer les 7 utilisateurs,
2. assigner les groupes Odoo corrects,
3. tester la connexion,
4. générer `users_created.txt`.

Groupes à utiliser :
```python
groupes = {
    'admin': ['base.group_system'],
    'commercial': ['sales_team.group_sale_salesman'],
    'adv': ['sales_team.group_sale_manager'],
    'magasinier': ['stock.group_stock_user'],
    'livreur': ['stock.group_stock_user'],
    'comptable': ['account.group_account_user'],
    'direction': ['account.group_account_manager', 'sales_team.group_sale_manager'],
}
```

---

## ✅ Checklist Phase 3

- [ ] 7 utilisateurs créés
- [ ] Connexions testées
- [ ] Matrice droits vérifiée
- [ ] README.md généré

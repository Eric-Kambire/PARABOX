# Phase 1 — Nettoyage & Master Data
## Dossier output : /scripts/ et /data/

---

## ⚠️ AVANT TOUT — Backup PostgreSQL

```bash
pg_dump -U odoo parabox_db > backup_avant_cleanup.sql
```

---

## Tâche 1.1 — Générer /scripts/cleanup.py

Script RPC qui supprime dans cet ordre :
1. `account.move` — toutes factures/avoirs non PARABOX
2. `stock.picking` — tous BL et réceptions
3. `sale.order` — toutes commandes clients
4. `purchase.order` — tous PO fournisseurs
5. `stock.lot` — tous les lots existants
6. `stock.quant` — remettre à 0 via adjust
7. `res.partner` — supprimer contacts NON PARABOX (garder 21 clients)
8. `product.template` — supprimer produits NON PARABOX (garder 20)

Le script doit :
- Logger chaque suppression dans `cleanup_log.txt`
- Afficher : `Supprimé X / Gardé Y` pour chaque modèle
- Ne JAMAIS supprimer les utilisateurs ni la société

---

## Tâche 1.2 — Générer /data/clients.csv

21 clients depuis `0_Portefeuille_Clients.xlsx`.

Colonnes :
`name,street,city,zone,commercial,type_client,credit_limit,email,phone,pricelist`

Limites de crédit démo :
```text
PARASHOP             → 50000 DH
PARFUMERIE ATLAS     → 15000 DH
PARAPHARMACIE GUÉLIZ → 8000 DH
PARA TALBORJT        → 3000 DH
Tous les autres      → 10000 DH
```

---

## Tâche 1.3 — Générer /data/produits.csv

20 produits depuis `3_Catalogue.xlsx`.

Colonnes :
`ref,barcode,name,categorie,marque,prix_ht,fournisseur,uom,tracking,dlc`

Règle tracking :
- Cosmétiques + compléments → `by_lot`
- Autres → `none`

---

## Tâche 1.4 — Générer /data/fournisseurs.csv

```csv
name,email,phone,city,produits
Inty Distribution,inty@demo.ma,0522000001,Casablanca,P007/P020
Paranova Maroc,paranova@demo.ma,0522000002,Casablanca,P006
HeyPara,heypara@demo.ma,0522000003,Casablanca,P005/P017
Pharma Plus Maroc,pharmaplus@demo.ma,0522000004,Rabat,P008
BeautyDist,beautydist@demo.ma,0522000005,Casablanca,P003/P010
CosmétiPro,cosmetipro@demo.ma,0522000006,Casablanca,P001/P022
DermaLab Maroc,dermalab@demo.ma,0522000007,Casablanca,P002/P009
```

---

## Tâche 1.5 — Générer /data/lots_dlc.csv

Format :
`lot_name,product_ref,qty,location,expiration_date`

- Minimum 3 lots par produit tracé
- Format lot : `LOT-[REF]-2026-[NNN]`
- DLC : entre 2026-12-01 et 2028-06-01

---

## Tâche 1.6 — Générer /scripts/import_data.py

Fonctions attendues :
- `import_clients()`
- `import_produits()`
- `import_fournisseurs()`
- `import_lots()`
- `main()`

---

## ✅ Checklist Phase 1

- [ ] Backup DB créé
- [ ] cleanup.py exécuté
- [ ] 21 clients importés
- [ ] 20 produits importés
- [ ] 7 fournisseurs créés
- [ ] Lots créés
- [ ] Stocks = 0 partout
- [ ] README.md généré

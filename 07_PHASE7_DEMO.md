# Phase 7 — Script de Démo Complet
## Dossier output : /demo/

---

## Prérequis avant démo

- [ ] Phases 1 à 6 terminées
- [ ] Odoo accessible via ngrok
- [ ] Données démo chargées
- [ ] 7 comptes utilisateurs testés
- [ ] SMTP configuré

---

## Scénario 1 — Commande normale B2B (8 min)

```text
Acteur     : commercial@parabox.ma
Client     : PARFUMERIE ATLAS
Produits   : P001 x10 + P009 x5
Objectif   : flux standard sans friction

Étapes :
1. Créer opportunité
2. Convertir en devis
3. Confirmer commande
4. Préparer picking
5. Envoyer OTP
6. Signature client
7. BL validé
8. Facture auto sur livré réel
9. Paiement enregistré
10. Dashboard mis à jour
```

---

## Scénario 2 — Livraison partielle + Backorder (5 min)

```text
Client   : PARASHOP
Produit  : P002 x20
Stock    : 12 seulement
Objectif : montrer facture sur livré réel

Étapes :
1. Créer BC pour 20
2. Préparer 12
3. Valider backorder
4. Facturer 12, pas 20
```

---

## Scénario 3 — Blocage crédit + Dérogation (4 min)

```text
Client    : PARA TALBORJT
Limite    : 3000 DH
Encours   : 2800 DH
Commande  : +725 DH
Objectif  : montrer contrôle crédit automatique
```

---

## Scénario 4 — Réapprovisionnement automatique (3 min)

```text
Produit    : P001
Objectif   : montrer déclenchement auto PO
Étapes :
1. Dashboard montre rupture
2. Inventory > Replenishment
3. PO auto généré
4. Réception + lots + DLC
5. Stock redevient vert
```

---

## Scénario 5 — Litige + Résolution (3 min)

```text
Client     : PARAPHARMACIE GUÉLIZ
Objectif   : traçabilité BC → BL → Facture → Litige → Avoir
```

---

## Scénario 6 — Paiement multi-instruments (2 min)

```text
Facture : 4 800 DH
Paiement :
- Cash   2 000
- Chèque 1 800
- Traite 1 000
Objectif : montrer plan d'encaissement
```

---

## Ordre recommandé

```text
Intro → S1 → S3 → S2 → S4 → S5 → S6 → Dashboard → Conclusion
Total ~31 minutes
```

---

## Données à préparer

Créer `/demo/donnees_demo.json` avec :
- stock initial,
- encours clients,
- lots actifs.

---

## ✅ Checklist Phase 7

- [ ] 6 scénarios testés
- [ ] Données démo chargées
- [ ] URL ngrok testée sur mobile
- [ ] OTP fonctionnel
- [ ] Dashboard à jour
- [ ] Ordre de présentation validé
- [ ] README généré

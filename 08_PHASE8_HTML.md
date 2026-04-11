# Phase 8 — Refonte HTML Interactif
## Dossier output : /docs/CAP2026_Support_Visuel.html

---

## Objectif
Transformer le HTML existant en support de présentation :
- crédible,
- rigoureux,
- défendable,
- standalone,
- sans dépendance internet.

---

## Nouveaux onglets à ajouter

```text
1. Vue Globale
2. Chaîne B2B
3. Approvisionnement
4. B2C PARASHOP
5. ⚠️ Zones Grises & Gaps
6. 🛠 Travail à Réaliser
7. 📄 Documents Pivots
8. 👁 Ce qui reste humain
9. 📊 Pilotage & KPI
10. 🧾 Preuves & Auditabilité
```

---

## Blocs AS-IS / Odoo standard / MVP

```html
<div class="gap-box">
  <div class="gap-row asis"><strong>🔴 AS-IS :</strong> ...</div>
  <div class="gap-row standard"><strong>⚙️ Odoo standard :</strong> ...</div>
  <div class="gap-row mvp"><strong>🧩 MVP PARABOX :</strong> ...</div>
</div>
```

CSS :
```css
.gap-box { border-radius:8px; overflow:hidden; margin:12px 0; }
.gap-row { padding:8px 14px; font-size:0.88rem; line-height:1.5; }
.asis     { background:#fde8e8; border-left:4px solid #e74c3c; }
.standard { background:#e8f4fd; border-left:4px solid #3498db; }
.mvp      { background:#f0e8fd; border-left:4px solid #8e44ad; }
```

---

## Badges "Niveau de réalité"

```html
<span class="badge-reality badge-asis">AS-IS majoritaire</span>
<span class="badge-reality badge-partial">Partiellement configuré</span>
<span class="badge-reality badge-target">Cible future</span>
<span class="badge-reality badge-dev">Nécessite développement MVP</span>
```

---

## Onglet “⚠️ Zones Grises & Gaps”

### Carte 1 — Commande informelle
- AS-IS : WhatsApp / téléphone → ressaisie ADV
- Odoo : devis structuré
- MVP : capture rapide commande récurrente

### Carte 2 — Boîte noire logistique
- AS-IS : commandé ≠ préparé ≠ chargé ≠ livré
- Odoo : picking / delivery
- MVP : suivi 4 états + écarts + substitutions

### Carte 3 — BL / Preuve de livraison
- AS-IS : BL papier signé
- Odoo : bon de livraison
- MVP : signature OTP + BIC + hash PDF

### Carte 4 — Paiements multiples
- AS-IS : lettrage manuel Excel
- Odoo : paiement simple
- MVP : plan d'encaissement multi-instruments

### Carte 5 — Double étiquetage produit
- AS-IS : plusieurs codes pour un même produit
- Odoo : article + lot
- MVP : alias produit / code fournisseur / EAN

---

## Onglet “📊 Pilotage & KPI”

| KPI | Définition | Source actuelle | Source Odoo | Owner | Fréquence |
|-----|-----------|----------------|-------------|-------|-----------|
| OTIF | % BL livrés complets à temps | Excel J+1 | stock.picking | Logistique | Quotidien |
| Fill Rate | Qtés livrées / commandées | Papier | logistics.line | Magasinier | Par BL |
| DSO | Encours / CA × 30 | Excel | account.move | Comptable | Mensuel |
| Encours échus | Factures > échéance | Excel | account.move | DAF | Hebdo |
| Coût litiges | Somme litiges ouverts | Excel | parabox.litige | ADV | Hebdo |
| Fiabilité stock | % produits sans écart inventaire | Aucune | stock.quant | Magasinier | Mensuel |

---

## Note méthodologique finale

```html
<div class="methodology-note">
  <h4>📌 Note méthodologique</h4>
  <p>Ce support distingue explicitement :</p>
  <ol>
    <li>Le fonctionnement réel observé chez PARABOX (AS-IS)</li>
    <li>Les capacités standard d'Odoo 17 Community</li>
    <li>Les développements MVP nécessaires</li>
    <li>Le travail concret à réaliser pour une démonstration crédible</li>
  </ol>
  <p><strong>Aucun outil payant. Aucune licence Enterprise. Tout fonctionne en local sur localhost:8069.</strong></p>
</div>
```

---

## ✅ Checklist Phase 8

- [ ] 10 onglets présents
- [ ] Blocs AS-IS / Standard / MVP
- [ ] Badges de réalité
- [ ] Onglet zones grises
- [ ] Onglet KPI
- [ ] Note méthodologique
- [ ] Standalone
- [ ] Test navigateur + mobile

# PARABOX — Projet MATCH
## Document Explicatif — CAP2026

**Auteur :** Équipe CAP2026 PARABOX
**Date :** Avril 2026
**Version :** 1.0 — Soutenance
**Technologie :** Odoo 17 Community | Python 3.10 | PostgreSQL | Zéro licence payante

---

## Page 1 — Résumé Exécutif

### Contexte PARABOX

PARABOX est un distributeur marocain de parapharmacie implanté à Casablanca. La société réalise environ 130 MDH de chiffre d'affaires annuel, dessert plus de 100 pharmacies et para-pharmacies en B2B, exploite 10 points de vente PARASHOP en B2C, et compte 60 collaborateurs répartis entre la direction commerciale, la logistique, la comptabilité et le terrain. L'entrepôt central couvre 1 200 m². Les outils actuels sont fragmentés : commandes reçues par WhatsApp, saisie manuelle dans Microsoft Access, facturation sous Ciel Compta, suivi encours sous Excel.

### Problème central

PARABOX facture ce qui est **commandé** (BC), non ce qui est **livré** (BL). Conséquence directe : si le livreur remet 8 boîtes au lieu des 10 commandées, la facture porte sur 10. Le client conteste. Aucune preuve de livraison opposable n'existe. Ce dysfonctionnement génère environ **3 MDH/an de litiges non recouvrés** et expose **10 MDH d'encours** à un risque de contestation.

### Solution choisie — Projet MATCH

Le Projet MATCH déploie **Odoo 17 Community** en installation locale Windows, exposé via ngrok pour la démo. L'acronyme MATCH résume le flux cible : **BC → BL (livré réel) → Facture → Signature sécurisée → Zéro litige**. Six modules Python custom complètent les fonctionnalités natives d'Odoo Community pour couvrir les besoins spécifiques PARABOX.

### Résultats attendus

| Indicateur | Avant | Après | Gain |
|-----------|-------|-------|------|
| Litiges facturation | ~3 MDH/an | ~0,9 MDH/an | **−2,1 MDH/an** |
| DSO moyen | >90 jours | ~60 jours | **~3 MDH trésorerie libérée** |
| Temps ADV ressaisie | ~2h/jour | ~0,2h/jour | **~250k DH/an** |
| Coût projet (open source) | — | — | **0 DH de licence** |
| Payback estimé | — | — | **< 6 mois** |

### Stack technique

Odoo 17 Community · Python 3.10 · PostgreSQL · Windows local · ngrok accès externe · ReportLab PDF · Chart.js · SHA-256 cryptographie · Zéro SaaS · Zéro licence payante.

---

## Page 2 — Flux Logistique AS-IS vs TO-BE

### Tableau comparatif complet

| Étape | AS-IS PARABOX | TO-BE Odoo standard | MVP Custom MATCH |
|-------|---------------|---------------------|------------------|
| Commande client | WhatsApp / téléphone → ressaisie ADV dans Excel. Risque d'oubli, doublons, erreurs de prix. | Devis Odoo structuré avec lignes produits, prix, UdM, remises. Workflow Devis → BC confirmé. | Contrôle crédit automatique à la confirmation. Blocage + dérogation ADV traçable. |
| Vérification crédit | Balance âgée Excel consultée manuellement la veille. Aucun blocage automatique. | Credit hold manuel possible sur la fiche client. | `parabox_credit_control` : blocage auto si encours + montant > limite. Log dérogation. |
| Préparation | Liste papier en entrepôt. Picking manuel. Pas de lien avec lots. | Picking Odoo, move.lines par produit, obligation lot si tracking='lot'. | `parabox_logistics_tracking` : 4 états (Commandé / Préparé / Chargé / Livré). Écarts tracés. |
| Livraison / BL | BL papier signé à la main. Feuille perdue dans 30% des cas. Pas de preuve en cas de litige. | BL Odoo validé avec lots. PDF envoyable par email. Pas de signature native Community. | `parabox_sign` : OTP 6 chiffres + canvas BIC + GPS + IP + PDF SHA-256. Preuve non répudiable. |
| Facturation | Sur quantité **commandée** (BC). Si livraison partielle → client conteste → litige certain. | Politique "Quantités livrées" configurable. Facture sur BL validés. | `sale_default_invoice_policy = 'delivery'` configuré. Facturation automatiquement sur livré réel. |
| Paiement | Cash, chèques, traites suivis dans Excel. Lettrage manuel. Chèques rejetés non tracés. | Paiement simple Odoo : un mode, un montant. Plusieurs paiements possibles mais sans plan. | `parabox_encaissement` : plan multi-lignes (cash + chèque + traite + virement). Statut auto. |
| Litige | Email / téléphone. Non relié aux documents. Non tracé. Pas de SLA. | Aucun module litige natif dans Community. | `parabox_litige` : kanban 5 étapes, lien BC/BL/Facture/Avoir, SLA automatique. |
| Pilotage | Excel J+1. Décisions basées sur données de la veille. | Reporting Odoo basique (pivot, graph, liste). | `parabox_dashboard` : 10 KPIs Finance + Logistique, Chart.js, refresh 60 secondes. |

### Flux TO-BE schématisé

```
Pharmacie passe commande
        ↓
[SALES] BC — S-PARA-2026-XXXXX  ←── Contrôle crédit automatique
        ↓ génération automatique
[INVENTORY] BL — BL-PARA-2026-XXXXX
        ↓ magasinier prépare + scanne lot/DLC
[SIGN] Livreur → OTP email → Client signe (BIC + GPS) → Hash PDF généré
        ↓ BL validé sur quantités réellement livrées
[INVOICE] Facture — FAC-PARA-2026-XXXXX — sur QTÉ LIVRÉE (jamais QTÉ COMMANDÉE)
        ↓
[ENCAISSEMENT] Cash / Chèque / Traite → Plan multi-modes → Lettrage
        ↓
[DASHBOARD] KPIs mis à jour en temps réel pour la Direction
```

---

## Page 3 — Architecture Odoo Community

### Pourquoi Odoo Community et non Enterprise

La version Enterprise d'Odoo coûte environ 25 € par utilisateur et par mois, soit pour 7 utilisateurs PARABOX environ 21 000 DH par an en licence logicielle, auxquels s'ajoutent les frais d'hébergement SaaS. Dans le cadre d'un projet CAP2026 à budget nul, ce coût est rédhibitoire. La version Community est open source, distribuée sous licence LGPL-3, entièrement en Python avec un ORM accessible et modifiable. Les fonctionnalités Enterprise manquantes sont compensées par des développements Python custom documentés et maintenables.

### Modules Odoo natifs installés et justifications

| Module | Justification technique |
|--------|------------------------|
| `sale_management` | Flux commandes B2B + politique `invoice_policy = 'delivery'` = cœur du Projet MATCH |
| `stock` | Gestion entrepôt, lots, DLC, picking 2-step (Pick + Ship), backorders |
| `purchase` | Réapprovisionnement fournisseurs, règles min/max, réception avec lots |
| `account` | Facturation, paiements, lettrage, encours client, DSO |
| `crm` | Pipeline commercial, opportunités, suivi relation clients |
| `contacts` | Base partenaires unifiée (clients + fournisseurs) |
| `point_of_sale` | Canal B2C PARASHOP — caisse tactile, synchronisation stock |

### Architecture d'installation locale

```
Windows PC (localhost:8069)
├── PostgreSQL 14 ──── base : parabox_db
├── Python 3.10 ──── Odoo 17 Community
│   ├── Modules natifs (sale, stock, account…)
│   └── Modules custom PARABOX
│       ├── parabox_credit_control
│       ├── parabox_logistics_tracking
│       ├── parabox_litige
│       ├── parabox_encaissement
│       ├── parabox_product_alias
│       ├── parabox_sign
│       ├── parabox_dashboard
│       └── parabox_mobile
└── Tunnel ngrok ──── https://[token].ngrok.io ──── Jury / Mobile
```

### Comparaison Community vs Enterprise pour PARABOX

| Fonctionnalité requise | Enterprise | Community | Solution MVP développée |
|------------------------|-----------|-----------|------------------------|
| Signature électronique BL | ✅ Odoo Sign | ❌ Absent | `parabox_sign` : OTP + BIC + SHA-256 |
| Dashboard BI temps réel | ✅ Odoo BI | ⚠️ Basique | `parabox_dashboard` : Chart.js |
| Contrôle crédit automatique | ✅ Natif | ❌ Absent | `parabox_credit_control` |
| Approbations workflow | ✅ Approvals | ⚠️ Limité | Workflow sur `sale.order` |
| Gestion litiges | ❌ Absent aussi | ❌ Absent | `parabox_litige` : kanban + SLA |
| Plan encaissement multi-modes | ❌ Absent aussi | ❌ Absent | `parabox_encaissement` |

---

## Page 4 — Utilisateurs, Rôles et Droits

### Fiches utilisateurs

**Administrateur — Eric Kambiré — admin@parabox.ma**
Mission : configuration système, gestion des modules, supervision globale.
Modules accessibles : tous.
Peut faire : créer, modifier, supprimer, configurer toute l'instance Odoo.
Ne peut pas : rien de bloqué.
Dans la démo : configuration initiale, vérification intégrité PDF.

**Commercial — Yassine El Idrissi — commercial@parabox.ma**
Mission : créer et gérer les commandes clients B2B.
Modules accessibles : CRM, Ventes, lecture Inventaire.
Peut faire : créer devis, confirmer BC, consulter stock, créer opportunités CRM.
Ne peut pas : valider BL, créer factures, accorder dérogations crédit, voir comptabilité.
Dans la démo : S1 (créer BC PARFUMERIE ATLAS), S3 (BC bloqué PARA TALBORJT).

**ADV — Fatima Benali — adv@parabox.ma**
Mission : administration des ventes, dérogations crédit, gestion litiges.
Modules accessibles : Ventes, Inventaire (lecture), Litiges, Dérogations.
Peut faire : accorder/refuser dérogations crédit, ouvrir et gérer litiges, valider conditions commerciales.
Ne peut pas : créer factures, accéder à la comptabilité complète.
Dans la démo : S3 (dérogation crédit), S5 (ouverture litige).

**Magasinier — Omar Tazi — magasinier@parabox.ma**
Mission : préparer les commandes, valider les réceptions, gérer le stock physique.
Modules accessibles : Inventaire complet, Achats (réception).
Peut faire : créer/valider pickings, saisir quantités réelles, gérer lots, réceptionner livraisons fournisseurs.
Ne peut pas : créer commandes clients, accéder à la comptabilité.
Dans la démo : S1 (picking + saisie lots), S2 (livraison partielle + backorder), S4 (réception réappro).

**Livreur — Karim Alami — livreur@parabox.ma**
Mission : livrer les commandes, déclencher la signature électronique.
Modules accessibles : Interface mobile `/parabox/mobile/livreur`, pickings assignés.
Peut faire : voir ses BL du jour, envoyer OTP au client, consulter détail produits.
Ne peut pas : créer commandes, modifier stocks, accéder à la comptabilité.
Dans la démo : S1 (interface mobile → OTP → validation livraison).

**Comptable — Amina Chraibi — comptable@parabox.ma**
Mission : gérer la facturation, les paiements, le suivi encours.
Modules accessibles : Comptabilité complète, plans d'encaissement.
Peut faire : confirmer factures, enregistrer paiements, gérer plans d'encaissement multi-modes, lettrage.
Ne peut pas : créer commandes, modifier stock.
Dans la démo : S6 (plan encaissement multi-instruments sur facture 4 800 DH).

**Direction — Karim Haddad — direction@parabox.ma**
Mission : pilotage stratégique via les KPIs Finance + Logistique.
Modules accessibles : Dashboard PARABOX, rapports Odoo, lecture tous modules.
Peut faire : consulter tous les KPIs, déclencher escalades litiges.
Ne peut pas : modifier données opérationnelles.
Dans la démo : Dashboard temps réel mis à jour après chaque scénario.

### Matrice des droits synthétique

| Module | Admin | Commercial | ADV | Magasinier | Livreur | Comptable | Direction |
|--------|-------|-----------|-----|-----------|---------|----------|-----------|
| CRM | Complet | Complet | Lecture | ✗ | ✗ | Lecture | Lecture |
| Ventes | Complet | Créer/Confirm | Valider | Lecture | ✗ | Lecture | Lecture |
| Inventaire | Complet | Lecture | Lecture | Complet | Picking | Lecture | Lecture |
| Achats | Complet | ✗ | Lecture | Réception | ✗ | Valider | Lecture |
| Comptabilité | Complet | Lecture | Lecture | ✗ | ✗ | Complet | Lecture |
| Dashboard | Complet | KPI perso | Ops | Stock | ✗ | Finance | Complet |
| Litiges | Complet | Lecture | Complet | Lecture | ✗ | Lecture | Lecture |
| Dérogations | Complet | ✗ | Approuver | ✗ | ✗ | ✗ | Lecture |

---

## Page 5 — Module parabox_credit_control

### Problème adressé

PARABOX expose environ 10 MDH d'encours clients, dont une partie significative est portée par des clients dont la situation financière est fragile. Sans contrôle automatique, un commercial peut confirmer une commande de 15 000 DH pour un client déjà endetté de 18 000 DH sans que personne ne soit alerté. La balance âgée est consultée manuellement dans Excel avec un décalage de 24 heures.

### Logique métier — Arbre de décision

```
Clic "Confirmer commande"
          ↓
  Client marqué credit_hold = True ?
  ├── OUI → Blocage immédiat + activité ADV + exception levée
  └── NON
          ↓
  credit_limit > 0 ?
  ├── NON → Confirmation normale (limite désactivée)
  └── OUI
          ↓
  encours_actuel + amount_total > credit_limit ?
  ├── NON → Confirmation normale
  └── OUI
          ↓
    credit_derogation = True ? (dérogation déjà accordée)
    ├── OUI → Confirmation normale (log existant)
    └── NON
            ↓
      Créer activité pour chaque ADV (group_sale_manager)
      Mettre credit_hold_blocked = True
      Lever UserError avec chiffres précis
            ↓
      ADV examine → accorde ou refuse
      └── Accordée → credit_derogation = True, log (qui/quand/raison) → Confirmation
      └── Refusée → Commande reste bloquée, commercial recontacte client
```

### Champs techniques ajoutés

Sur `res.partner` : `credit_limit` (Float, défaut 10 000 DH), `credit_hold` (Boolean), `encours_actuel` (Float computed depuis factures ouvertes), `taux_utilisation_credit` (Float computed).

Sur `sale.order` : `credit_hold_blocked` (Boolean readonly), `credit_derogation` (Boolean), `credit_derogation_by` (Many2one res.users), `credit_derogation_dt` (Datetime), `credit_derogation_note` (Text).

### Justification du choix technique

La surcharge de `action_confirm()` par héritage ORM Python est l'approche standard Odoo. Elle s'intègre sans patch ni monkey-patching, est mise à jour automatiquement avec les versions d'Odoo, et ne casse pas les autres modules qui appellent `action_confirm()`. L'activité automatique assure que l'ADV est notifié même si l'email ne fonctionne pas.

### Limites honnêtes

La `credit_limit` est saisie manuellement — il n'y a pas de scoring externe automatique. L'encours calculé ne tient compte que des factures Odoo, pas des engagements hors Odoo. En production, une synchronisation avec le système bancaire serait nécessaire pour un scoring fiable.

---

## Page 6 — Module parabox_sign

### Problème adressé

Le bon de livraison papier est perdu dans environ 30% des cas selon les témoignages terrain. Même quand il est présent, la signature manuscrite est souvent illisible, non datée et non localisée. En cas de litige, PARABOX ne peut pas prouver que la livraison a eu lieu ni que le client a accepté les quantités. La signature électronique native d'Odoo n'existe que dans la version Enterprise.

### Architecture de sécurité en 3 phases

**Phase 1 — Avant la livraison**
Le livreur ouvre la demande de signature dans Odoo et clique "Envoyer OTP". Le système génère 6 chiffres aléatoires via `random.SystemRandom()`, calcule leur hash SHA-256 (jamais l'OTP en clair en base), stocke le hash avec une expiration à 30 minutes, et envoie l'email au client avec l'OTP et l'URL unique de signature.

**Phase 2 — Sur le terrain**
Le client ouvre l'URL `/parabox/sign/<token>` sur son téléphone (aucune installation requise). Il entre les 6 chiffres, le système compare le hash. Si correct, il trace sa signature sur le canvas HTML5 avec son doigt (bibliothèque JavaScript custom en mode BIC). Le GPS est capturé si autorisé par le navigateur. L'IP et le User-Agent sont enregistrés automatiquement.

**Phase 3 — Après la signature**
Le PDF du BL est généré avec la signature incrustée via ReportLab. Le hash SHA-256 du PDF binaire est calculé et stocké en base (`pdf_hash`). Un email de confirmation est envoyé au client avec le PDF en pièce jointe. À tout moment, le bouton "Vérifier intégrité PDF" recalcule le hash et le compare au hash stocké — toute modification du PDF, même mineure, sera détectée.

### Mode dégradé

Si le client n'a pas reçu l'OTP (réseau indisponible, email incorrect, batterie vide), le livreur peut activer le mode dégradé. La signature est enregistrée sans OTP, marquée `mode = 'degrade'`, et une activité est créée automatiquement pour l'ADV qui doit vérifier la livraison. Le workflow logistique n'est pas bloqué.

### Limites honnêtes

Cette implémentation ne constitue pas une signature électronique qualifiée au sens de la loi 53-05 marocaine sur les échanges électroniques ou du règlement européen eIDAS. Elle constitue cependant un commencement de preuve par écrit recevable devant un tribunal commercial marocain, suffisant pour résoudre 95% des litiges B2B de distribution.

---

## Page 7 — Modules Logistique

### parabox_logistics_tracking — Traçabilité 4 états

**Problème :** Dans le flux actuel, il est impossible de savoir si un écart entre le BC et le BL s'est produit à la préparation (le magasinier a préparé moins), au chargement (le chauffeur a oublié un colis) ou à la livraison (le client a refusé une référence). Odoo standard ne trace que l'état final.

**Solution :** Le modèle `parabox.logistics.line` ajoute une ligne par produit par BL avec les champs `qty_ordered` (BC), `qty_prepared` (picking), `qty_loaded` (chargement véhicule) et `qty_delivered` (livré réel). Les écarts sont calculés automatiquement. Un champ `substitution` avec `product_sub_id` documente les remplacements de produits. Le taux de service par BL est calculé en pourcentage. Les lignes sont créées automatiquement lors de la validation du BL sortant.

**Impact concret :** Fill Rate calculable par BL, par client, par livreur. Écarts tracés avec responsabilité identifiée. Substitutions documentées et opposables.

### parabox_litige — Kanban SLA

**Problème :** Les litiges PARABOX sont actuellement gérés par email et téléphone. Aucun document n'est lié au litige. Aucun SLA n'existe. La direction n'a aucune visibilité sur le montant total des litiges ouverts.

**Solution :** Le modèle `parabox.litige` relie chaque litige à la commande (BC), au BL, à la facture et à l'avoir. Les étapes kanban (Ouvert → En analyse → En attente client → Résolu → Clos) permettent un suivi visuel. Le SLA est calculé automatiquement : alerte orange dès 3 jours sans résolution, escalade automatique vers la direction à 7 jours (activité créée). Un cron quotidien vérifie les SLA.

**Impact concret :** Dossier litige complet en un clic. Réponse client garantie sous 24h (objectif). Montant total litiges visible dans le Dashboard.

### parabox_encaissement — Plan multi-instruments

**Problème :** Un client paie souvent en plusieurs fois avec des modes différents — une partie en cash immédiat, un chèque sur 30 jours, une traite sur 60 jours. Odoo standard gère un paiement à la fois. Le suivi multi-modes se fait dans Excel, sans lien avec la facture Odoo.

**Solution :** Le modèle `parabox.encaissement` crée un plan de paiement lié à une facture `account.move`. Les lignes de paiement (`parabox.encaissement.ligne`) portent le mode (cash, chèque, traite, virement), le montant, la date d'échéance et le statut (Reçu, Encaissé, Rejeté). Le solde restant et le statut global (En attente / Partiel / Soldé) sont recalculés automatiquement à chaque modification.

**Impact concret :** Encours réel fiable. Relances ciblées sur les chèques à encaisser et les traites à l'échéance. DSO calculable correctement.

---

## Page 8 — Dashboard Direction

### Problème adressé

La Direction de PARABOX prend ses décisions commerciales et logistiques sur la base d'un tableau Excel mis à jour manuellement chaque matin. Les chiffres ont donc 12 à 24 heures de retard. En cas de rupture stock critique ou de dérapage DSO, la réaction est tardive.

### Architecture technique

Le module `parabox_dashboard` utilise l'ORM Odoo pour calculer les 10 KPIs côté serveur Python, retourne les données en JSON via un appel RPC, et les rend avec Chart.js (bibliothèque open source MIT, chargée depuis CDN). Le composant OWL (framework JavaScript d'Odoo) orchestre l'affichage et le rafraîchissement automatique toutes les 60 secondes.

### Les 10 KPIs — Formules et sources

**Finance :**

1. **CA du mois en cours** = `sum(amount_untaxed)` des `account.move` de type `out_invoice` postées dans le mois courant. Comparaison automatique avec le mois précédent (évolution en %).

2. **Encours clients total** = `sum(amount_residual)` des factures ouvertes non payées. Nombre de factures concernées affiché.

3. **DSO** (Days Sales Outstanding) = `(encours_total / CA_90j) × 90`. Alerte rouge si DSO > 45 jours.

4. **Montant litiges ouverts** = `sum(montant_litige)` des `parabox.litige` dont l'étape n'est pas "Clos". Alerte rouge si > 50 000 DH.

5. **Factures en retard** = `account.move` postées, non payées, dont `invoice_date_due < today`. Montant total et nombre de factures.

**Logistique :**

6. **OTIF** (On Time In Full) = BL dont `date_done ≤ scheduled_date` / total BL validés sur 30 jours × 100. Alerte rouge si OTIF < 90%.

7. **Fill Rate** = lignes de BL où `quantity_done ≥ product_uom_qty` / total lignes × 100.

8. **Ruptures stock** = nombre de `product.product` avec `qty_available ≤ 0`. Liste des 3 premières références affichée en rouge.

9. **BL en cours** = `stock.picking` sortants en état `confirmed` / `assigned` / `waiting`.

10. **Reliquats ouverts** = BL avec `backorder_id ≠ False` et état non terminé.

### Design UX

Layout deux colonnes sur grand écran. Codes couleur : vert (objectif atteint), orange (attention), rouge (action requise immédiate). Trois graphiques Chart.js : barres CA mensuel 6 mois, donut litiges par type, barres horizontales Top 5 encours clients. Horloge temps réel en entête. Accessible uniquement depuis le compte `direction@parabox.ma`.

---

## Page 9 — Script de Démo

### Les 6 scénarios résumés

**Scénario 1 — Commande normale B2B (8 min) — commercial@parabox.ma**
Données : PARFUMERIE ATLAS, P001 × 10 + P009 × 5.
Étapes : BC confirmé → picking lots → OTP mobile livreur → signature canvas → BL validé → facture sur livré réel → paiement cash.
**Point fort jury :** "La facture a été créée sur les quantités livrées, pas commandées — c'est le cœur du Projet MATCH."

**Scénario 2 — Livraison partielle + backorder (5 min) — magasinier@parabox.ma**
Données : PARASHOP, P002 × 20, stock = 12.
Étapes : BC 20 → BL 12 + backorder 8 → facture 12 uniquement.
**Point fort jury :** "Le client ne paie que ce qu'il a reçu. Le backorder sera facturé à la livraison suivante."

**Scénario 3 — Blocage crédit + dérogation (4 min) — commercial + adv@parabox.ma**
Données : PARA TALBORJT, limite 3 000 DH, encours 2 800 DH, commande +725 DH.
Étapes : BC confirmé → blocage auto → notification ADV → dérogation accordée avec raison → commande confirmée → log tracé.
**Point fort jury :** "Aucun commercial ne peut dépasser la limite de crédit sans validation ADV loggée. Audit complet."

**Scénario 4 — Réapprovisionnement automatique (3 min) — magasinier@parabox.ma**
Données : P001, règle Min 20 / Max 100.
Étapes : stock visible sous le minimum → Inventaire > Réapprovisionnement → PO généré → réception avec lot → stock vert.
**Point fort jury :** "Aucune intervention humaine nécessaire pour déclencher la commande fournisseur."

**Scénario 5 — Litige BC ≠ BL (3 min) — adv@parabox.ma**
Données : PARAPHARMACIE GUÉLIZ, écart quantité 5 unités × 90 DH = 450 DH.
Étapes : litige ouvert → lié au BC + BL → kanban Ouvert → Analyse → Résolu → avoir créé → Clos.
**Point fort jury :** "Tout le dossier litige est dans Odoo : BC, BL, facture, avoir, communication client."

**Scénario 6 — Paiement multi-instruments (2 min) — comptable@parabox.ma**
Données : Facture 4 800 DH : cash 2 000 + chèque 1 800 (CHQ-047) + traite 1 000 (TRT-012, 60j).
Étapes : plan encaissement créé → 3 lignes saisies → statut Partiel → cash marqué Encaissé.
**Point fort jury :** "L'encours réel est connu à la ligne. Le DSO est calculable sans Excel."

### Checklist pré-démo

```
□ Backup DB parabox_db créé (copie PostgreSQL)
□ Stock P001 ≥ 20, P002 ≥ 12, P004 ≥ 5, P009 ≥ 10
□ Encours PARA TALBORJT configuré à 2 800 DH (créer facture ouverte)
□ ngrok actif : ngrok http 8069 → copier URL HTTPS
□ web.base.url mis à jour dans Odoo avec URL ngrok
□ SMTP testé : envoyer OTP de test → vérifier réception email
□ 7 comptes testés (login + password) sur navigateur
□ Dashboard visible sur direction@parabox.ma
□ reportlab installé : pip install reportlab --break-system-packages
□ 3 onglets Chrome ouverts : commercial / livreur mobile / direction dashboard
□ Téléphone de démo connecté + navigateur Chrome ouvert sur URL ngrok
```

### Formules clés à retenir pour le jury

1. *"La facture suit le BL, jamais le BC"* — Projet MATCH, politique `delivery`.
2. *"La signature est non répudiable : OTP prouvé + BIC tracé + hash SHA-256 anti-fraude."*
3. *"Le blocage crédit est automatique. La dérogation est loggée : qui, quand, combien, pourquoi."*
4. *"Le réapprovisionnement se déclenche sans intervention humaine dès que le stock passe sous le minimum."*
5. *"Le litige est relié à tous les documents : BC, BL, facture, avoir — dossier complet en 1 clic."*
6. *"Tout fonctionne en Odoo Community open source. Zéro licence payante. Zéro SaaS."*

---

## Page 10 — Limites, Honnêteté et Roadmap

### Ce que ce MVP ne fait pas — et pourquoi c'est acceptable

| Limitation | Raison technique/économique | Alternative MVP déployée |
|-----------|----------------------------|--------------------------|
| Pas de signature eIDAS qualifiée | Nécessite PKI certifiée + prestataire qualifié → coût et délais importants | OTP + hash SHA-256 = preuve suffisante pour 95% des litiges commerciaux marocains |
| Pas de scoring crédit externe | API scoring bancaire payante + RGPD données bancaires | `credit_limit` manuel + dérogation tracée = contrôle opérationnel immédiat |
| Pas d'app mobile native iOS/Android | Développement natif = 3-6 mois + App Store + certificats | Interface web responsive sur mobile via ngrok = fonctionnel pour la démo |
| Pas de BI avancé (PowerBI / Tableau) | Licences payantes ou complexité d'intégration | Chart.js open source connecté à l'ORM Odoo = 10 KPIs temps réel |
| Pas de connexion Ciel Compta | Migration hors scope MVP | Odoo remplace complètement Ciel — aucun besoin de pont |
| Données fournisseurs fictives | Master data réelle à fiabiliser en production | CSV import prêt — structure validée |
| Module qualité (retours, SAV) absent | Hors scope Phase 1 | Structure entrepôt Odoo permet l'extension |
| POS PARASHOP simplifié | Priorité au flux B2B source des litiges | Module `point_of_sale` installé et extensible |

### Roadmap post-MVP

**Court terme — 1 à 3 mois**
Formation des équipes opérationnelles (commercial, ADV, magasinier, comptable — 2 jours chacun). Fiabilisation complète du master data (21 clients réels + fournisseurs réels). Migration des données historiques Ciel Compta vers Odoo. Tests picking réels en entrepôt avec le magasinier. Configuration SMTP production pour les emails OTP.

**Moyen terme — 3 à 6 mois**
Module qualité : retours produits, quarantaine, alertes DLC expirantes. Extension POS PARASHOP : synchronisation stock temps réel entre le point de vente et l'entrepôt principal. Portail B2B pharmacies : commande en ligne directe sans WhatsApp, lié au workflow BC Odoo. Module prévision : analyse historique ventes pour réapprovisionnement prédictif. Connexion transporteur externe pour suivi livraison GPS.

**Long terme — 6 à 12 mois**
Application mobile livreur native (React Native ou Flutter) remplaçant l'interface web mobile. Scoring crédit client automatique basé sur l'historique Odoo. EDI fournisseurs pour bons de commande automatiques. Dashboard BI avancé via Metabase open source connecté directement à PostgreSQL. Signature électronique qualifiée si requis légalement.

### ROI Consolidé

| Indicateur | Avant MVP | Après MVP | Gain annuel estimé |
|-----------|-----------|-----------|-------------------|
| Litiges facturation | ~3,0 MDH/an | ~0,9 MDH/an | **+2,1 MDH** |
| Trésorerie (DSO −30j) | 90+ jours | ~60 jours | **~3,0 MDH libérés** |
| Temps ADV ressaisie | ~2h/jour | ~0,2h/jour | **~250 k DH/an** |
| Erreurs picking | ~15% | <3% | **Qualité de service** |
| Ruptures stock | Fréquentes | Rares (min/max auto) | **CA préservé** |
| **Gain total Year 1** | | | **~5,35 MDH** |
| **Coût projet (open source)** | | | **0 DH** |
| **Payback** | | | **< 6 mois** |

### Message final pour le jury

> Ce projet ne prétend pas avoir tout déployé en production.
>
> Il démontre qu'avec Odoo 17 Community open source, une équipe peut construire
> une solution logistique et financière crédible, traçable et non répudiable —
> sans budget logiciel, sans licence Enterprise, en partant du terrain réel PARABOX.
>
> Le MVP couvre les 80% des irritants qui génèrent 80% des pertes financières :
> 3 MDH de litiges et 10 MDH d'encours à risque.
>
> C'est suffisant pour prouver la valeur.
> C'est suffisant pour convaincre la direction.
> C'est suffisant pour déployer.

---

*Document généré — CAP2026 — Odoo 17 Community — Zéro licence payante*

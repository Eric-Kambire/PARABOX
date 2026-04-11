# Phase 9 — Document Explicatif (10 pages)
## Dossier output : /docs/CAP2026_Document_Explicatif.md

---

## Objectif pour Claude Coworker

Générer un document Markdown de 10 pages denses, défendable en soutenance.
Double registre : technique (développeur) + métier (jury/prof/client).
Chaque choix architectural doit être justifié.
Ton : clair, structuré, honnête, professionnel. Zéro marketing.

> Convertir ensuite en Word via pandoc :
> `pandoc CAP2026_Document_Explicatif.md -o CAP2026_Document_Explicatif.docx`

---

## Page 1 — Résumé Exécutif

Rédiger :
- Contexte PARABOX (5 lignes max) :
  distributeur parapharmacie marocain, 130 MDH CA,
  100+ pharmacies B2B, 10 PARASHOP B2C, 60 collaborateurs,
  entrepôt 1 200 m², outils actuels fragmentés (WhatsApp/Access/Ciel/Excel)

- Problème central :
  PARABOX facture ce qui est commandé, pas ce qui est livré.
  Écart BC ≠ BL → ~3 MDH/an litiges + ~10 MDH encours à risque.

- Solution choisie :
  Odoo 17 Community open source, installation locale Windows,
  exposition via ngrok + port 8069.
  Projet MATCH : BC → BL (livré réel) → Facture → Signature sécurisée.

- Résultats attendus :
  Litiges -70% (~2,1 MDH/an économisés)
  DSO -30 jours (~3 MDH trésorerie libérée)
  ADV -2h/jour de ressaisie
  Payback < 6 mois

- Stack technique :
  Odoo 17 Community | Python 3.10 | PostgreSQL | Windows local
  ngrok pour accès externe | zéro licence payante | zéro SaaS

---

## Page 2 — Flux Logistique AS-IS vs TO-BE

Rédiger un tableau comparatif pour chaque étape du flux :

| Étape | AS-IS | TO-BE Odoo | MVP custom |
|-------|-------|-----------|-----------|
| Commande client | WhatsApp/téléphone → ressaisie ADV | Devis Odoo structuré | Capture rapide récurrente |
| Vérification crédit | Balance âgée Excel J-1, aucun blocage | Credit hold manuel | Blocage auto + dérogation tracée |
| Préparation | Liste papier, picking manuel | Picking Odoo standard | Suivi 4 états + écarts |
| Livraison / BL | BL papier signé, souvent perdu | BL Odoo validé | Signature OTP + BIC + hash PDF |
| Facturation | Sur commandé (pas livré) | Sur livré si configuré | Projet MATCH configuré |
| Paiement | Excel, lettrage manuel | Paiement simple Odoo | Multi-instruments + matching |
| Litige | Email/téléphone, pas tracé | Aucun module natif | Module litige relié docs |
| Pilotage | Excel J+1, décisions à l'aveugle | Reporting Odoo basique | Dashboard temps réel Chart.js |

Puis schéma texte du flux TO-BE :
```text
Pharmacie commande
      ↓
[SALES] BC S-PARA-2026-XXXXX
      ↓ auto
[INVENTORY] BL BL-PARA-2026-XXXXX
      ↓ magasinier prépare + assigne lot/DLC
[SIGN] Livreur envoie OTP → Client signe BIC → Hash PDF
      ↓ BL validé
[INVOICE] Facture FAC-PARA-2026-XXXXX sur QTÉ LIVRÉE
      ↓
[ENCAISSEMENT] Cash/Chèque/Traite → Lettrage
      ↓
[DASHBOARD] KPIs mis à jour temps réel
```

---

## Page 3 — Architecture Odoo Community

Rédiger :

### Pourquoi Odoo Community et pas Enterprise
- Enterprise : licence ~25€/user/mois → ~21 000 DH/an pour 7 users
- Community : open source, gratuit, code Python accessible
- Modules manquants Enterprise compensés par développements custom Python
- Cohérent avec un projet étudiant à budget zéro

### Modules installés et justification
| Module | Justification |
|--------|--------------|
| sale_management | Flux commandes + politique Invoice what is delivered |
| stock | Gestion entrepôt, lots, DLC, picking |
| purchase | Réapprovisionnement fournisseurs |
| account | Facturation + paiements + lettrage |
| crm | Pipeline commercial |
| point_of_sale | Canal B2C PARASHOP (simplifié) |

### Architecture locale
```text
Windows PC
  └── PostgreSQL (parabox_db)
  └── Python 3.10 + Odoo 17 Community
  └── localhost:8069
        ↓ accès externe
  ngrok tunnel OU règle pare-feu port 8069
        ↓
  Jury/Client (navigateur)
```

### Contraintes Community vs Enterprise
| Fonctionnalité | Enterprise | Community | Solution MVP |
|---------------|-----------|-----------|-------------|
| Odoo Sign | ✅ Natif | ❌ Absent | parabox_sign custom |
| BI/Dashboards | ✅ Natif | ❌ Basique | Chart.js custom |
| Approvals | ✅ Natif | ⚠️ Limité | Workflow custom |
| Credit control | ✅ Natif | ❌ Absent | parabox_credit_control |

---

## Page 4 — Utilisateurs, Rôles et Droits

Rédiger une fiche pour chaque utilisateur :

### Format par utilisateur
**[Rôle] — [Nom] — [Login]**
- Mission : [1 phrase]
- Modules accessibles : [liste]
- Ce qu'il peut faire : [create/edit/validate/approve/read]
- Ce qu'il NE peut PAS faire : [liste]
- Dans la démo : [action concrète qu'il effectue]

### Les 7 utilisateurs
Développer chaque fiche pour :
1. Admin — Eric Kambiré — admin@parabox.ma
2. Commercial — Yassine El Idrissi — commercial@parabox.ma
3. ADV — Fatima Benali — adv@parabox.ma
4. Magasinier — Omar Tazi — magasinier@parabox.ma
5. Livreur — Karim Alami — livreur@parabox.ma
6. Comptable — Amina Chraibi — comptable@parabox.ma
7. Direction — Karim Haddad — direction@parabox.ma

Puis matrice synthétique :
| Module | Admin | Comm. | ADV | Maga. | Livr. | Compt. | Dir. |
|--------|-------|-------|-----|-------|-------|--------|------|
| CRM | Full | Full | Read | ✗ | ✗ | Read | Read |
| Sales | Full | Create | Valid. | ✗ | ✗ | Read | Read |
| Inventory | Full | Read | Read | Full | Pick | Read | Read |
| Purchase | Full | ✗ | Read | Receive | ✗ | Valid. | Read |
| Invoicing | Full | Read | Read | ✗ | ✗ | Full | Read |
| Dashboard | Full | KPI perso | Ops | Stock | ✗ | Finance | Full |

---

## Page 5 — Module parabox_credit_control

Rédiger :
- Problème adressé avec chiffre : ~10 MDH encours à risque, zéro blocage automatique
- Logique métier (schéma décision) :
```text
Confirmer commande
      ↓
Calculer encours client (factures non payées)
      ↓
encours + montant_commande > credit_limit ?
      ↓ OUI                    ↓ NON
  Bloquer (credit_hold)    Confirmer normalement
      ↓
  Notifier ADV
      ↓
  ADV approuve + saisit raison
      ↓
  Log dérogation (qui/quand/montant/raison)
      ↓
  Commande confirmée
```
- Champs techniques ajoutés (res.partner + sale.order)
- Justification choix technique : surcharge ORM Python, natif Odoo
- Limites honnêtes : credit_limit saisi manuellement, pas de scoring externe
- Ce que ça change concrètement : PARA TALBORJT ne peut plus commander au-delà de 3 000 DH sans validation ADV

---

## Page 6 — Module parabox_sign

Rédiger :
- Problème adressé : BL papier perdu dans 30% des cas → litige sans preuve
- Architecture sécurité (schéma) :
```text
J-1 ou matin livraison :
  Odoo → génère OTP 6 chiffres → hash SHA-256 → stocke
  Odoo → email client avec OTP + lien unique signé (token JWT)

Jour livraison :
  Livreur → ouvre lien sur mobile
  Client → entre OTP → système compare hash → OK
  Client → signe avec doigt (canvas signature_pad.js)
  Système → capture : IP, timestamp, user-agent, GPS (si activé)
  PDF → généré avec signature incrustée (wkhtmltopdf/reportlab)
  Hash SHA-256 → calculé sur PDF final → stocké en base
  Email → envoyé client avec PDF signé en pièce jointe

Vérification intégrité :
  Recalculer hash → comparer avec hash stocké
  Si différent → FRAUDE DÉTECTÉE → alerte rouge
```
- Mode dégradé : OTP non reçu → signature sans OTP → workflow continue → alerte ADV
- Activation/désactivation : paramètre système Parabox > Signature
- Limites honnêtes : pas de signature eIDAS qualifiée (prototype MVP)
- Bibliothèques utilisées : signature_pad.js (MIT), hashlib Python, smtplib

---

## Page 7 — Modules Logistique

### parabox_logistics_tracking
- Problème : commandé ≠ préparé ≠ chargé ≠ livré, aucune trace dans Odoo standard
- Modèle parabox.logistics.line avec 4 champs quantité
- Vue tableau sur le BL : Commandé | Préparé | Chargé | Livré | Écart | Substitution
- Impact : Fill Rate calculable, écarts tracés, substitutions documentées

### parabox_litige
- Problème : litiges gérés par email/téléphone, non reliés aux documents
- Modèle parabox.litige avec liens BC + BL + Facture + Avoir
- Workflow kanban : Ouvert → Analyse → Attente client → Résolu → Clos
- SLA : alerte rouge > 3 jours, escalade direction > 7 jours
- Impact : dossier litige complet en 1 clic, réponse client < 24h

### parabox_encaissement
- Problème : client paie en plusieurs fois (cash + chèque + traite), lettrage manuel Excel
- Modèle plan d'encaissement + lignes avec mode de paiement
- Statut automatique : En attente → Partiel → Soldé
- Impact : encours réel fiable, relances ciblées, DSO calculable

---

## Page 8 — Dashboard Direction

Rédiger :
- Problème : pilotage Excel J+1 → décisions basées sur données périmées
- Architecture : ORM Odoo → calcul Python → JSON → Chart.js (open source MIT)
- 10 KPIs avec formule et source :

Finance (5 KPIs) :
1. CA mois en cours = sum(account.move.amount_total) du mois
2. Encours total = sum(account.move.amount_residual) non payées
3. DSO = (Encours / CA) × 30
4. Litiges ouverts = sum(parabox.litige.montant_litige) où statut != clos
5. Factures en retard = count(account.move) où date > invoice_date_due

Logistique (5 KPIs) :
6. OTIF = BL Done à temps / total BL × 100
7. Fill Rate = sum(qty_delivered) / sum(qty_ordered) × 100
8. Ruptures = count(produits où stock = 0)
9. BL en cours = count(stock.picking) où state = assigned
10. Reliquats = count(stock.picking) où backorder_id != False

- Design UX : 2 colonnes, alertes couleur (vert/orange/rouge), refresh 60s
- Accès : direction@parabox.ma + admin uniquement
- Justification : Chart.js open source, pas de BI payant, données Odoo temps réel

---

## Page 9 — Script de Démo

Rédiger le résumé des 6 scénarios avec pour chacun :
- Acteur connecté
- Données utilisées
- Étapes clés (5 lignes max)
- Point fort à souligner devant le jury

Puis checklist pré-démo :
```text
□ Backup DB créé
□ Données démo chargées (load_demo_data.py exécuté)
□ Odoo accessible via ngrok (URL testée)
□ Email SMTP testé (OTP reçu)
□ 7 comptes utilisateurs testés (connexion OK)
□ Stock > 0 pour produits de démo
□ Encours PARA TALBORJT = 2 800 DH (pour montrer blocage)
□ Dashboard visible sur direction@parabox.ma
□ Mode signature activé
□ Chrome ouvert sur 3 onglets : commercial / livreur / direction
```

Points clés à répéter devant le jury :
```text
1. "La facture suit le BL, jamais le BC" → Projet MATCH
2. "La signature est non répudiable : OTP + BIC + hash PDF"
3. "Le blocage crédit est automatique, la dérogation est tracée"
4. "Le réapprovisionnement se déclenche sans intervention humaine"
5. "Le litige est relié à tous les documents : BC, BL, facture, avoir"
6. "Tout fonctionne en Odoo Community open source, zéro licence payante"
```

---

## Page 10 — Limites, Honnêteté et Roadmap

### Ce que ce MVP ne fait PAS (et pourquoi c'est acceptable)

| Limitation | Raison | Alternative MVP |
|-----------|--------|----------------|
| Pas de signature eIDAS qualifiée | Coût + infra PKI complexe | OTP + hash SHA-256 = preuve suffisante MVP |
| Pas de scoring crédit externe | API bancaire payante | credit_limit manuel, dérogation tracée |
| Pas d'app mobile native | Développement iOS/Android hors scope | Web responsive sur mobile via ngrok |
| Pas de BI avancé (PowerBI/Tableau) | Licences payantes | Chart.js open source, données Odoo |
| Données fournisseurs fictives | Master data à fiabiliser en production | CSV import, structure prête |
| Pas de connexion Ciel Compta | Migration hors scope MVP | Odoo remplace Ciel complètement |
| Pas de module qualité (retours) | Hors scope Phase 1 | Structure entrepôt quality prête |
| Pas de POS PARASHOP complet | Simplifié pour MVP | Module POS installé, extensible |

---

### Ce qui reste à faire après MVP (Roadmap)

**Court terme (1-3 mois après démo)**
```text
□ Formation équipes : commercial, ADV, magasinier, comptable (2 jours chacun)
□ Fiabilisation master data complète (21 clients + fournisseurs réels)
□ Migration données historiques Ciel Compta → Odoo
□ Tests utilisateurs terrain (picking réel en entrepôt)
□ Configuration SMTP production (emails réels, pas demo)
```

**Moyen terme (3-6 mois)**
```text
□ Module qualité : retours produits, quarantaine, DLC expirées
□ Extension POS PARASHOP : synchronisation stock temps réel
□ Portail B2B pharmacies : commande en ligne sans WhatsApp
□ Module prévision : analyse historique ventes → réappro prédictif
□ Connexion transporteur : suivi livraison GPS temps réel
```

**Long terme (6-12 mois)**
```text
□ App mobile livreur native (React Native ou Flutter)
□ Scoring crédit client automatique (données historiques Odoo)
□ EDI fournisseurs : commandes automatiques sans email
□ Dashboard BI avancé : Metabase open source connecté à PostgreSQL
□ Signature eIDAS si requis légalement (prestataire qualifié)
```

---

### ROI Consolidé

| Indicateur | Avant MVP | Après MVP | Gain annuel |
|-----------|-----------|-----------|-------------|
| Litiges facturation | ~3 MDH/an | ~0,9 MDH/an | **+2,1 MDH** |
| DSO moyen | >90 jours | ~60 jours | **~3 MDH trésorerie** |
| Temps ADV ressaisie | ~2h/jour | ~0,2h/jour | **~250k DH/an** |
| Erreurs picking | ~15% | <3% | **Qualité service** |
| Ruptures stock | Fréquentes | Rares (réappro auto) | **CA préservé** |
| **Total gain Year 1** | | | **~5,35 MDH** |
| Coût projet (MVP) | | | **~0 DH (open source)** |
| **Payback** | | | **< 6 mois** |

---

### Message final pour le jury

> Ce projet ne prétend pas avoir tout déployé.  
> Il démontre qu'avec Odoo 17 Community open source,  
> une équipe peut construire une solution logistique et financière  
> crédible, traçable et non répudiable —  
> sans budget logiciel, sans licence Enterprise,  
> en partant du terrain réel PARABOX.
>
> Le MVP couvre les 80% des irritants qui génèrent  
> 80% des pertes financières (~3 MDH litiges + ~10 MDH encours).
>
> C'est suffisant pour prouver la valeur.  
> C'est suffisant pour convaincre la direction.  
> C'est suffisant pour déployer.

---

## Commande de conversion Word

Une fois le .md généré, convertir en Word :

```bash
# Installer pandoc si pas encore fait
winget install pandoc

# Convertir
pandoc CAP2026_Document_Explicatif.md   -o CAP2026_Document_Explicatif.docx   --reference-doc=template_parabox.docx   --toc   --toc-depth=2

# Sans template (basique mais fonctionnel)
pandoc CAP2026_Document_Explicatif.md   -o CAP2026_Document_Explicatif.docx
```

> Si pandoc non disponible : copier le Markdown dans Google Docs
> ou Word directement — la structure reste lisible.

---

## ✅ Checklist Phase 9

- [ ] Document 10 pages généré et complet
- [ ] Page 1 résumé exécutif avec chiffres clés
- [ ] Page 2 tableau AS-IS vs TO-BE complet
- [ ] Page 3 architecture justifiée (Community vs Enterprise)
- [ ] Page 4 fiches utilisateurs + matrice droits
- [ ] Pages 5-8 un module par page avec justifications
- [ ] Page 9 script démo + checklist pré-démo
- [ ] Page 10 limites honnêtes + roadmap + ROI consolidé
- [ ] Converti en .docx via pandoc
- [ ] Relu et défendable devant jury
- [ ] README.md dans /docs/

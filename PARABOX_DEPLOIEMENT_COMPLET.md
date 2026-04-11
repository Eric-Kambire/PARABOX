# PARABOX — Guide de deploiement complet et plan de test

## 1. RESUME DES CORRECTIONS APPLIQUEES

### 1.1 Corrections critiques Odoo 17

| Fichier | Probleme | Correction |
|---------|----------|------------|
| `parabox_logistics_tracking/models/parabox_logistics_line.py` | `attrs=` sur champ Python (supprime en Odoo 17, provoque crash) | Supprime. La visibilite est deja geree dans la vue XML |
| `parabox_logistics_tracking/models/stock_picking.py` | `action_done()` renomme en Odoo 17 | Change en `_action_done()` |
| `parabox_logistics_tracking/models/stock_picking.py` | `move.quantity_done` renomme en Odoo 17 | Change en `move.quantity` avec fallback |
| `parabox_logistics_tracking/data/automated_actions.xml` | Syntaxe Odoo 16 `action_server_ids` + `ir.actions.server` separes | Reecrit pour Odoo 17 : code directement sur `base.automation` |
| `parabox_product_alias/models/parabox_product_alias.py` | `name_get()` deprecie en Odoo 17 | Remplace par `_compute_display_name()` |
| `parabox_mobile/controllers/mobile_controller.py` | `move.quantity_done` dans le controleur | Utilise `move_line_ids.qty_done` avec fallback sur `move.quantity` |

### 1.2 Suppression emojis (TOUS les modules)

Tous les emojis ont ete remplaces par des icones Font Awesome 4 (`fa fa-*`) dans les templates HTML/XML, et par du texte simple dans les selections Python et les sujets email.

Modules concernes : `parabox_encaissement`, `parabox_litige`, `parabox_sign`, `parabox_credit_control`, `parabox_product_alias`, `parabox_dashboard`, `parabox_logistics_tracking`, `parabox_mobile`.

### 1.3 KeyError: 'parabox.logistics.line' — Analyse racine

**Cause** : Le fichier `automated_actions.xml` utilisait la syntaxe Odoo 16 (`action_server_ids` + enregistrements `ir.actions.server` separes). En Odoo 17, `base.automation` herite directement de `ir.actions.server`. Le XML invalide empechait l'installation complete du module, ce qui empechait le modele `parabox.logistics.line` d'etre enregistre dans le registry Odoo.

**Correction** : Reecriture complete de `automated_actions.xml` avec le code directement sur les enregistrements `base.automation`.

### 1.4 Erreur 500 mobile livreur (quantity_done)

**Cause** : Odoo 17 a renomme `stock.move.quantity_done` en `stock.move.quantity`.

**Correction** : Le controleur mobile utilise desormais `move_line_ids.qty_done` (qui existe toujours) avec fallback sur `move.quantity`.

---

## 2. MATRICE DE CONTROLE D'ACCES

| Menu / Module | Direction | Commercial | Magasinier | Comptable | Livreur |
|---------------|:---------:|:----------:|:----------:|:---------:|:-------:|
| Dashboard PARABOX | X | - | - | - | - |
| PARABOX Logistique (menu racine) | X | X | X | X | - |
| Tracabilite | X | X | X | - | - |
| Signatures BL | X | - | X | - | - |
| Litiges | X | X | - | X | - |
| Encaissements | X | - | - | X | - |
| Alias Produits | X | - | X | - | - |
| Interface mobile livreur | - | - | - | - | X (web) |

Le livreur accede uniquement via `/parabox/mobile/livreur` (compte utilisateur type "Portail" ou interne avec groupe Livreur).

---

## 3. ORDRE DE DEPLOIEMENT (copie manuelle)

### 3.1 Pre-requis

- Odoo 17 Community installe sur `C:\Program Files\Odoo 17.0.20260219\`
- Acces administrateur Windows pour copier dans `Program Files`
- Les modules dev sont dans OneDrive : `CAP2026_PARABOX_Markdowns\odoo_modules\`

### 3.2 Ordre de copie (RESPECTER l'ordre)

Les modules ont des dependances. Copier et installer/upgrader dans cet ordre :

**Etape 1 — Module de base (aucune dependance PARABOX)**

```
parabox_logistics_tracking  →  C:\Program Files\Odoo 17.0.20260219\server\addons\parabox_logistics_tracking
```

**Etape 2 — Modules dependant de parabox_logistics_tracking**

```
parabox_credit_control      →  ...\addons\parabox_credit_control
parabox_product_alias       →  ...\addons\parabox_product_alias
parabox_sign                →  ...\addons\parabox_sign
parabox_litige              →  ...\addons\parabox_litige
parabox_encaissement        →  ...\addons\parabox_encaissement
```

**Etape 3 — Modules dependant de modules Etape 2**

```
parabox_mobile              →  ...\addons\parabox_mobile       (depend de parabox_sign)
parabox_dashboard           →  ...\addons\parabox_dashboard    (depend de parabox_litige)
```

### 3.3 Procedure de copie

Pour chaque module :

1. Ouvrir l'Explorateur Windows en tant qu'administrateur
2. Naviguer vers `C:\Program Files\Odoo 17.0.20260219\server\addons\`
3. Si le dossier du module existe deja : le supprimer entierement
4. Copier le dossier complet depuis OneDrive vers addons
5. Verifier que le dossier contient bien `__manifest__.py` a la racine

### 3.4 Procedure d'upgrade dans Odoo

Apres la copie de TOUS les modules :

1. Ouvrir Odoo dans le navigateur (http://localhost:8069)
2. Aller dans : **Parametres** > **Applications**
3. Cliquer le filtre "Applications" en haut et le remplacer par rien (voir toutes)
4. Chercher "PARABOX" dans la barre de recherche
5. Pour chaque module PARABOX, dans l'ordre ci-dessus :
   - Si le module est **deja installe** : cliquer les 3 points > **Mettre a jour**
   - Si le module est **pas encore installe** : cliquer **Installer**
6. Attendre que chaque upgrade se termine avant de passer au suivant
7. Redemarrer le service Odoo apres tous les upgrades :
   - `services.msc` > trouver "Odoo" > Redemarrer

### 3.5 Verification odoo.conf

Fichier : `C:\Program Files\Odoo 17.0.20260219\server\odoo.conf`

Verifier que `addons_path` contient bien le chemin des addons :

```
addons_path = C:\Program Files\Odoo 17.0.20260219\server\odoo\addons,C:\Program Files\Odoo 17.0.20260219\server\addons
```

NE PAS mettre le chemin OneDrive dans `addons_path` (cause des erreurs 500).

SMTP Gmail (deja configure) :

```
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_ssl = False
smtp_user = ernestlompo28@gmail.com
smtp_password = oafmxmjlvlwznhbb
```

---

## 4. ARCHITECTURE DES 8 MODULES

```
parabox_logistics_tracking   (BASE — groupes securite, tracabilite, automations)
    |
    +-- parabox_credit_control    (controle credit client sur sale.order)
    +-- parabox_product_alias     (table correspondance codes produit)
    +-- parabox_sign              (OTP + signature BIC + PDF SHA-256)
    |       |
    |       +-- parabox_mobile    (interface livreur mobile)
    |
    +-- parabox_litige            (kanban litiges avec SLA)
    +-- parabox_encaissement      (plan encaissement factures)
            |
            +-- parabox_dashboard (dashboard direction OWL + Chart.js)
```

---

## 5. PLAN DE TEST COMPLET

### 5.1 Tests de deploiement

| # | Test | Resultat attendu |
|---|------|------------------|
| D1 | Copier parabox_logistics_tracking et installer | Module installe sans erreur |
| D2 | Verifier que le modele `parabox.logistics.line` existe | Aller dans Parametres > Technique > Modeles > chercher "parabox.logistics.line" |
| D3 | Installer les 7 autres modules dans l'ordre | Aucun KeyError, aucune erreur XML |
| D4 | Redemarrer Odoo et verifier la page d'accueil | Pas de 500 |

### 5.2 Tests backend — Tracabilite

| # | Test | Resultat attendu |
|---|------|------------------|
| B1 | Creer une commande client et la confirmer | Message chatter "Commande confirmee - A preparer" |
| B2 | Creer un BL sortant, ajouter des produits, valider | Lignes tracabilite auto-creees dans l'onglet "Tracabilite PARABOX" |
| B3 | Verifier les ecarts calcules | ecart_total = qty_ordered - qty_delivered |
| B4 | Cocher "Substitution" sur une ligne | Champ "Produit substitue" devient visible |

### 5.3 Tests backend — Credit control

| # | Test | Resultat attendu |
|---|------|------------------|
| C1 | Definir limite credit 5000 DH sur un client | Champ visible dans onglet "Credit PARABOX" |
| C2 | Creer une commande > 5000 DH et confirmer | Blocage avec message "Depassement limite de credit" |
| C3 | Cliquer "Accorder derogation" (utilisateur ADV) | Commande confirmee, champs derogation remplis |
| C4 | Cocher "Compte bloque" sur le client et confirmer une commande | Blocage "Compte client bloque" |

### 5.4 Tests backend — Litiges

| # | Test | Resultat attendu |
|---|------|------------------|
| L1 | Creer un litige, verifier kanban | 5 colonnes : Ouvert, En analyse, Attente client, Resolu, Clos |
| L2 | Laisser un litige ouvert >3 jours (ou modifier date_ouverture) | SLA passe a "Alerte (>3j)" |
| L3 | Litige >7 jours | SLA passe a "Escalade (>7j)", alerte bandeau rouge |

### 5.5 Tests backend — Encaissement

| # | Test | Resultat attendu |
|---|------|------------------|
| E1 | Depuis une facture validee, cliquer bouton "Encaissements" | Ouvre le plan d'encaissement |
| E2 | Ajouter des lignes de paiement (cash, cheque) | Montant recu se calcule, statut passe a "partiel" |
| E3 | Solder entierement | Statut passe a "solde" |

### 5.6 Tests backend — Alias produit

| # | Test | Resultat attendu |
|---|------|------------------|
| A1 | Ouvrir une fiche produit, onglet "Alias PARABOX" | Tableau editable avec codes |
| A2 | Ajouter un alias avec EAN invalide (ex: 12345) | Erreur validation "EAN doit faire 8 ou 13 caracteres" |

### 5.7 Tests backend — Signature

| # | Test | Resultat attendu |
|---|------|------------------|
| S1 | Depuis un BL sortant, cliquer "Signer BL" | Cree une demande de signature, formulaire s'ouvre |
| S2 | Cliquer "Envoyer OTP" | Email envoye au client avec code 6 chiffres |
| S3 | Acceder a l'URL `/parabox/sign/<token>` | Page publique de signature (pas besoin de login) |
| S4 | Entrer l'OTP et signer | Statut passe a "Signe", PDF genere avec hash SHA-256 |
| S5 | Cliquer "Verifier integrite PDF" | Notification "Integrite verifiee" |

### 5.8 Tests portail mobile

| # | Test | Resultat attendu |
|---|------|------------------|
| M1 | Se connecter et aller sur `/parabox/mobile/livreur` | Liste des BL en cours avec KPIs |
| M2 | Cliquer sur un BL | Detail avec produits, quantites, section signature |
| M3 | Cliquer "Envoyer le code OTP au client" | Message succes, URL de signature affichee |
| M4 | Annuler un BL dans Odoo pendant que la page detail est ouverte | Banniere "Ce BL vient d'etre annule" (polling 15s) |
| M5 | Tester sur mobile (Chrome/Safari) | Interface responsive, pas de scroll horizontal |

### 5.9 Tests dashboard

| # | Test | Resultat attendu |
|---|------|------------------|
| DH1 | Se connecter en tant que Direction | Menu "Dashboard PARABOX" visible |
| DH2 | Ouvrir le dashboard | 10 KPIs affiches, 4 graphiques Chart.js |
| DH3 | Verifier le scroll | Page scrollable verticalement (pas bloquee) |
| DH4 | Reduire la fenetre / zoom 150% | Grille KPIs fluide, textes adaptables |
| DH5 | Attendre 60 secondes | Donnees se rafraichissent automatiquement |

### 5.10 Tests securite / roles

| # | Test | Resultat attendu |
|---|------|------------------|
| R1 | Se connecter en tant que Direction | Voit TOUT : dashboard, tracabilite, litiges, encaissements, alias, signatures |
| R2 | Se connecter en tant que Commercial | Voit : tracabilite, litiges. NE VOIT PAS : dashboard, encaissements, alias, signatures |
| R3 | Se connecter en tant que Magasinier | Voit : tracabilite, signatures, alias. NE VOIT PAS : dashboard, litiges, encaissements |
| R4 | Se connecter en tant que Comptable | Voit : litiges, encaissements. NE VOIT PAS : dashboard, tracabilite, signatures, alias |
| R5 | Se connecter en tant que Livreur | NE VOIT PAS le menu PARABOX backend. Accede via `/parabox/mobile/livreur` |

### 5.11 Tests de regression

| # | Test | Resultat attendu |
|---|------|------------------|
| RG1 | Aller sur http://localhost:8069 | Pas de 500 |
| RG2 | Ouvrir Ventes > Commandes | Fonctionne normalement |
| RG3 | Ouvrir Inventaire > Bons de livraison | Fonctionne normalement |
| RG4 | Ouvrir Facturation > Factures clients | Fonctionne normalement |
| RG5 | Aller sur `/parabox/mobile/livreur` | Pas de 500, page s'affiche |
| RG6 | Aller sur `/parabox/mobile/livreur/bl/1` (BL existant) | Pas de 500, detail s'affiche |

---

## 6. FLUX METIER DOCUMENTES

### 6.1 Flux Commande → Livraison → Signature

1. Commercial cree une commande (sale.order)
2. Confirmation → verification credit → si OK, passe en "Bon de commande"
3. Automation : notification au magasinier via chatter
4. Magasinier prepare le BL (stock.picking outgoing)
5. Lignes de tracabilite auto-creees a la validation du BL
6. Livreur voit le BL sur son interface mobile `/parabox/mobile/livreur`
7. Livreur envoie l'OTP au client depuis l'interface mobile
8. Client recoit l'email avec code OTP + lien de signature
9. Client entre l'OTP et signe avec le doigt sur la page publique
10. PDF signe genere avec hash SHA-256, email confirmation envoye

### 6.2 Flux Litige

1. Un ecart est detecte (quantite, produit abime, etc.)
2. Creation d'un litige dans le kanban (lie au BL/BC/facture)
3. Progression : Ouvert → En analyse → Attente client → Resolu → Clos
4. SLA automatique : alerte a 3 jours, escalade direction a 7 jours
5. Possibilite d'emettre un avoir si necessaire

### 6.3 Flux Encaissement

1. Facture client validee dans Odoo
2. Creation du plan d'encaissement (depuis le bouton sur la facture)
3. Ajout des lignes de paiement : cash, cheque, traite, virement
4. Suivi : En attente → Partiel → Solde
5. Gestion des rejets (cheque rejete, traite impayee)

### 6.4 Flux Credit Control

1. Direction definit la limite credit par client (onglet Credit PARABOX)
2. A la confirmation d'une commande : verification automatique
3. Si encours + commande > limite → blocage + demande derogation
4. ADV recoit une activite + email
5. ADV accorde ou refuse la derogation

---

## 7. FICHIERS MODIFIES DANS CETTE SESSION

| Module | Fichier | Type de modification |
|--------|---------|---------------------|
| parabox_logistics_tracking | models/parabox_logistics_line.py | Supprime `attrs=` (crash Odoo 17) |
| parabox_logistics_tracking | models/stock_picking.py | `action_done` → `_action_done` + fix quantity |
| parabox_logistics_tracking | data/automated_actions.xml | Reecrit pour Odoo 17 base.automation |
| parabox_logistics_tracking | views/stock_picking_views.xml | Supprime emoji |
| parabox_product_alias | models/parabox_product_alias.py | `name_get` → `_compute_display_name` |
| parabox_product_alias | views/product_template_views.xml | Supprime emoji |
| parabox_encaissement | models/parabox_encaissement.py | Supprime emojis des selections |
| parabox_litige | models/parabox_litige.py | Supprime emojis des selections |
| parabox_sign | models/sign_request.py | Supprime emojis selections + notifications |
| parabox_sign | models/sign_log.py | Supprime emojis des selections |
| parabox_sign | views/sign_portal_templates.xml | Emojis → FA4 icons |
| parabox_sign | views/sign_request_views.xml | Deja propre (corrige session precedente) |
| parabox_credit_control | data/mail_template.xml | Supprime emojis sujet/corps |
| parabox_credit_control | views/sale_order_views.xml | Supprime emojis boutons/alertes |
| parabox_credit_control | views/res_partner_views.xml | Supprime emoji alerte |
| parabox_dashboard | views/dashboard_views.xml | Supprime emoji nom menu |
| parabox_mobile | views/mobile_templates.xml | Deja propre (corrige session precedente) |
| parabox_mobile | controllers/mobile_controller.py | Deja propre (corrige session precedente) |

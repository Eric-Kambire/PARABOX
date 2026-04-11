# PARABOX — Script de Démo Complet
## CAP2026 | Odoo 17 Community
### Durée totale estimée : 35–40 minutes | Public : Direction + Jury

---

## ⚡ Préparation avant démo (10 min avant)

```text
□ Démarrer Odoo (Services Windows → Odoo Server → Démarrer)
□ Tester http://localhost:8069 → écran login OK
□ Lancer ngrok : ngrok http 8069 (dans CMD)
□ Copier l'URL https://xxxx.ngrok.io
□ Odoo → Settings > Technical > System Parameters → web.base.url = URL ngrok
□ Tester chaque compte utilisateur (tableau ci-dessous)
□ Ouvrir sur smartphone : https://xxxx.ngrok.io/parabox/mobile/livreur
□ Préparer une commande "brouillon" pour le scénario 1
```

### Comptes utilisateurs

| Utilisateur | Login | Rôle | Ce qu'il voit |
|-------------|-------|------|---------------|
| Karim Haddad | karimhaddad@parabox.ma | Direction | Dashboard + tout PARABOX |
| Yassine Benali | yassine@parabox.ma | Commercial | Ventes, Litiges, Traçabilité |
| Omar Idrissi | omar@parabox.ma | Magasinier | Stock, BL, Signatures, Alias |
| Amina Cherkaoui | amina@parabox.ma | Comptable | Facturation, Encaissements, Litiges |
| Karim Alami | karim.alami@parabox.ma | Livreur | Interface mobile uniquement |

---

## 🎬 SCÉNARIO 1 — Flux de vente complet (10 min)
### "De la commande à la livraison signée"

**Acteurs** : Yassine (Commercial) + Omar (Magasinier) + Karim Alami (Livreur sur smartphone)
**Client** : PARFUMERIE ATLAS | **Produits** : P001 × 10 + P009 × 5

---

**[Étape 1 — Connexion et contrôle d'accès]**
> Se connecter comme Yassine (Commercial)
- Montrer le menu : uniquement Ventes + PARABOX Logistique restreint
- Dire : *"Chaque utilisateur voit uniquement ce dont il a besoin — pas de confusion possible"*

**[Étape 2 — Créer la commande client]**
> Sales > Orders > New
- Client : PARFUMERIE ATLAS
- Ligne 1 : P001 × 10 | Ligne 2 : P009 × 5
- Cliquer **Confirmer**
- **Attendre 3 secondes** → cloche Odoo (🔔 en haut à droite) → Omar reçoit notification inbox "📦 Nouvelle commande à préparer"
- Dire : *"Notification automatique au magasinier — IN-APP, aucun email parasite"*

**[Étape 3 — Magasinier prépare le BL]**
> Ouvrir onglet privé → connexion Omar (Magasinier)
- Cliquer la cloche → voir la notification avec détails commande
- Inventory > Operations > Transfers → trouver le BL PARFUMERIE ATLAS
- Cliquer **"Vérifier disponibilité"** → état passe à "Prêt à livrer" (badge bleu)
- Dire : *"Le stock est réservé. Le livreur peut partir."*

**[Étape 4 — Interface mobile livreur]**
> Prendre le smartphone — ouvrir l'URL ngrok
- Connexion Karim Alami
- Montrer la page d'accueil : KPI strip (BL en cours / Livrés / Signés)
- Cliquer sur le BL PARFUMERIE ATLAS → page de détail
- Lire les produits commandés + quantités
- Cliquer **"📧 Envoyer OTP"** → animation spinner → "OTP envoyé à client@email.com"

**[Étape 5 — Signature du client]**
- Cliquer l'URL de signature générée automatiquement
- Entrer le code OTP reçu par email (ou montrer l'email reçu)
- Dessiner la signature sur le canvas (doigt sur l'écran)
- Valider → "✅ Signature enregistrée"

**[Étape 6 — Validation finale]**
> Retour sur la page BL dans l'interface mobile
- Cliquer **"✓ Valider la livraison"**
- BL passe en "Livré" (badge vert)
- Cloche Odoo → Yassine + Karim Haddad reçoivent "✅ BL validé"

**[Résultat visible]**
> Connexion Direction (Karim Haddad) → Dashboard
- OTIF mis à jour, Fill Rate, "BL en cours" diminue
- Dire : *"Le flux complet — commande → livraison → signature — en moins de 2 minutes"*

---

## 🎬 SCÉNARIO 2 — Livraison partielle + Backorder (5 min)
### "Facturation sur le livré réel, jamais sur l'estimé"

**Acteur** : Omar (Magasinier)
**Client** : PARASHOP | P002 × 20 | Stock dispo : 12 seulement

---

1. Créer une commande PARASHOP : P002 × 20 → confirmer
2. Omar > Inventory > Transfers → ouvrir le BL (20 unités)
3. "Vérifier disponibilité" → seules 12 sont en stock
4. Modifier la quantité "Fait" à **12** (pas 20)
5. Valider → Odoo demande : "Créer un backorder ?" → **Oui**
6. BL1 = 12 livrés (✅ done) | BL2 = 8 restants (⏳ nouveau BL)
7. Sales > Orders > PARASHOP → Créer facture → **"Sur livré"** → 12 unités, pas 20
8. Dire : *"PARABOX ne facture jamais ce qui n'est pas livré"*
9. Dashboard → "Reliquats ouverts" = 1 (visible immédiatement)

---

## 🎬 SCÉNARIO 3 — Blocage crédit automatique (4 min)
### "Le système protège les finances de PARABOX"

**Acteur** : Yassine (Commercial)
**Client** : PARA TALBORJT | Limite : 3 000 DH | Encours : 2 800 DH

---

1. Connexion Yassine → nouvelle commande PARA TALBORJT
2. Ajouter produit P003 × 3 (~900 DH total)
3. Tenter de confirmer → **blocage automatique** (message d'alerte rouge)
4. Dire : *"La limite de crédit est dépassée — le système bloque sans intervention humaine"*
5. Montrer : PARABOX Logistique > module Credit Control → fiche PARA TALBORJT
6. Encours actuel, historique paiements, limite configurée
7. Dire : *"Un responsable peut accorder une dérogation manuelle si le client est fiable"*

---

## 🎬 SCÉNARIO 4 — Dashboard Direction (5 min)
### "La Direction voit tout, en temps réel"

**Acteur** : Karim Haddad (Direction)

---

1. Connexion Direction → cliquer "📊 Dashboard PARABOX" dans le menu
2. Montrer le **header** : logo, horloge en temps réel (secondes), "Mis à jour : HH:MM:SS"
3. **Bandeau alertes** (bande noire sous le header) :
   - Si alertes : lire les messages rouges/orange un par un
   - Si aucune alerte : "✅ Tous les indicateurs sont dans les normes"
4. Section **Finance** (5 cartes) :
   - CA Mois : valeur + flèche d'évolution (▲ vert ou ▼ rouge)
   - Encours clients : montant + nombre de factures
   - DSO : valeur en jours (rouge si > 45j)
   - Litiges : montant total
   - **Cliquer "Factures en retard ↗"** → naviguer vers liste Odoo filtrée
5. Section **Logistique** (5 cartes) :
   - OTIF : barre de progression (verte si ≥ 95%)
   - Fill Rate : barre de progression
   - **Cliquer "BL en cours ↗"** → liste des BL ouverts
   - Ruptures stock (rouge si > 0)
6. Section **Graphiques** :
   - CA mensuel 6 mois (barres)
   - Litiges par type (donut)
   - Top 5 encours clients (barres horizontales)
   - Statuts BL 30 jours (donut couleurs)
7. Dire : *"Refresh automatique toutes les 60 secondes — aucune intervention manuelle"*

---

## 🎬 SCÉNARIO 5 — Réapprovisionnement automatique (3 min)
### "Zéro rupture grâce aux règles min/max"

**Acteur** : Omar (Magasinier)

---

1. Dashboard → "Ruptures stock" → cliquer pour voir les produits
2. Omar > Inventory > Configuration > Reordering Rules (min/max)
3. Montrer les règles configurées : seuil min, seuil max, fournisseur
4. Inventory > Operations > Replenishment → produits sous le seuil
5. Cliquer **"Réapprovisionner"** → bon de commande fournisseur créé automatiquement
6. Purchase > Orders > voir le bon créé
7. Simuler réception : valider + saisir numéros de lots
8. Stock mis à jour → rupture disparaît → Dashboard se met à jour

---

## 🎬 SCÉNARIO 6 — Gestion litiges (3 min)
### "Chaque incident est tracé et résolu"

**Acteur** : Yassine (Commercial)

---

1. PARABOX Logistique > Litiges > Nouveau
2. Remplir : client, type (produit endommagé / manquant / retard), montant, description
3. Assigner au responsable
4. Montrer le **Kanban** des litiges : colonnes par stage
5. Dashboard Direction → "Litiges ouverts" +1 (mis à jour)
6. Résoudre le litige : glisser vers "Résolu"
7. Dashboard → montant litiges diminue

---

## 🎬 SCÉNARIO 7 — Traçabilité + Audit (3 min)
### "Chaque livraison est prouvable juridiquement"

**Acteur** : Karim Haddad (Direction)

---

1. PARABOX Logistique > Traçabilité
2. Filtrer par client : PARFUMERIE ATLAS → voir historique complet
3. PARABOX Logistique > Signatures BL
4. Ouvrir la signature du scénario 1 :
   - Hash SHA-256 du PDF affiché
   - Date/heure, IP du signataire, coordonnées GPS
   - Mode : "🔒 OTP + Signature"
5. Cliquer **"Vérifier intégrité du PDF"**
6. Message : "✅ Document non modifié. Hash vérifié."
7. Dire : *"En cas de litige juridique, la preuve est irréfutable et horodatée"*

---

## 🧯 Gestion des imprévus

| Problème | Solution rapide |
|----------|-----------------|
| Odoo ne démarre pas | Services Windows → Redémarrer "Odoo Server" |
| Écran blanc / 500 | Redémarrer Odoo, vérifier les logs : `C:\Program Files\Odoo 17.0.20260219\server\odoo.log` |
| ngrok expire | Relancer `ngrok http 8069`, mettre à jour `web.base.url` |
| Email OTP non reçu | Vérifier spam client, ou passer en mode dégradé (signature sans OTP) |
| Dashboard ne charge pas | Vérifier que le module est à jour, recharger la page |
| Notifications pas reçues | Vérifier groupes PARABOX assignés aux utilisateurs concernés |
| Stock insuffisant | Inventory > Products → ajuster quantité manuellement |

---

## 📋 Messages clés à retenir (pour le jury)

1. **Zéro développement externe** — tout Odoo Community + modules Python open source
2. **Contrôle d'accès par rôle** — chaque employé voit uniquement son périmètre
3. **Notifications intelligentes** — IN-APP uniquement, pas d'emails parasites
4. **Signature juridiquement valide** — OTP + canvas BIC + GPS + hash SHA-256
5. **Dashboard temps réel** — 10 KPIs, 4 graphiques, alertes automatiques, refresh 60s
6. **Interface mobile** — aucune app à installer, fonctionne sur tout smartphone
7. **Budget : zéro** — 100% open source, hébergement local

---

## 📋 Checklist post-démo

```text
□ Supprimer les commandes de test (ou laisser pour référence)
□ Réinitialiser les stocks si nécessaire
□ Arrêter ngrok
□ web.base.url → remettre http://localhost:8069
```

---

*Script PARABOX CAP2026 — Version 2.0 | Révisé avec tous les workflows*

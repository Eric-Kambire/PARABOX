# Installation des modules Phase 4

## Étape 1 — Copier les modules dans le dossier addons Odoo

```bash
# Sur Windows, copier les 5 dossiers depuis :
# CAP2026_PARABOX_Markdowns/odoo_modules/
# vers le dossier addons de votre installation Odoo 17 Community
# ex: C:\Program Files\Odoo 17\server\odoo\addons\

# Modules à copier :
# - parabox_credit_control
# - parabox_logistics_tracking
# - parabox_litige
# - parabox_encaissement
# - parabox_product_alias
```

## Étape 2 — Activer le mode développeur

```
http://localhost:8069/web?debug=1#action=base_setup.action_general_configuration
```
Ou : Paramètres > Activer le mode développeur

## Étape 3 — Mettre à jour la liste des modules

Paramètres > Modules > Mettre à jour la liste des modules

## Étape 4 — Installer dans l'ordre

```
1. parabox_logistics_tracking  (base — crée le menu PARABOX Logistique)
2. parabox_credit_control
3. parabox_litige               (dépend du menu créé par logistics_tracking)
4. parabox_encaissement
5. parabox_product_alias
```

## Étape 5 — Vérification post-installation

```
✅ Menu "PARABOX Logistique" visible dans Odoo
✅ Onglet "Crédit PARABOX" sur la fiche client
✅ Onglet "📦 Traçabilité PARABOX" sur les BL sortants
✅ Kanban "Litiges" accessible
✅ "Plans d'encaissement" dans PARABOX Logistique
✅ "Alias Produits" dans PARABOX Logistique
✅ Onglet "🔗 Alias PARABOX" sur la fiche produit
```

## Note important sur parabox_litige

Le module `parabox_litige` hérite du menu parent de `parabox_logistics_tracking`.
Il faut donc installer `parabox_logistics_tracking` **en premier**.

## Problème connu : encaissement_count sur account.move

Si l'installation de `parabox_encaissement` échoue à cause du bouton stat
sur `account.move`, commenter temporairement le fichier
`views/account_move_views.xml` dans le manifest jusqu'à résolution.

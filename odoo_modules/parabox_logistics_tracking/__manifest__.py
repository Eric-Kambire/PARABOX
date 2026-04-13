{
    'name': 'PARABOX - Traçabilité Logistique',
    'version': '17.0.2.0.0',
    'summary': 'Trace Commandé → Préparé → Chargé → Livré réel + timestamps T1/T2/T3 + scanner obligatoire',
    'description': """
        Module de traçabilité logistique PARABOX :
        - 4 états : Commandé / Préparé / Chargé / Livré réel
        - Calcul automatique des écarts BC vs BL
        - Gestion des substitutions produit
        - Lien avec stock.picking
        - Timestamps T1/T2/T3 (préparation / prise en charge / livraison OTP)
        - Durées calculées : délai prise en charge + durée livraison réelle
        - Scanner produit obligatoire avant confirmation livreur
        - Cron alerte : commande non récupérée après 2h
    """,
    'author': 'PARABOX',
    'category': 'Inventory/Inventory',
    'depends': ['stock', 'sale_management', 'base_automation'],
    'data': [
        'security/groups.xml',           # 1. Groupes en premier (crée les res.groups)
        'security/ir.model.access.csv',  # 2. ACL (référence les groupes et le modèle)
        'data/automated_actions.xml',    # 3. Automatisations métier
        'data/cron.xml',                 # 4. Tâche planifiée alerte T2 (noupdate=1)
        'views/parabox_logistics_line_views.xml',  # 5. Vues + actions (sans menuitem)
        'views/stock_picking_views.xml',           # 6. Vue BL avec onglet traçabilité
        'views/menus.xml',               # 7. Menus EN DERNIER — groupes garantis existants
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'PARABOX - Traçabilité Logistique',
    'version': '17.0.1.0.0',
    'summary': 'Trace Commandé → Préparé → Chargé → Livré réel + écarts',
    'description': """
        Module de traçabilité logistique PARABOX :
        - 4 états : Commandé / Préparé / Chargé / Livré réel
        - Calcul automatique des écarts BC vs BL
        - Gestion des substitutions produit
        - Lien avec stock.picking
    """,
    'author': 'PARABOX',
    'category': 'Inventory/Inventory',
    'depends': ['stock', 'sale_management', 'base_automation'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/automated_actions.xml',
        'views/parabox_logistics_line_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

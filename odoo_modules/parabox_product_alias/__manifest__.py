{
    'name': 'PARABOX - Alias Produit',
    'version': '17.0.1.0.0',
    'summary': 'Table de correspondance codes PARABOX / fournisseur / revendeur / EAN',
    'description': """
        Module de correspondance des codes produits PARABOX :
        - Code PARABOX interne
        - Code fournisseur (pour rapprochement BL fournisseur)
        - Code revendeur (pour rapprochement commandes clients)
        - Code-barres EAN
        - Lien vers le fournisseur concerné
    """,
    'author': 'PARABOX',
    'category': 'Inventory/Inventory',
    'depends': ['product', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/parabox_product_alias_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

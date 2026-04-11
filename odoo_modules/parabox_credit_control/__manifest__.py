{
    'name': 'PARABOX - Contrôle Crédit Client',
    'version': '17.0.1.0.0',
    'summary': 'Blocage commande si dépassement limite crédit + dérogation ADV',
    'description': """
        Module de contrôle crédit PARABOX :
        - Limite de crédit par client (champ sur res.partner)
        - Blocage automatique de la confirmation si encours > limite
        - Workflow de dérogation par l'ADV
        - Log des dérogations accordées
        - Notification email automatique
    """,
    'author': 'PARABOX',
    'category': 'Sales/Sales',
    'depends': ['sale_management', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

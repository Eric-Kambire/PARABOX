{
    'name': 'PARABOX - Gestion des Litiges',
    'version': '17.0.1.0.0',
    'summary': 'Kanban des litiges BC/BL/Facture avec SLA et escalade',
    'description': """
        Module de gestion des litiges PARABOX :
        - Kanban : Ouvert → En analyse → En attente client → Résolu → Clos
        - SLA : alerte rouge > 3 jours, escalade direction > 7 jours
        - Lien avec commande / BL / facture / avoir
        - Suivi responsable + historique
    """,
    'author': 'PARABOX',
    'category': 'Sales/Sales',
    'depends': ['sale_management', 'stock', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/litige_stage_data.xml',
        'views/parabox_litige_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'PARABOX - Plan d\'Encaissement',
    'version': '17.0.1.0.0',
    'summary': 'Plan de paiement multi-modes sur factures (cash/chèque/traite/virement)',
    'description': """
        Module de gestion des encaissements PARABOX :
        - Plan d'encaissement par facture
        - Paiements multiples : cash, chèque, traite, virement
        - Suivi statut : En attente / Partiel / Soldé
        - Calcul automatique solde restant
        - Gestion des rejets (chèque rejeté, traite impayée)
    """,
    'author': 'PARABOX',
    'category': 'Accounting/Accounting',
    'depends': ['account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/parabox_encaissement_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

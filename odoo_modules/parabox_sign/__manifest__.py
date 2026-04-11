{
    'name': 'PARABOX - Signature BL Sécurisée',
    'version': '17.0.1.0.0',
    'summary': 'OTP email + signature BIC terrain + hash SHA-256 PDF — zéro litige livraison',
    'description': """
        Module de signature sécurisée PARABOX (Projet MATCH) :

        AVANT livraison :
          - OTP 6 chiffres envoyé par email au client
          - OTP hashé (SHA-256) en base, valable 30 min

        PENDANT livraison :
          - Page web responsive sur téléphone livreur
          - Client entre OTP + signe avec le doigt (canvas BIC)
          - Capture IP, user-agent, timestamp, GPS (optionnel)

        APRÈS signature :
          - PDF BL généré avec signature incrustée (reportlab)
          - Hash SHA-256 du PDF stocké → détection fraude
          - Email confirmation au client avec PDF signé en PJ

        MODE DÉGRADÉ :
          - Signature sans OTP possible (marquée "Non OTP")
          - Workflow continue, alerte ADV automatique
    """,
    'author': 'PARABOX',
    'category': 'Inventory/Inventory',
    'depends': ['stock', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/email_templates.xml',
        'views/sign_request_views.xml',
        'views/sign_portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'parabox_sign/static/src/css/sign_style.css',
            'parabox_sign/static/src/js/signature_pad.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['reportlab'],
    },
}

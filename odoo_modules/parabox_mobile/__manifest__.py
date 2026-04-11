{
    'name': 'PARABOX - Interfaces Web Mobile',
    'version': '17.0.1.0.0',
    'summary': 'Espace livreur mobile + page signature client — accessibles via ngrok',
    'description': """
        Interfaces web mobile PARABOX (Phase 10 — Projet MATCH) :

        Interface 1 — Espace Livreur
          URL : /parabox/mobile/livreur
          Login : livreur@parabox.ma
          - Voir ses BL du jour (assigned/ready)
          - Détail des produits à livrer
          - Envoyer OTP au client depuis le terrain
          - Valider la livraison

        Interface 2 — Page Signature Client
          URL : /parabox/sign/<token>
          - Public (pas de compte Odoo requis)
          - OTP + canvas BIC + GPS
          - Déjà fourni par parabox_sign

        Technologie : HTML/CSS/JS mobile-first, fetch() vers Odoo RPC.
        Fonctionne sur tout téléphone Chrome/Safari via ngrok.
    """,
    'author': 'PARABOX',
    'category': 'Inventory/Inventory',
    'depends': ['stock', 'parabox_sign'],
    'data': [
        'security/ir.model.access.csv',
        'views/mobile_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'PARABOX - Dashboard Direction',
    'version': '17.0.2.0.0',
    'summary': '10 KPIs Finance + Logistique — Dashboard temps réel pour la Direction',
    'description': """
        Dashboard de pilotage PARABOX pour la Direction (accès restreint).

        Finance :
          - CA du mois en cours vs mois précédent
          - Encours clients total
          - DSO (Days Sales Outstanding)
          - Montant litiges ouverts
          - Factures en retard (cliquable → liste)

        Logistique :
          - OTIF (On Time In Full) avec barre de progression
          - Fill Rate avec barre de progression
          - Produits en rupture
          - BL en cours (cliquable → liste)
          - Reliquats ouverts

        Graphiques :
          - CA mensuel (6 mois, barres)
          - Litiges par type (donut)
          - Top 5 encours clients (barres horizontales)
          - Statuts BL 30 jours (donut)

        Design v2 : gradient header, alertes bandeau, progress bars,
        cartes interactives, Chart.js 4, refresh 60s, horloge OWL.
    """,
    'author': 'PARABOX',
    'category': 'Reporting',
    'depends': ['sale_management', 'stock', 'account', 'parabox_litige'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'parabox_dashboard/static/src/xml/dashboard.xml',
            'parabox_dashboard/static/src/css/dashboard.css',
            'parabox_dashboard/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

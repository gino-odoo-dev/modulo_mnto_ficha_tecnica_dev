{
    'name': 'Ficha Tecnica (Receta)',
    'version': '1.0',
    'summary': 'Ingreso y Copia Ficha Tecnica',
    'description': 'Modulo de Ingreso y Copia de Ficha Tecnica.',
    'author': 'Mag',
    'depends': ['base', 'mrp', 'product'],
    'data': [
        'views/receta_model_views.xml',
        'views/copia_ficha_tecnica_wizard_view.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'receta/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

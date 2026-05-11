{
    'name': 'Custom Calculations — الحسابات المالية',
    'version': '17.0.1.0.0',
    'summary': 'نظام حسابات مالية متكامل',
    'author': 'Ahmed Bebars',
    'category': 'Accounting',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/calculation_views.xml',
        'views/calculation_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

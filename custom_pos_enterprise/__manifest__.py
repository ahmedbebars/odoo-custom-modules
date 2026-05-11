{
    'name': 'Custom POS Enterprise',
    'version': '17.0.1.0.0',
    'summary': 'خصائص POS متقدمة: Split Bill, Loyalty, Floor Plan, Kitchen Display',
    'author': 'Ahmed Bebars',
    'category': 'Point of Sale',
    'depends': ['base', 'mail', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
        'views/pos_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

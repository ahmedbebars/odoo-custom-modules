{
    'name': 'Custom Inventory',
    'version': '17.0.1.0.0',
    'summary': 'إدارة المخزون المخصصة - تتبع المنتجات والكميات',
    'description': '''
        مديول إدارة المخزون:
        - إضافة وتتبع المنتجات
        - إدارة الكميات والمستودعات
        - تنبيهات نقص المخزون
        - سجل حركات المخزون (وارد/صادر)
        - تقارير المخزون
    ''',
    'author': 'Ahmed Bebars',
    'category': 'Inventory',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/movement_views.xml',
        'views/inventory_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

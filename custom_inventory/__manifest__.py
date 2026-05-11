{
    'name': 'Custom Inventory — إدارة المخزون',
    'version': '17.0.1.0.0',
    'summary': 'نظام إدارة مخزون متكامل مع التنبيهات والتقارير',
    'author': 'Ahmed Bebars',
    'category': 'Inventory',
    'depends': ['base', 'mail', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_product_views.xml',
        'views/inventory_movement_views.xml',
        'views/inventory_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

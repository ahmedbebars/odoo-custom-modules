{
    'name': 'Custom Planning — جدولة المناوبات',
    'version': '17.0.1.0.0',
    'summary': 'نظام جدولة الشيفتات والموارد البشرية مع كل خصائص Enterprise',
    'description': '''
        مديول Planning شامل يضيف:
        ✅ جدولة الشيفتات (Gantt View)
        ✅ قوالب الشيفتات
        ✅ شيفتات متكررة
        ✅ شيفتات مفتوحة + Auto Plan
        ✅ إدارة الأدوار
        ✅ الموارد المادية (Materials)
        ✅ تبادل الشيفتات (Shift Switch)
        ✅ إلغاء التخصيص
        ✅ إشعارات البريد الإلكتروني
        ✅ تقارير متقدمة
        ✅ ربط مع Sales & Project
    ''',
    'author': 'Ahmed Bebars',
    'category': 'Services/Planning',
    'depends': [
        'base',
        'mail',
        'resource',
        'hr',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/mail_templates.xml',
        'views/planning_shift_views.xml',
        'views/planning_role_views.xml',
        'views/planning_resource_views.xml',
        'views/planning_template_views.xml',
        'views/planning_config_views.xml',
        'views/planning_report_views.xml',
        'views/planning_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_planning/static/src/css/planning.css',
            'custom_planning/static/src/xml/planning_gantt.xml',
            'custom_planning/static/src/js/planning_gantt.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/src/img/planning_banner.png'],
}

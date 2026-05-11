# Custom Inventory Module — مديول إدارة المخزون

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)

## 📋 الوصف | Description

مديول Odoo مخصص لإدارة المخزون مع تتبع كامل للمنتجات والكميات وحركات الوارد والصادر.

## ✨ المميزات | Features

- ✅ إدارة كاملة للمنتجات (كود، فئة، وحدة، سعر)
- ✅ تتبع الكمية الفعلية والمتاحة والمحجوزة
- ✅ حركات المخزون (وارد / صادر / تعديل / تحويل)
- ✅ تنبيه تلقائي عند الوصول للحد الأدنى ⚠️
- ✅ Kanban View للمنتجات
- ✅ Workflow كامل للحركات (مسودة → مؤكد → منفذ)
- ✅ تلوين تلقائي في القوائم
- ✅ فلاتر بحث متقدمة
- ✅ Chatter & Activity log

## 🗂️ هيكل الملفات | Structure

```
custom_inventory/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product.py       ← نموذج المنتجات
│   └── movement.py      ← نموذج حركات المخزون
├── views/
│   ├── product_views.xml
│   ├── movement_views.xml
│   └── inventory_menus.xml
└── security/
    └── ir.model.access.csv
```

## 🚀 التثبيت | Installation

1. انسخ المجلد إلى `custom_addons`
2. أضف المسار في `odoo.conf`
3. شغّل: `./odoo-bin -u custom_inventory -d your_database`
4. ابحث عن "Custom Inventory" في Apps وثبّته

## 📦 المتطلبات | Dependencies

- Odoo 17.0 | Modules: `base`, `mail`

## 👤 المطور | Developer

**Ahmed Bebars** — [@ahmedbebars](https://github.com/ahmedbebars)

## 📄 License: LGPL-3

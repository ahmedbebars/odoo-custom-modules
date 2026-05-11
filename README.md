# Odoo Custom Modules — مديولات Odoo 17 مخصصة

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Author](https://img.shields.io/badge/Author-Ahmed%20Bebars-orange)
![Modules](https://img.shields.io/badge/Modules-4-brightgreen)

## 📦 المديولات

| المديول | الوصف | التثبيت |
|---------|-------|---------|
| [custom_calculations](./custom_calculations/) | 💰 الحسابات المالية المتقدمة (إيرادات، ربح، ضريبة) | `base, mail, account` |
| [custom_inventory](./custom_inventory/) | 📦 إدارة المخزون مع التنبيهات وتتبع الحركات | `base, mail, stock` |
| [custom_pos_enterprise](./custom_pos_enterprise/) | 🛒 POS: Split Bill, Loyalty, Floor Plan, Kitchen | `base, mail, point_of_sale` |
| [custom_planning](./custom_planning/) | 📅 جدولة الشيفتات: Roles, Auto Plan, Switch | `base, mail, hr` |

## 🚀 التثبيت

```bash
# نسخ المديول
cp -r custom_calculations /opt/odoo/custom-addons/

# تحديث
./odoo-bin -u custom_calculations -d your_database
```

أو مع Docker:
```bash
cd /opt/odoo/custom-addons
git clone https://github.com/ahmedbebars/odoo-custom-modules.git temp
cp -r temp/custom_calculations .
rm -rf temp
docker compose restart odoo
```

---
**Ahmed Bebars** | License: LGPL-3 | Odoo 17.0

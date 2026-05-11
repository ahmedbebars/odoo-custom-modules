# Custom Planning — مديول جدولة المناوبات

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Category](https://img.shields.io/badge/Category-Planning-purple)

مديول Planning كامل يضيف نظام جدولة شيفتات متكاملاً مع كل خصائص Enterprise.

---

## ✨ الخصائص

| الخاصية | الوصف |
|---------|-------|
| 📅 **جدول مرئي** | Calendar View أسبوعي/شهري مع ألوان |
| 🎭 **الأدوار** | تصنيف الموظفين بأدوار (نادل، شيف، كاشير...) |
| 👥 **الموارد** | موظفون ومعدات مادية |
| 📋 **قوالب الشيفتات** | قوالب جاهزة توفر وقت التحضير |
| 🔄 **شيفتات متكررة** | يومي / أسبوعي / شهري |
| 🔓 **شيفتات مفتوحة** | شيفتات بدون مورد جاهزة للتخصيص |
| 🤖 **Auto Plan** | توزيع تلقائي ذكي مراعياً التعارضات والإجازات |
| 🔁 **تبادل الشيفتات** | الموظف يطلب تبادل شيفته مع زميل |
| ❌ **إلغاء التخصيص** | الموظف يلغي شيفته ليصبح مفتوحاً |
| 📧 **إشعارات البريد** | قوالب HTML عربية للإشعارات |
| 📊 **تقارير** | Pivot + Graph + Calendar |

## 🚀 التثبيت

```bash
cp -r custom_planning /opt/odoo/custom-addons/
./odoo-bin -u custom_planning -d your_database
```

**المتطلبات:** `base`, `mail`, `resource`, `hr`, `hr_holidays`

## 👤 Ahmed Bebars | License: LGPL-3

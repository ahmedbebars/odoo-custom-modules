from odoo import models, fields


class PosFloor(models.Model):
    _name = 'pos.floor.plan'
    _description = 'مخطط الطابق'

    name = fields.Char(string='اسم الطابق', required=True)
    table_ids = fields.One2many('pos.table.plan', 'floor_id', string='الطاولات')
    active = fields.Boolean(default=True)


class PosTable(models.Model):
    _name = 'pos.table.plan'
    _description = 'طاولة'

    name = fields.Char(string='رقم الطاولة', required=True)
    floor_id = fields.Many2one('pos.floor.plan', string='الطابق', ondelete='cascade')
    seats = fields.Integer(string='عدد المقاعد', default=4)
    state = fields.Selection([
        ('available', '🟢 متاحة'), ('occupied', '🔴 مشغولة'),
        ('reserved', '🟡 محجوزة'), ('cleaning', '🔵 تنظيف'),
    ], default='available', string='الحالة')
    current_order_id = fields.Many2one('pos.order.extension', string='الأمر الحالي')
    x_position = fields.Integer(string='موضع X', default=0)
    y_position = fields.Integer(string='موضع Y', default=0)

    def action_occupy(self):
        self.write({'state': 'occupied'})

    def action_free(self):
        self.write({'state': 'available', 'current_order_id': False})

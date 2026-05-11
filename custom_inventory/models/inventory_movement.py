from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InventoryMovement(models.Model):
    _name = 'inventory.movement'
    _description = 'حركة المخزون'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(string='المرجع', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('inventory.movement') or 'MOV-0001')
    product_id = fields.Many2one('inventory.product', string='المنتج', required=True)
    movement_type = fields.Selection([
        ('in', '📥 وارد'), ('out', '📤 صادر'), ('transfer', '🔄 تحويل'),
    ], string='نوع الحركة', required=True)
    quantity = fields.Float(string='الكمية', required=True, digits=(16, 2))
    date = fields.Datetime(string='التاريخ', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'مسودة'), ('done', 'منفذ'), ('cancelled', 'ملغي'),
    ], default='draft', tracking=True)
    unit_cost = fields.Float(string='سعر الوحدة', digits=(16, 2))
    total_cost = fields.Float(string='إجمالي التكلفة', compute='_compute_total', store=True)
    notes = fields.Text(string='ملاحظات')

    @api.depends('quantity', 'unit_cost')
    def _compute_total(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.constrains('quantity')
    def _check_qty(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError('الكمية يجب أن تكون أكبر من صفر!')

    def action_confirm(self):
        for rec in self:
            if rec.movement_type == 'out':
                if rec.product_id.available_qty < rec.quantity:
                    raise ValidationError(f'الكمية المتاحة ({rec.product_id.available_qty}) أقل من المطلوبة ({rec.quantity})!')
            rec.state = 'done'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

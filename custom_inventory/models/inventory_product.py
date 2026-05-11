from odoo import models, fields, api


class InventoryProduct(models.Model):
    _name = 'inventory.product'
    _description = 'منتج المخزون'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='اسم المنتج', required=True, tracking=True)
    code = fields.Char(string='الكود', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('inventory.product') or 'NEW')
    category = fields.Selection([
        ('raw', 'مواد خام'), ('finished', 'منتج نهائي'),
        ('spare', 'قطع غيار'), ('consumable', 'مستهلكات'),
    ], string='الفئة', default='finished')
    unit = fields.Selection([
        ('pcs', 'قطعة'), ('kg', 'كيلو'), ('liter', 'لتر'), ('box', 'علبة'), ('meter', 'متر'),
    ], string='وحدة القياس', default='pcs')
    cost_price = fields.Float(string='سعر التكلفة', digits=(16, 2))
    sale_price = fields.Float(string='سعر البيع', digits=(16, 2))
    min_qty = fields.Float(string='الحد الأدنى', default=10.0)
    max_qty = fields.Float(string='الحد الأقصى', default=1000.0)
    current_qty = fields.Float(string='الكمية الحالية', compute='_compute_qty', store=True)
    reserved_qty = fields.Float(string='الكمية المحجوزة', default=0.0)
    available_qty = fields.Float(string='الكمية المتاحة', compute='_compute_qty', store=True)
    movement_ids = fields.One2many('inventory.movement', 'product_id', string='الحركات')
    active = fields.Boolean(default=True)
    low_stock_alert = fields.Boolean(string='تنبيه نقص المخزون', compute='_compute_qty', store=True)

    @api.depends('movement_ids.quantity', 'movement_ids.movement_type', 'reserved_qty')
    def _compute_qty(self):
        for rec in self:
            incoming = sum(rec.movement_ids.filtered(lambda m: m.movement_type == 'in' and m.state == 'done').mapped('quantity'))
            outgoing = sum(rec.movement_ids.filtered(lambda m: m.movement_type == 'out' and m.state == 'done').mapped('quantity'))
            rec.current_qty = incoming - outgoing
            rec.available_qty = rec.current_qty - rec.reserved_qty
            rec.low_stock_alert = rec.current_qty <= rec.min_qty

    _sql_constraints = [('code_unique', 'UNIQUE(code)', 'الكود يجب أن يكون فريداً!')]

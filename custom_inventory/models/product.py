from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InventoryProduct(models.Model):
    _name = 'inventory.product'
    _description = 'منتج المخزون'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='اسم المنتج', required=True, tracking=True)
    code = fields.Char(string='كود المنتج', required=True, copy=False)
    category = fields.Selection([
        ('raw', 'مواد خام'),
        ('finished', 'منتج تام'),
        ('semi', 'منتج نصف مصنع'),
        ('consumable', 'مستهلكات'),
        ('spare', 'قطع غيار'),
        ('other', 'أخرى'),
    ], string='الفئة', default='finished', required=True, tracking=True)

    description = fields.Text(string='الوصف')
    image = fields.Binary(string='صورة المنتج', attachment=True)

    # الكميات
    qty_on_hand = fields.Float(
        string='الكمية الفعلية',
        compute='_compute_quantities',
        store=True,
        digits=(16, 2),
    )
    qty_reserved = fields.Float(
        string='كمية محجوزة',
        compute='_compute_quantities',
        store=True,
        digits=(16, 2),
    )
    qty_available = fields.Float(
        string='الكمية المتاحة',
        compute='_compute_quantities',
        store=True,
        digits=(16, 2),
    )

    # حدود المخزون
    min_qty = fields.Float(string='الحد الأدنى للمخزون', default=0.0, digits=(16, 2))
    max_qty = fields.Float(string='الحد الأقصى للمخزون', default=0.0, digits=(16, 2))
    reorder_qty = fields.Float(string='كمية إعادة الطلب', default=0.0, digits=(16, 2))

    # التسعير
    cost_price = fields.Float(string='سعر التكلفة', digits=(16, 2), default=0.0)
    sale_price = fields.Float(string='سعر البيع', digits=(16, 2), default=0.0)

    # الوحدة والمورد
    unit = fields.Selection([
        ('piece', 'قطعة'),
        ('kg', 'كيلوجرام'),
        ('liter', 'لتر'),
        ('meter', 'متر'),
        ('box', 'علبة'),
        ('roll', 'لفة'),
        ('set', 'طقم'),
        ('other', 'أخرى'),
    ], string='وحدة القياس', default='piece', required=True)

    supplier = fields.Char(string='المورد الرئيسي')
    location = fields.Char(string='مكان التخزين')

    # الحركات
    movement_ids = fields.One2many(
        'inventory.movement', 'product_id',
        string='حركات المخزون',
    )
    movement_count = fields.Integer(
        string='عدد الحركات',
        compute='_compute_movement_count',
    )

    # الحالة
    active = fields.Boolean(string='نشط', default=True)
    low_stock_alert = fields.Boolean(
        string='تنبيه نقص المخزون',
        compute='_compute_low_stock',
        store=True,
    )

    # ===========================
    #  Compute Methods
    # ===========================
    @api.depends('movement_ids', 'movement_ids.quantity', 'movement_ids.move_type', 'movement_ids.state')
    def _compute_quantities(self):
        for rec in self:
            done_movements = rec.movement_ids.filtered(lambda m: m.state == 'done')
            in_qty = sum(done_movements.filtered(lambda m: m.move_type == 'in').mapped('quantity'))
            out_qty = sum(done_movements.filtered(lambda m: m.move_type == 'out').mapped('quantity'))
            reserved_qty = sum(
                rec.movement_ids.filtered(
                    lambda m: m.move_type == 'out' and m.state == 'confirmed'
                ).mapped('quantity')
            )
            rec.qty_on_hand = in_qty - out_qty
            rec.qty_reserved = reserved_qty
            rec.qty_available = rec.qty_on_hand - reserved_qty

    @api.depends('qty_on_hand', 'min_qty')
    def _compute_low_stock(self):
        for rec in self:
            rec.low_stock_alert = rec.min_qty > 0 and rec.qty_on_hand <= rec.min_qty

    def _compute_movement_count(self):
        for rec in self:
            rec.movement_count = len(rec.movement_ids)

    # ===========================
    #  Constraints
    # ===========================
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'كود المنتج يجب أن يكون فريداً!'),
    ]

    @api.constrains('min_qty', 'max_qty')
    def _check_qty_limits(self):
        for rec in self:
            if rec.max_qty > 0 and rec.min_qty > rec.max_qty:
                raise ValidationError('الحد الأدنى لا يمكن أن يكون أكبر من الحد الأقصى!')

    # ===========================
    #  Actions
    # ===========================
    def action_view_movements(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'حركات {self.name}',
            'res_model': 'inventory.movement',
            'view_mode': 'tree,form',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }

    def action_add_stock(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'إضافة مخزون',
            'res_model': 'inventory.movement',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_id': self.id,
                'default_move_type': 'in',
            },
        }

    def action_remove_stock(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'صرف مخزون',
            'res_model': 'inventory.movement',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_id': self.id,
                'default_move_type': 'out',
            },
        }

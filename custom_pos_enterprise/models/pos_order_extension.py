from odoo import models, fields, api
from odoo.exceptions import UserError


class PosOrderExtension(models.Model):
    _name = 'pos.order.extension'
    _description = 'تمديد أوامر POS'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='رقم الأمر', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('pos.order.extension') or 'POS-EXT-0001')
    session_id = fields.Many2one('pos.session.report', string='الجلسة')
    table_number = fields.Integer(string='رقم الطاولة')
    customer_name = fields.Char(string='اسم العميل')
    customer_count = fields.Integer(string='عدد الأشخاص', default=1)
    order_type = fields.Selection([
        ('dine_in', '🍽️ داخل المطعم'),
        ('takeaway', '🥡 تيك أواي'),
        ('delivery', '🚚 ديليفري'),
    ], string='نوع الطلب', default='dine_in', required=True)
    state = fields.Selection([
        ('open', 'مفتوح'), ('split', 'مقسّم'),
        ('paid', 'مدفوع'), ('cancelled', 'ملغي'),
    ], default='open', tracking=True)
    # Split Bill
    split_count = fields.Integer(string='عدد التقسيمات', default=1)
    split_amount = fields.Float(string='قيمة كل تقسيم', compute='_compute_split', store=True)
    # الإجماليات
    subtotal = fields.Float(string='المجموع الفرعي', digits=(16, 2))
    discount_amount = fields.Float(string='الخصم', digits=(16, 2))
    tax_amount = fields.Float(string='الضريبة (14%)', compute='_compute_totals', store=True, digits=(16, 2))
    total_amount = fields.Float(string='الإجمالي', compute='_compute_totals', store=True, digits=(16, 2))
    payment_method = fields.Selection([
        ('cash', '💵 كاش'), ('card', '💳 بطاقة'),
        ('split', '🔀 Split Cash+Card'), ('online', '📱 أونلاين'),
    ], string='طريقة الدفع', default='cash')
    notes = fields.Text(string='ملاحظات المطبخ')
    # Kitchen
    kitchen_status = fields.Selection([
        ('pending', 'قيد الانتظار'), ('preparing', 'يجهّز'),
        ('ready', 'جاهز'), ('served', 'قُدِّم'),
    ], default='pending', string='حالة المطبخ', tracking=True)
    line_ids = fields.One2many('pos.order.ext.line', 'order_id', string='الأصناف')

    @api.depends('subtotal', 'discount_amount')
    def _compute_totals(self):
        for rec in self:
            after_discount = rec.subtotal - rec.discount_amount
            rec.tax_amount = after_discount * 0.14
            rec.total_amount = after_discount + rec.tax_amount

    @api.depends('total_amount', 'split_count')
    def _compute_split(self):
        for rec in self:
            rec.split_amount = rec.total_amount / rec.split_count if rec.split_count > 0 else 0

    def action_split_bill(self):
        self.write({'state': 'split'})

    def action_send_to_kitchen(self):
        self.write({'kitchen_status': 'preparing'})

    def action_mark_ready(self):
        self.write({'kitchen_status': 'ready'})

    def action_pay(self):
        self.write({'state': 'paid', 'kitchen_status': 'served'})


class PosOrderExtLine(models.Model):
    _name = 'pos.order.ext.line'
    _description = 'صنف الأمر'

    order_id = fields.Many2one('pos.order.extension', string='الأمر', ondelete='cascade')
    product_name = fields.Char(string='الصنف', required=True)
    quantity = fields.Float(string='الكمية', default=1.0)
    unit_price = fields.Float(string='السعر', digits=(16, 2))
    subtotal = fields.Float(string='الإجمالي', compute='_compute_sub', store=True)
    notes = fields.Char(string='ملاحظة خاصة')

    @api.depends('quantity', 'unit_price')
    def _compute_sub(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

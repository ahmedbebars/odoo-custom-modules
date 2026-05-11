from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FinancialCalculation(models.Model):
    _name = 'financial.calculation'
    _description = 'الحساب المالي'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(string='اسم الحساب', required=True, tracking=True)
    date = fields.Date(string='التاريخ', default=fields.Date.today, required=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('done', 'منتهي'),
    ], string='الحالة', default='draft', tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # الإيرادات
    revenue = fields.Float(string='الإيرادات الأساسية', digits=(16, 2))
    other_revenue = fields.Float(string='الإيرادات الأخرى', digits=(16, 2))
    total_revenue = fields.Float(string='إجمالي الإيرادات', compute='_compute_all', store=True, digits=(16, 2))

    # التكاليف
    cost_of_goods = fields.Float(string='تكلفة البضاعة المباعة', digits=(16, 2))
    gross_profit = fields.Float(string='الربح الإجمالي', compute='_compute_all', store=True, digits=(16, 2))
    gross_margin = fields.Float(string='هامش الربح الإجمالي (%)', compute='_compute_all', store=True)

    # المصروفات التشغيلية
    operating_expenses = fields.Float(string='المصروفات التشغيلية', digits=(16, 2))
    operating_profit = fields.Float(string='ربح التشغيل', compute='_compute_all', store=True, digits=(16, 2))

    # الخصم والضريبة
    discount_rate = fields.Float(string='نسبة الخصم (%)', default=0.0)
    discount_amount = fields.Float(string='مبلغ الخصم', compute='_compute_all', store=True, digits=(16, 2))
    tax_rate = fields.Float(string='نسبة الضريبة (%)', default=14.0)
    tax_amount = fields.Float(string='مبلغ الضريبة', compute='_compute_all', store=True, digits=(16, 2))

    # صافي الربح
    net_profit = fields.Float(string='صافي الربح', compute='_compute_all', store=True, digits=(16, 2))
    net_margin = fields.Float(string='هامش صافي الربح (%)', compute='_compute_all', store=True)
    is_profitable = fields.Boolean(string='رابح', compute='_compute_all', store=True)

    notes = fields.Text(string='ملاحظات')

    @api.depends('revenue', 'other_revenue', 'cost_of_goods', 'operating_expenses',
                 'discount_rate', 'tax_rate')
    def _compute_all(self):
        for rec in self:
            rec.total_revenue = rec.revenue + rec.other_revenue
            rec.gross_profit = rec.total_revenue - rec.cost_of_goods
            rec.gross_margin = (rec.gross_profit / rec.total_revenue * 100) if rec.total_revenue else 0.0
            rec.operating_profit = rec.gross_profit - rec.operating_expenses
            rec.discount_amount = rec.operating_profit * rec.discount_rate / 100
            after_discount = rec.operating_profit - rec.discount_amount
            rec.tax_amount = after_discount * rec.tax_rate / 100
            rec.net_profit = after_discount - rec.tax_amount
            rec.net_margin = (rec.net_profit / rec.total_revenue * 100) if rec.total_revenue else 0.0
            rec.is_profitable = rec.net_profit > 0

    @api.constrains('discount_rate', 'tax_rate')
    def _check_rates(self):
        for rec in self:
            if not (0 <= rec.discount_rate <= 100):
                raise ValidationError('نسبة الخصم يجب أن تكون بين 0 و 100!')
            if not (0 <= rec.tax_rate <= 100):
                raise ValidationError('نسبة الضريبة يجب أن تكون بين 0 و 100!')

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_draft(self):
        self.write({'state': 'draft'})

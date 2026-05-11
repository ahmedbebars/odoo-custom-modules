from odoo import models, fields, api


class PosSessionReport(models.Model):
    _name = 'pos.session.report'
    _description = 'تقرير جلسة POS'
    _inherit = ['mail.thread']

    name = fields.Char(string='اسم الجلسة', required=True)
    date = fields.Date(string='التاريخ', default=fields.Date.today)
    cashier_id = fields.Many2one('res.users', string='الكاشير', default=lambda self: self.env.user)
    state = fields.Selection([
        ('open', 'مفتوحة'), ('closing', 'جارٍ الإغلاق'), ('closed', 'مغلقة'),
    ], default='open', tracking=True)
    order_ids = fields.One2many('pos.order.extension', 'session_id', string='الطلبات')
    # إحصائيات
    total_orders = fields.Integer(compute='_compute_stats', store=True)
    total_revenue = fields.Float(compute='_compute_stats', store=True, digits=(16, 2))
    cash_amount = fields.Float(compute='_compute_stats', store=True, digits=(16, 2))
    card_amount = fields.Float(compute='_compute_stats', store=True, digits=(16, 2))
    opening_cash = fields.Float(string='كاش الافتتاح', digits=(16, 2))
    closing_cash = fields.Float(string='كاش الإغلاق الفعلي', digits=(16, 2))
    cash_difference = fields.Float(string='الفرق', compute='_compute_diff', store=True)

    @api.depends('order_ids', 'order_ids.total_amount', 'order_ids.state')
    def _compute_stats(self):
        for rec in self:
            paid = rec.order_ids.filtered(lambda o: o.state == 'paid')
            rec.total_orders = len(paid)
            rec.total_revenue = sum(paid.mapped('total_amount'))
            rec.cash_amount = sum(paid.filtered(lambda o: o.payment_method == 'cash').mapped('total_amount'))
            rec.card_amount = sum(paid.filtered(lambda o: o.payment_method == 'card').mapped('total_amount'))

    @api.depends('opening_cash', 'cash_amount', 'closing_cash')
    def _compute_diff(self):
        for rec in self:
            expected = rec.opening_cash + rec.cash_amount
            rec.cash_difference = rec.closing_cash - expected

    def action_close_session(self):
        self.write({'state': 'closed'})

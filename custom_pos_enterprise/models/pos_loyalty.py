from odoo import models, fields, api


class PosLoyaltyProgram(models.Model):
    _name = 'pos.loyalty.program'
    _description = 'برنامج الولاء'

    name = fields.Char(required=True)
    points_per_amount = fields.Float(string='نقاط لكل جنيه', default=1.0)
    min_points_redeem = fields.Integer(string='أقل نقاط للاسترداد', default=100)
    redeem_value = fields.Float(string='قيمة كل 100 نقطة (جنيه)', default=5.0)
    active = fields.Boolean(default=True)


class PosLoyaltyCard(models.Model):
    _name = 'pos.loyalty.card'
    _description = 'بطاقة الولاء'
    _inherit = ['mail.thread']

    name = fields.Char(string='رقم البطاقة', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('pos.loyalty.card') or 'LOYALTY-0001')
    customer_name = fields.Char(string='اسم العميل', required=True)
    phone = fields.Char(string='الهاتف')
    points = fields.Float(string='النقاط المتراكمة', default=0.0)
    total_spent = fields.Float(string='إجمالي الإنفاق', digits=(16, 2))
    program_id = fields.Many2one('pos.loyalty.program', string='البرنامج')
    tier = fields.Selection([
        ('bronze', '🥉 برونزي'), ('silver', '🥈 فضي'),
        ('gold', '🥇 ذهبي'), ('platinum', '💎 بلاتيني'),
    ], compute='_compute_tier', store=True)

    @api.depends('points')
    def _compute_tier(self):
        for rec in self:
            if rec.points >= 10000:
                rec.tier = 'platinum'
            elif rec.points >= 5000:
                rec.tier = 'gold'
            elif rec.points >= 1000:
                rec.tier = 'silver'
            else:
                rec.tier = 'bronze'

    def action_add_points(self, amount):
        if self.program_id:
            self.points += amount * self.program_id.points_per_amount
            self.total_spent += amount

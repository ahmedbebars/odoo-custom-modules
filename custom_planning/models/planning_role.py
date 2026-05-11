from odoo import models, fields, api


class PlanningRole(models.Model):
    _name = 'planning.role'
    _description = 'دور في التخطيط'
    _order = 'sequence, name'

    name = fields.Char(string='اسم الدور', required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='اللون', default=0)
    resource_ids = fields.Many2many(
        'planning.resource', string='الموارد بهذا الدور',
    )

    # ربط مع Sales
    product_ids = fields.Many2many(
        'product.product', string='الخدمات المرتبطة',
        domain=[('type', '=', 'service')],
    )

    # إحصائيات
    shift_count = fields.Integer(
        string='عدد الشيفتات', compute='_compute_shift_count',
    )

    @api.depends()
    def _compute_shift_count(self):
        for rec in self:
            rec.shift_count = self.env['planning.shift'].search_count(
                [('role_id', '=', rec.id)]
            )

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PlanningResource(models.Model):
    _name = 'planning.resource'
    _description = 'مورد التخطيط (موظف أو معدات)'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(string='الاسم', required=True)
    resource_type = fields.Selection([
        ('employee', 'موظف'),
        ('material', 'معدات / مواد'),
    ], string='نوع المورد', default='employee', required=True)

    # للموظفين
    employee_id = fields.Many2one(
        'hr.employee', string='الموظف',
        domain=[('active', '=', True)],
    )

    # الأدوار
    role_ids = fields.Many2many(
        'planning.role', string='الأدوار',
    )
    default_role_id = fields.Many2one(
        'planning.role', string='الدور الافتراضي',
        domain="[('id', 'in', role_ids)]",
    )

    # ساعات العمل
    work_time_ids = fields.Many2many(
        'resource.calendar', string='جدول ساعات العمل',
    )

    active = fields.Boolean(default=True)
    color = fields.Integer(string='اللون', default=0)
    avatar = fields.Binary(string='الصورة', related='employee_id.image_128', readonly=True)

    # إحصائيات
    shift_count = fields.Integer(
        string='عدد الشيفتات', compute='_compute_stats',
    )
    planned_hours = fields.Float(
        string='ساعات مخططة هذا الشهر', compute='_compute_stats',
    )

    @api.depends()
    def _compute_stats(self):
        import calendar
        from datetime import date
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        for rec in self:
            shifts = self.env['planning.shift'].search([
                ('resource_id', '=', rec.id),
                ('start_datetime', '>=', str(first_day)),
                ('end_datetime', '<=', str(last_day)),
            ])
            rec.shift_count = len(shifts)
            rec.planned_hours = sum(shifts.mapped('allocated_hours'))

    @api.constrains('default_role_id', 'role_ids')
    def _check_default_role(self):
        for rec in self:
            if rec.default_role_id and rec.default_role_id not in rec.role_ids:
                raise ValidationError('الدور الافتراضي يجب أن يكون ضمن الأدوار المحددة!')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.name = self.employee_id.name

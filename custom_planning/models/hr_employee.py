from odoo import models, fields


class HrEmployee(models.Model):
    """تمديد الموظف بإعدادات Planning"""
    _inherit = 'hr.employee'

    planning_role_ids = fields.Many2many(
        'planning.role',
        'hr_employee_planning_role_rel',
        string='أدوار التخطيط',
    )
    planning_default_role_id = fields.Many2one(
        'planning.role',
        string='الدور الافتراضي في التخطيط',
    )
    planning_resource_id = fields.Many2one(
        'planning.resource',
        string='مورد التخطيط المرتبط',
        readonly=True,
    )
    # إحصائيات
    planned_shifts_count = fields.Integer(
        string='عدد الشيفتات المقبلة',
        compute='_compute_planning_stats',
    )
    planned_hours_month = fields.Float(
        string='ساعات مخططة هذا الشهر',
        compute='_compute_planning_stats',
    )

    def _compute_planning_stats(self):
        from datetime import date
        import calendar
        today = date.today()
        first = today.replace(day=1)
        last = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        for emp in self:
            resource = emp.planning_resource_id
            if resource:
                shifts = self.env['planning.shift'].search([
                    ('resource_id', '=', resource.id),
                    ('start_datetime', '>=', str(first)),
                    ('end_datetime', '<=', str(last)),
                    ('state', '!=', 'cancelled'),
                ])
                emp.planned_shifts_count = len(shifts)
                emp.planned_hours_month = sum(shifts.mapped('allocated_hours'))
            else:
                emp.planned_shifts_count = 0
                emp.planned_hours_month = 0.0

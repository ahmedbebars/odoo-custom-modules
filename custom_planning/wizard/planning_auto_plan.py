from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PlanningAutoPlan(models.TransientModel):
    _name = 'planning.auto.plan'
    _description = 'التخطيط التلقائي للشيفتات المفتوحة'

    date_start = fields.Date(string='من تاريخ', required=True, default=fields.Date.today)
    date_end = fields.Date(
        string='إلى تاريخ', required=True,
        default=lambda self: (datetime.today() + timedelta(weeks=1)).date(),
    )
    consider_time_off = fields.Boolean(string='مراعاة الإجازات', default=True)
    consider_working_hours = fields.Boolean(string='مراعاة ساعات العمل', default=True)
    consider_contracts = fields.Boolean(string='مراعاة العقود', default=True)

    open_shifts_count = fields.Integer(
        string='عدد الشيفتات المفتوحة',
        compute='_compute_open_shifts',
    )

    @api.depends('date_start', 'date_end')
    def _compute_open_shifts(self):
        for rec in self:
            rec.open_shifts_count = self.env['planning.shift'].search_count([
                ('resource_id', '=', False),
                ('state', '=', 'draft'),
                ('start_datetime', '>=', str(rec.date_start)),
                ('start_datetime', '<=', str(rec.date_end)),
            ])

    def action_auto_plan(self):
        """التوزيع التلقائي للشيفتات المفتوحة"""
        self.ensure_one()
        open_shifts = self.env['planning.shift'].search([
            ('resource_id', '=', False),
            ('state', '=', 'draft'),
            ('start_datetime', '>=', str(self.date_start)),
            ('start_datetime', '<=', str(self.date_end)),
        ])

        if not open_shifts:
            raise UserError('لا توجد شيفتات مفتوحة في هذه الفترة!')

        assigned = 0
        for shift in open_shifts:
            resource = self._find_best_resource(shift)
            if resource:
                shift.write({'resource_id': resource.id})
                assigned += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Auto Plan مكتمل!',
                'message': f'تم تخصيص {assigned} شيفت من أصل {len(open_shifts)}',
                'type': 'success' if assigned == len(open_shifts) else 'warning',
            }
        }

    def _find_best_resource(self, shift):
        """إيجاد أنسب مورد للشيفت"""
        domain = [('active', '=', True)]

        # فلترة بالدور
        if shift.role_id:
            domain.append(('role_ids', 'in', [shift.role_id.id]))

        resources = self.env['planning.resource'].search(domain)

        for resource in resources:
            # تحقق من عدم وجود تعارض
            conflict = self.env['planning.shift'].search_count([
                ('resource_id', '=', resource.id),
                ('state', 'not in', ['cancelled']),
                ('start_datetime', '<', shift.end_datetime),
                ('end_datetime', '>', shift.start_datetime),
                ('id', '!=', shift.id),
            ])
            if not conflict:
                return resource

        return False

from odoo import models, fields, api


class PlanningSendSchedule(models.TransientModel):
    _name = 'planning.send.schedule'
    _description = 'إرسال الجدول للموظفين'

    date_start = fields.Date(string='من تاريخ', required=True, default=fields.Date.today)
    date_end = fields.Date(string='إلى تاريخ', required=True)
    resource_ids = fields.Many2many(
        'planning.resource', string='الموارد',
        help='اتركه فارغاً لإرسال للكل',
    )
    shifts_count = fields.Integer(
        string='عدد الشيفتات', compute='_compute_count',
    )

    @api.depends('date_start', 'date_end', 'resource_ids')
    def _compute_count(self):
        for rec in self:
            domain = [
                ('state', '=', 'draft'),
                ('start_datetime', '>=', str(rec.date_start) if rec.date_start else '2000-01-01'),
            ]
            if rec.resource_ids:
                domain.append(('resource_id', 'in', rec.resource_ids.ids))
            rec.shifts_count = self.env['planning.shift'].search_count(domain)

    def action_publish_and_send(self):
        """نشر الجدول وإرسال الإشعارات"""
        domain = [
            ('state', '=', 'draft'),
            ('start_datetime', '>=', str(self.date_start)),
        ]
        if self.date_end:
            domain.append(('end_datetime', '<=', str(self.date_end)))
        if self.resource_ids:
            domain.append(('resource_id', 'in', self.resource_ids.ids))

        shifts = self.env['planning.shift'].search(domain)
        shifts_with_resource = shifts.filtered(lambda s: s.resource_id)
        shifts_with_resource.write({'state': 'published'})

        # إرسال إشعارات
        for shift in shifts_with_resource:
            shift._send_notification()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تم النشر!',
                'message': f'تم نشر {len(shifts_with_resource)} شيفت وإرسال الإشعارات',
                'type': 'success',
            }
        }

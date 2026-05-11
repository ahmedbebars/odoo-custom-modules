from odoo import models, fields


class PlanningShiftTemplate(models.Model):
    _name = 'planning.shift.template'
    _description = 'قالب الشيفت'
    _order = 'name'

    name = fields.Char(string='اسم القالب', required=True)
    role_id = fields.Many2one('planning.role', string='الدور')

    # وقت البداية والمدة
    start_hour = fields.Float(string='ساعة البداية', default=8.0)
    duration = fields.Float(string='المدة (ساعات)', default=8.0)

    # حساب وقت النهاية
    end_hour = fields.Float(
        string='ساعة النهاية', compute='_compute_end_hour', store=True,
    )

    color = fields.Integer(string='اللون', default=0)
    active = fields.Boolean(default=True)
    note = fields.Text(string='ملاحظات')

    def _compute_end_hour(self):
        for rec in self:
            rec.end_hour = (rec.start_hour + rec.duration) % 24

    def name_get(self):
        result = []
        for rec in self:
            start_h = int(rec.start_hour)
            start_m = int((rec.start_hour - start_h) * 60)
            end_h = int(rec.end_hour)
            end_m = int((rec.end_hour - end_h) * 60)
            name = f"{rec.name} ({start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d})"
            result.append((rec.id, name))
        return result

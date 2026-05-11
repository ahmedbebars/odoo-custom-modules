from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class PlanningShift(models.Model):
    _name = 'planning.shift'
    _description = 'شيفت / مناوبة'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime'

    name = fields.Char(
        string='اسم الشيفت', compute='_compute_name', store=True,
    )

    # المورد والدور
    resource_id = fields.Many2one(
        'planning.resource', string='المورد (موظف/معدة)',
        tracking=True, index=True,
    )
    role_id = fields.Many2one(
        'planning.role', string='الدور',
        tracking=True,
    )
    template_id = fields.Many2one(
        'planning.shift.template', string='القالب',
    )

    # الوقت
    start_datetime = fields.Datetime(
        string='وقت البداية', required=True, tracking=True,
    )
    end_datetime = fields.Datetime(
        string='وقت النهاية', required=True, tracking=True,
    )
    allocated_hours = fields.Float(
        string='الساعات المخصصة', compute='_compute_allocated_hours', store=True,
    )
    allocated_percentage = fields.Float(
        string='نسبة الوقت المخصص (%)', default=100.0,
    )

    # الحالة
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('done', 'منتهي'),
        ('cancelled', 'ملغي'),
    ], string='الحالة', default='draft', tracking=True)

    is_published = fields.Boolean(
        string='منشور', compute='_compute_is_published', store=True,
    )

    # الشيفتات المفتوحة (بدون مورد)
    is_open_shift = fields.Boolean(
        string='شيفت مفتوح', compute='_compute_is_open', store=True,
    )

    # التكرار
    repeat = fields.Boolean(string='متكرر', default=False)
    repeat_type = fields.Selection([
        ('daily', 'يومي'),
        ('weekly', 'أسبوعي'),
        ('monthly', 'شهري'),
    ], string='نوع التكرار', default='weekly')
    repeat_interval = fields.Integer(string='كل كم', default=1)
    repeat_until = fields.Date(string='التكرار حتى')
    repeat_parent_id = fields.Many2one('planning.shift', string='الشيفت الأصلي')

    # تبادل الشيفتات
    switch_requested = fields.Boolean(string='طلب تبادل', default=False)
    switch_requested_by = fields.Many2one(
        'planning.resource', string='طلب التبادل من',
    )

    # ربط مع Sales و Project
    sale_order_id = fields.Many2one('sale.order', string='أمر البيع') \
        if False else fields.Char(string='أمر البيع (مرجع)')
    project_id = fields.Many2one('project.project', string='المشروع') \
        if False else fields.Char(string='المشروع (مرجع)')

    # ملاحظات
    note = fields.Text(string='ملاحظة للموظف')
    color = fields.Integer(string='اللون', compute='_compute_color', store=True)

    _sql_constraints = [
        ('start_end_check', 'CHECK(end_datetime > start_datetime)',
         'وقت النهاية يجب أن يكون بعد وقت البداية!'),
    ]

    # ============ Compute Methods ============

    @api.depends('resource_id', 'role_id', 'start_datetime')
    def _compute_name(self):
        for rec in self:
            parts = []
            if rec.resource_id:
                parts.append(rec.resource_id.name)
            if rec.role_id:
                parts.append(rec.role_id.name)
            if rec.start_datetime:
                parts.append(rec.start_datetime.strftime('%d/%m %H:%M'))
            rec.name = ' - '.join(parts) if parts else 'شيفت جديد'

    @api.depends('start_datetime', 'end_datetime')
    def _compute_allocated_hours(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime:
                delta = rec.end_datetime - rec.start_datetime
                rec.allocated_hours = delta.total_seconds() / 3600
            else:
                rec.allocated_hours = 0.0

    @api.depends('state')
    def _compute_is_published(self):
        for rec in self:
            rec.is_published = rec.state == 'published'

    @api.depends('resource_id')
    def _compute_is_open(self):
        for rec in self:
            rec.is_open_shift = not bool(rec.resource_id)

    @api.depends('role_id', 'state')
    def _compute_color(self):
        for rec in self:
            if rec.state == 'cancelled':
                rec.color = 1  # أحمر
            elif rec.is_open_shift:
                rec.color = 3  # أصفر
            elif rec.role_id:
                rec.color = rec.role_id.color
            else:
                rec.color = 0

    # ============ Onchange Methods ============

    @api.onchange('template_id')
    def _onchange_template(self):
        if self.template_id and self.start_datetime:
            template = self.template_id
            start = self.start_datetime.replace(
                hour=int(template.start_hour),
                minute=int((template.start_hour % 1) * 60),
                second=0,
            )
            self.start_datetime = start
            self.end_datetime = start + timedelta(hours=template.duration)
            if template.role_id:
                self.role_id = template.role_id

    @api.onchange('resource_id')
    def _onchange_resource(self):
        if self.resource_id and self.resource_id.default_role_id:
            self.role_id = self.resource_id.default_role_id

    # ============ Constraints ============

    @api.constrains('start_datetime', 'end_datetime', 'resource_id')
    def _check_overlap(self):
        for rec in self:
            if not rec.resource_id:
                continue
            overlapping = self.search([
                ('id', '!=', rec.id),
                ('resource_id', '=', rec.resource_id.id),
                ('state', 'not in', ['cancelled']),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
            ])
            if overlapping:
                raise ValidationError(
                    f'تعارض! {rec.resource_id.name} عنده شيفت في نفس الوقت:\n'
                    f'{overlapping[0].name}'
                )

    # ============ Actions ============

    def action_publish(self):
        for rec in self:
            if not rec.resource_id:
                raise UserError('لا يمكن نشر شيفت مفتوح بدون تعيين مورد!')
            rec.state = 'published'
            rec._send_notification()

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_request_switch(self):
        """طلب تبادل الشيفت"""
        self.ensure_one()
        if self.state != 'published':
            raise UserError('يمكن طلب التبادل فقط للشيفتات المنشورة!')
        self.write({
            'switch_requested': True,
            'switch_requested_by': self.resource_id.id,
        })
        # إرسال إشعار للموظفين بنفس الدور
        self._notify_switch_request()

    def action_take_shift(self, resource_id):
        """موظف يأخذ الشيفت"""
        self.ensure_one()
        resource = self.env['planning.resource'].browse(resource_id)
        old_resource = self.resource_id
        self.write({
            'resource_id': resource.id,
            'switch_requested': False,
            'switch_requested_by': False,
        })
        self.message_post(
            body=f'تم تبادل الشيفت: من {old_resource.name} إلى {resource.name}'
        )

    def action_unassign(self):
        """إلغاء تخصيص الشيفت"""
        self.ensure_one()
        self.write({'resource_id': False, 'switch_requested': False})
        self.message_post(body='تم إلغاء التخصيص — الشيفت أصبح مفتوحاً')

    def _send_notification(self):
        """إرسال إشعار للمورد عن الشيفت المنشور"""
        for rec in self:
            if rec.resource_id and rec.resource_id.employee_id:
                template = self.env.ref(
                    'custom_planning.email_template_shift_published', False
                )
                if template:
                    template.send_mail(rec.id, force_send=True)

    def _notify_switch_request(self):
        """إشعار الموظفين بطلب تبادل الشيفت"""
        pass

    def action_create_recurring(self):
        """إنشاء الشيفتات المتكررة"""
        self.ensure_one()
        if not self.repeat or not self.repeat_until:
            raise UserError('يرجى تحديد إعدادات التكرار وتاريخ الانتهاء!')

        current = self.start_datetime
        end = self.end_datetime
        count = 0

        while True:
            if self.repeat_type == 'daily':
                delta = timedelta(days=self.repeat_interval)
            elif self.repeat_type == 'weekly':
                delta = timedelta(weeks=self.repeat_interval)
            else:
                # monthly
                delta = timedelta(days=30 * self.repeat_interval)

            current = current + delta
            end = end + delta

            if current.date() > self.repeat_until:
                break

            self.copy({
                'start_datetime': current,
                'end_datetime': end,
                'state': 'draft',
                'repeat': False,
                'repeat_parent_id': self.id,
            })
            count += 1

            if count > 365:
                break

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'تم!',
                'message': f'تم إنشاء {count} شيفت متكرر',
                'type': 'success',
            }
        }

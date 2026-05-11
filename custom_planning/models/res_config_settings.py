from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    planning_allow_unassignment = fields.Boolean(
        string='السماح بإلغاء التخصيص الذاتي',
        config_parameter='custom_planning.allow_unassignment',
        default=False,
    )
    planning_unassignment_days = fields.Integer(
        string='الحد الأقصى للإلغاء قبل الشيفت (أيام)',
        config_parameter='custom_planning.unassignment_days',
        default=2,
    )
    planning_recurring_months = fields.Integer(
        string='الشيفتات المتكررة مسبقاً (أشهر)',
        config_parameter='custom_planning.recurring_months',
        default=6,
    )
    planning_send_email = fields.Boolean(
        string='إرسال إشعارات البريد عند النشر',
        config_parameter='custom_planning.send_email',
        default=True,
    )

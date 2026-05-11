from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class InventoryMovement(models.Model):
    _name = 'inventory.movement'
    _description = 'حركة المخزون'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='رقم الحركة',
        required=True,
        copy=False,
        readonly=True,
        default='جديد',
    )
    date = fields.Datetime(
        string='تاريخ الحركة',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    product_id = fields.Many2one(
        'inventory.product',
        string='المنتج',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    move_type = fields.Selection([
        ('in', 'وارد (إضافة)'),
        ('out', 'صادر (صرف)'),
        ('adjust', 'تعديل جرد'),
        ('transfer', 'تحويل'),
    ], string='نوع الحركة', required=True, default='in', tracking=True)

    quantity = fields.Float(
        string='الكمية',
        required=True,
        digits=(16, 2),
        tracking=True,
    )
    unit_price = fields.Float(
        string='سعر الوحدة',
        digits=(16, 2),
        default=0.0,
    )
    total_value = fields.Float(
        string='إجمالي القيمة',
        compute='_compute_total_value',
        store=True,
        digits=(16, 2),
    )

    reference = fields.Char(string='المرجع / رقم الفاتورة')
    partner = fields.Char(string='المورد / العميل')
    notes = fields.Text(string='ملاحظات')

    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('done', 'منفذ'),
        ('cancelled', 'ملغي'),
    ], string='الحالة', default='draft', tracking=True)

    # Computed: qty available before movement
    qty_before = fields.Float(
        string='الكمية قبل الحركة',
        compute='_compute_qty_before',
        digits=(16, 2),
    )

    # ===========================
    #  Compute Methods
    # ===========================
    @api.depends('quantity', 'unit_price')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = rec.quantity * rec.unit_price

    def _compute_qty_before(self):
        for rec in self:
            if rec.product_id:
                rec.qty_before = rec.product_id.qty_on_hand
            else:
                rec.qty_before = 0.0

    # ===========================
    #  Sequence
    # ===========================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'جديد') == 'جديد':
                prefix = {
                    'in': 'IN',
                    'out': 'OUT',
                    'adjust': 'ADJ',
                    'transfer': 'TRF',
                }.get(vals.get('move_type', 'in'), 'MOV')
                seq = self.env['ir.sequence'].next_by_code('inventory.movement') or '0001'
                vals['name'] = f'{prefix}/{seq}'
        return super().create(vals_list)

    # ===========================
    #  Constraints
    # ===========================
    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError('الكمية يجب أن تكون أكبر من صفر!')

    @api.constrains('move_type', 'quantity', 'state')
    def _check_stock_availability(self):
        for rec in self:
            if rec.move_type == 'out' and rec.state == 'done':
                if rec.product_id.qty_available < 0:
                    raise ValidationError(
                        f'لا توجد كمية كافية من المنتج "{rec.product_id.name}"!\n'
                        f'الكمية المتاحة: {rec.product_id.qty_on_hand}'
                    )

    # ===========================
    #  Actions / Workflow
    # ===========================
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.write({'state': 'confirmed'})

    def action_done(self):
        for rec in self:
            if rec.state in ('draft', 'confirmed'):
                if rec.move_type == 'out':
                    available = rec.product_id.qty_on_hand
                    if available < rec.quantity:
                        raise UserError(
                            f'الكمية المطلوبة ({rec.quantity}) أكبر من المتاح ({available})!'
                        )
                rec.write({'state': 'done'})
                rec.product_id._compute_quantities()

    def action_cancel(self):
        for rec in self:
            if rec.state != 'done':
                rec.write({'state': 'cancelled'})
            else:
                raise UserError('لا يمكن إلغاء حركة منفذة!')

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'cancelled':
                rec.write({'state': 'draft'})

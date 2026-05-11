from odoo import models, fields


class InventoryAdjustment(models.TransientModel):
    _name = 'inventory.adjustment'
    _description = 'تسوية المخزون'

    product_id = fields.Many2one('inventory.product', string='المنتج', required=True)
    actual_qty = fields.Float(string='الكمية الفعلية', required=True)
    reason = fields.Text(string='سبب التسوية')

    def action_apply(self):
        product = self.product_id
        diff = self.actual_qty - product.current_qty
        if diff != 0:
            movement_type = 'in' if diff > 0 else 'out'
            self.env['inventory.movement'].create({
                'product_id': product.id,
                'movement_type': movement_type,
                'quantity': abs(diff),
                'notes': f'تسوية مخزون: {self.reason or ""}',
                'state': 'done',
            })
        return {'type': 'ir.actions.act_window_close'}

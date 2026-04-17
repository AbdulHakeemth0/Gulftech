from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.http import request





class SaleInherit(models.Model):
    _inherit = "sale.order"

    location = fields.Many2one(
        'stock.location', string='Location')



# this is the  function for adding the field in the stock.picking ware already in sale.order
    def action_confirm(self):
        print('ssaaaaaaaaaaaaaa')
        res = super(SaleInherit, self).action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.write({'location': order.location.id})
        return res
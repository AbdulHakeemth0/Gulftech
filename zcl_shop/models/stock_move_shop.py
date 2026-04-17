from odoo import fields, models, api


class Stocks(models.Model):
    _inherit = "stock.move"
    _description = "Transfer"

    items_id = fields.Many2one('product.product',string="Items")
    serial_no = fields.Integer(string="Sl no")
    link_1 = fields.Char(string="Link-1")
    units = fields.Many2one('uom.uom',string="Units")

    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                record.product_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                record.product_id = product.id
                record.items_id.display_name = product.display_name

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock Picking"

    direct_transfer = fields.Boolean(string="Direct transfer")
    shop_transfer = fields.Boolean(string="Shop transfer")
    damage_stock_out = fields.Boolean(string="Damage stock out")
    damage_stock_in = fields.Boolean(string="Damage stock in")

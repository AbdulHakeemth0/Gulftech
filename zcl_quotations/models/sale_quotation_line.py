# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models, api


class SaleQuotationLine(models.Model):
    _name = 'sale.quotation.line'
    _description = "sale quotation line"

    sno = fields.Integer(string="Sno", store=True)
    item_id = fields.Many2one('product.product', string="Item", required=True)
    items_id = fields.Many2one('product.product', string="Item", required=True)
    description = fields.Char(string="Description")
    units = fields.Many2one('uom.uom',string="Units")
    qty = fields.Float(string="Qty", default=1.0)
    rate = fields.Float(string="Rate", digits=(16, 3))
    gross = fields.Float(string="Gross", digits=(16, 3), readonly=True)
    sale_type = fields.Char(string="Sale Type", readonly=True)
    discount_on_foc = fields.Float(string="Discount on FOC", digits=(16, 3), readonly=True)
    bottom_price = fields.Float(string="Bottom Price", digits=(16, 3), readonly=True)
    net_value = fields.Float(string="Net Value", digits=(16, 3), readonly=True,compute="_net_value",store=True)
    stock_in_hand = fields.Float(string="Stock in hand", readonly=True)
    quotation_id = fields.Many2one('sale.quotation')
    description = fields.Char(string="Label")

    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                record.item_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                record.item_id = product.id
                record.item_id.display_name = product.display_name

    @api.onchange('item_id')
    def _find_data(self):
        self.rate = self.item_id.cntr_max_price
        self.bottom_price = self.item_id.cntr_min_price
        self.description = self.item_id.display_name
        self.sale_type = 'FOC' if self.item_id.foc else None

    @api.onchange('qty', 'item_id')
    def _calculate_gross(self):
        self.gross = float(self.rate * self.qty)

    @api.depends('sale_type', 'item_id', 'gross')
    def _net_value(self):
        for rec in self:
            if not rec.sale_type:
                rec.net_value = float(rec.gross)
            else:
                rec.discount_on_foc = -rec.gross
                rec.net_value = None

    @api.onchange('rate')
    def _calculate_gross_rate(self):
        self.gross = float(self.rate * self.qty)






# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import fields, models, api


class Stocks(models.Model):
    _inherit = "stock.move"
    _description = "Transfer"

    items_id = fields.Many2one('product.product',string="Items")
    serial_no = fields.Integer(string="Sl no")
    link_1 = fields.Char(string="Link-1")

    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                record.product_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                record.product_id = product.id
                record.items_id.display_name = product.display_name


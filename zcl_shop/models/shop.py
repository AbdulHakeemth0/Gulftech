# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import models,fields, api, _
from odoo.exceptions import ValidationError


class LocationInherits(models.Model):
    _inherit = "stock.location"
    _description = "Shop"

    tax_card_no = fields.Char(string="Tax Card No")
    vat_no = fields.Char(string="VATIN")

    @api.onchange('name')
    def _onchange_name(self):
        self.shop_location = True

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            shop = self.search([('shop_location','=',True)])
            for rec in shop:
                if self.branch_id.id == rec.branch_id.id:
                    raise ValidationError("Branch must be unique for each shop")



    def write(self, vals):
        recordset = self.env['stock.location'].search([('id', '!=', False)], limit=1, order="id desc")
        previous_id = recordset.ids[0]
        # if self.shop_location:
        if 'shop_location' in vals:
            existing_walk_in_customer = self.env['res.partner'].search([('branch_id','=',vals.get('branch_id'))])
            if not existing_walk_in_customer:
                customer_vals = {
                    'name': 'Walk-in Customer',
                    'id_card': 000,
                    'phone': 000,
                    'customer_true': True,
                    'walkin_customer': True,
                    'is_shop_customer': True,
                    'branch_id': vals.get('branch_id'),
                    'shop_id': int(previous_id+1),
                }
                customer = self.env['res.partner'].create(customer_vals)
                self.invalidate_model(['warehouse_id'])
        return super(LocationInherits, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('zcl_shop.sequence_shop') or _('New')
        res = super(LocationInherits, self).create(vals)
        return res

    def oh_hand_stock(self):
        return {
            'name': 'Store Stock',
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'domain': [('location_id.id', '=', self.id)],
            'res_id': self.id,
            # 'view_id': self.env.ref('zcl_shop.action_store_product_stock_form').id,
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }


class StockInherits(models.Model):
    _inherit = "stock.quant"

    @api.model
    def shop_store_stock_in_hand(self):
        return {
            'name': 'Stock in hand',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'tree',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('stock.view_stock_quant_tree')}),
            ],
            'domain': [('location_id', '=', self.env.user.branch_l_id.id)],

        }

# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Anoop Jayaprakash
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LocationInherits(models.Model):
    _inherit = "stock.location"
    _description = "Shop"
    # _rec_name = 'name'

    def action_view_all_shop_stock_products(self):
        return {
            'name': 'Products',
            'view_mode': 'Kanban',
            'res_model': 'stock.quant',
            'res_id': self.id,
            'view_id': self.env.ref('store.action_shop_product').id,
            'type': 'ir.actions.act_window',
            'domain': [('location_id', '=', self.id)],
        }


class WarehouseInherits(models.Model):
    _inherit = "stock.warehouse"
    _description = "warehouse"
    _rec_name = 'name'

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('zcl_store.sequence_store') or _('New')
        res = super(WarehouseInherits, self).create(vals)
        return res

    def update_warehouse_stock(self):
        for rec in self.search([('store_warehouse','=',False)]):
            rec.lot_stock_id.name = rec.name

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            store = self.search([('store_warehouse', '=', False)])
            for rec in store:
                if self.branch_id.id == rec.branch_id.id:
                    raise ValidationError("Branch must be unique for each shop")

    def store_stock(self):
        if self.env['stock.location'].search([('warehouse_id', '=', int(self.id)), ('usage', '=', 'internal')], limit=1).ids:
            return {
                'name': 'Stocks',
                'view_mode': 'tree',
                'res_model': 'stock.quant',
                'res_id': self.id,
                'view_id': self.env.ref('zcl_store.view_store_stock_quant_tree_inventory_editable').id,
                'type': 'ir.actions.act_window',
                'domain': [('location_id', '=', self.env['stock.location'].search([('warehouse_id', '=', int(self.id)), ('usage', '=', 'internal')], limit=1).ids)],
                'context': {'default_location_id': self.env['stock.location'].search([('warehouse_id', '=', int(self.id)), ('usage', '=', 'internal')], limit=1).id}
            }

    def shop_stock(self):
        return {
            'name': 'Shop Stocks',
            'view_mode': 'kanban',
            'res_model': 'stock.location',
            'res_id': self.id,
            'view_id': self.env.ref('zcl_store.view_all_shop_kanban').id,
            'type': 'ir.actions.act_window',
            'domain': [('shop_identify', '=', True)],
        }

class StockMovesInherits(models.Model):
    _inherit = "stock.move"

    customer_name = fields.Char(related='picking_id.partner_id.name', string="Customer")

    onhand_qty = fields.Float(
            string='On Hand Quantity',
            compute='_compute_onhand_quantity'
    )

    @api.depends('location_id','product_id.qty_available')
    def _compute_onhand_quantity(self):
        for move in self:
            quant = self.env['stock.quant'].search([
                ('location_id', '=', move.location_id.id),
                ('product_id', '=', move.product_id.id)
            ])
            move.onhand_qty = sum(quant.mapped('quantity'))

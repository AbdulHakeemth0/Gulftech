# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import api, fields, models, _


class MaterialRequest(models.Model):
    _inherit = "stock.move"
    _description = "Damage stock"
    # _order = 'id desc'

    damage_stock_id = fields.Many2one('damage.stock', string="damage stock Out")
    damage_stock_state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed'), ('approve', 'Approved'), ('reject', 'Rejected'), ('completed', 'Done')], compute='_compute_damage_stock_state', store=True)
    pending_qty = fields.Float(string='Pending quantity', compute='_compute_pending_qty', store=True)

    @api.depends('damage_stock_id.state')
    def _compute_damage_stock_state(self):
        for move in self:
            move.damage_stock_state = move.damage_stock_id.state if move.damage_stock_id else False

    @api.depends('damage_stock_state')
    def _compute_pending_qty(self):
        for move in self:
            if move.damage_stock_state == 'completed':
                move.pending_qty = float(move.product_uom_qty - move.quantity_done)
            else:
                move.pending_qty = 0

    # SHOP WISE Damage stock out report view
    @api.model
    def damage_stock_out_report_shop(self):
        domain = [
            ('damage_stock_state', 'in', ('done', 'approve', 'reject', 'completed')),
            ('branch_id', 'in', self.env.user.branch_ids.ids),
        ]
        action = {
            'name': 'Damage Stock Out Report',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree',
            'view_id': self.env.ref('zcl_damage_stock.damage_stock_in_view_tree_store_report').id,
            'domain': domain,
        }
        return action
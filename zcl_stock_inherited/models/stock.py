# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models

from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
import calendar



class LocationInherits(models.Model):
    _inherit = "stock.location"
    _description = "Shop"
    _rec_name = 'name'

    name = fields.Char('Shop Name', required=True)
    shop_location = fields.Boolean(default=False, store=True)
    reference = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))


class WarehouseInherits(models.Model):
    _inherit = "stock.warehouse"
    _description = "warehouse"
    _rec_name = 'name'

    reference = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))
    name = fields.Char('Store', required=True, default="")
    code = fields.Char('Short Name', required=True, size=5, help="Short name used to identify your store")
    store_warehouse = fields.Boolean(default=False)


class StockMove(models.Model):
    _inherit = 'stock.move'

    customer_id = fields.Many2one('res.partner',related='picking_id.partner_id',string="Customer")
    narration = fields.Html(related='picking_id.note', string="Narration")
    remarks = fields.Text(string="Remarks")
    req_qty = fields.Float(string="Requested Quantity")
    send_qty = fields.Float(string="Sending Quantity")
    pending_qty = fields.Float(string="Pending Quantity", compute="_check_pending_qty",store=True)

    shopreq_narration = fields.Html(string="Narration", compute="_compute_shopreq_narration")

    reserved_availability = fields.Float(
        'Quantity Reserved', compute='_compute_reserved_availability',
        digits='Product Unit of Measure',
        readonly=False,
        store=True,
        help='Quantity that has already been reserved for this move')

    @api.onchange('product_uom_qty')
    def onchange_product_qty(self):
        if self.picking_id.direct_transfer:
            self.send_qty = self.product_uom_qty


    @api.depends('reference')
    def _compute_shopreq_narration(self):
        for move in self:
            if move.reference:
                related_picking = self.env['stock.picking'].search([('name', '=', move.reference)], limit=1)
                if related_picking:
                    move.shopreq_narration = related_picking.narration

    @api.depends('quantity_done','send_qty','state')
    def _check_pending_qty(self):
        for rec in self:
            if rec.state == 'draft':
                rec.pending_qty = abs(rec.req_qty - rec.send_qty)
            else:
                if rec.picking_id.direct_transfer:
                    rec.pending_qty = abs(rec.quantity_done - rec.send_qty)
                else:
                    rec.pending_qty = abs(rec.send_qty - rec.req_qty)

    on_hand_qty = fields.Float(string="OnHand Qty", compute="_compute_onhand", store=True)

    @api.depends('location_id','product_id.qty_available')
    def _compute_onhand(self):
        for rec in self:
            stock_quants = self.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.location_id.id),
            ])
            total_stock = sum(quant.quantity for quant in stock_quants)
            rec.on_hand_qty = total_stock


class StockQuant(models.Model):
    _inherit = "stock.quant"

    location_count_ids = fields.One2many('location.count.history','history_id')
    sale_quantity = fields.Float(string="Sale Quantity")
    unit_price = fields.Float(related='product_id.standard_price', string="Unit Price", store=True)

    def auto_location_history(self):
        today = fields.date.today()
        first_day = today.replace(day=1)
        last_day = first_day.replace(day=calendar.monthrange(today.year, today.month)[1])
        for rec in self.search([]):
            if today.day == 1:
                history = self.env['location.count.history'].create({'date': today, 'count': rec.quantity, 'history_id': rec.id, 'location_id': rec.location_id.id, 'product_id': rec.product_id.id})
            qty = 0
            sales = self.env['sale.order'].search(
                ['|', ('normal_do', '=', True), ('cash_memo', '=', True), ('state', '=', 'sale'),
                 ('create_date', '>=', first_day), ('create_date', '<=', last_day),
                 ('branch_id', '=', rec.location_id.branch_id.id)])
            for sale in sales:
                for res in sale.order_line:
                    if res.product_id.id == rec.product_id.id:
                        qty += res.product_uom_qty
            rec.sale_quantity = qty
            current_month = self.env['location.count.history'].search([('date','=',first_day),('history_id','=', rec.id)])
            if current_month:
                current_month.sale_quantity = qty
            if current_month.sale_quantity:
                current_month.moving_percentage = (current_month.sale_quantity / current_month.count) * 100

class LocationCountHistory(models.Model):
    _name = "location.count.history"
    # _order = 'CASE WHEN moving_percentage = 0 THEN 1 ELSE 0 END, moving_percentage DESC'

    date = fields.Date(string="Date")
    count = fields.Float(string="Count")
    sale_quantity = fields.Float(string="Sale Quantity")
    moving_percentage = fields.Float(string="Percentage")
    history_id = fields.Many2one('stock.quant')
    location_id = fields.Many2one('stock.location')
    product_id = fields.Many2one('product.product')

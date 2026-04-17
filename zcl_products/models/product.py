# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Syooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"
    # _sql_constraints = [('default_code', 'unique(default_code)', 'Product Code must be unique!')]

    product_alias = fields.Char(string='Alias')
    product_arabic_name = fields.Char(string='Arabic Name')
    # branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True, readonly=True)
    product_type = fields.Selection([('finished_good', 'Finished Good'), ('raw_material', 'Raw Material')],
                                    string="Product Type", required=True)
    reorder_level = fields.Float(string='Reorder Level')
    bin_capacity = fields.Integer(string='Bin Capacity')
    valuation_method = fields.Selection(
        [('wt_average', 'Wt Average'), ('lifo', 'LIFO'), ('fifo', 'FIFO'), ('fifo_time', 'FIFO (Consider Tr. Time)')],
        default='wt_average')
    brand = fields.Char(string='Brand')
    warranty = fields.Integer(string='Warranty')
    division_group = fields.Char(string='Division Group')
    item_sub_group = fields.Char(string='Item Sub Group')
    markup = fields.Char(string='Markup %')
    foc = fields.Boolean(string='Foc')
    vendor = fields.Many2one('res.partner', string='Vendor', domain=[('vendor_true', '=', True)])
    country_of_origin_id = fields.Many2one('res.country', 'Country of Origin')
    alternative = fields.Char(string='Alternative 1')
    item_group = fields.Char(string='Item Group')
    item_category = fields.Char(string='Item Category')
    brand_new = fields.Char(string='Brand New')
    movement = fields.Selection([
        ('fast', 'Fast'),
        ('slow', 'Slow'),
        ('medium', 'Medium'),
    ], string="Movement")
    grade = fields.Char(string='Grade')
    item_type = fields.Char(string='Item Type')
    with_effect_from = fields.Date(string='With effect from')
    cntr_max_price = fields.Float(string='Cntr Max Price', digits=(12, 3))
    rate_definition = fields.Selection([('over_all_selling_rate', 'Over all Selling rate'), ('branch', 'Branch')],
                                       default='over_all_selling_rate', string='Rates Definition')
    minimal_selling_price = fields.Float(string="Minimal Selling Price", digits=(12, 3))
    cntr_min_price = fields.Float(string='Cntr Min Price', digits=(12, 3))
    traders_price = fields.Float(string='Traders Price', digits=(12, 3))
    dealer_price = fields.Float(string='Dealer', digits=(12, 3))
    discount = fields.Float(string='Discount', digits=(12, 3))
    project_price = fields.Float(string='Project Price', digits=(12, 3))
    wholesale = fields.Float(string='Wholesale', digits=(12, 3))
    basic_unit = fields.Selection([('no', 'NO'), ('yes', 'YES')], default='no', tracking=True)
    related_units_ids = fields.One2many('unit.line', 'unit_model_id', string='Related Units')
    related_reorders_ids = fields.One2many('reorder.line', 'main_model_id', string='Related Reorders')
    cash_sale_count = fields.Float(string="Cash Sale Count")
    cash_sale_price = fields.Float(string="Cash Sale Price", digits=(12, 3))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed')],
                             string='Status', default='draft', required=True)
    purchase_uom = fields.Many2one('uom.uom', string="Purchase Unit Of Measure")
    sale_uom = fields.Many2one('uom.uom', string="Sale Unit Of Measure")

    # purchase_rates = fields.Float(string="Purchase Rate")
    min_rates = fields.Float(string="Minimum Rate")
    least_rates = fields.Float(string="Least Rate")
    last_rates = fields.Float(string="Last Rate")
    product_loc_ids = fields.One2many('product.count.line','product_loc_id', compute="_compute_location_count", string="Locations", store=True)
    default_code = fields.Char(index=True, required=True)
    django_id = fields.Integer(string="Django ID")

    # def get_all_location(self):
    #     print("hihihii")
    #     for rec in self:
    #         stock_list = []
    #         location = self.env['stock.location'].search([])
    #         print(rec.id,"reccccccccccccccccc")
    #         for loc in location:
    #             stock_quants = self.env['stock.quant'].search([('product_id', '=', rec._origin.id),('location_id', '=', loc.id),])
    #             print(stock_quants,"ddddddddddddd")
    #             total_stock = sum(quant.quantity for quant in stock_quants)
    #             # if rec.product_loc_ids:
    #             #     for res in rec.product_loc_ids:
    #                     # if loc not in res.location_id:
    #             stock_list = [{'location_id': loc.id,'quantity': total_stock}]
    #                         # self.env['product.count.line'].create({'location_id': loc.id,
    #                         #                                        'quantity': total_stock,
    #                         #                                        'product_loc_id': rec.id})
    #
    #         return {
    #             'name': 'Material',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'product.product',
    #             'view_mode': 'form',
    #             'view_id': self.env.ref('zcl_products.zcl_product_count_view').id,
    #             'target': "new",
    #             "context":{'default_product_loc_ids': stock_list}
    #         }

    @api.depends('qty_available', 'name')
    def _compute_location_count(self):
        for rec in self:
            rec.product_loc_ids = [(5, 0, 0)]
            stock_list = []
            location = self.env['stock.location'].search([])
            for loc in location:
                if loc.warehouse_id.store_warehouse or loc.shop_location or loc.scrap_location or loc.return_location:
                    stock_quants = self.env['stock.quant'].search(
                        [('product_id', '=', rec.id), ('location_id', '=', loc.id)])
                    total_stock = sum(quant.quantity for quant in stock_quants)
                    stock_list.append((0, 0, {
                        'location_id': loc.id,
                        'quantity': total_stock
                    }))
            rec.product_loc_ids = stock_list
    def get_all_location(self):
        stock_list = []
        for rec in self:
            location = self.env['stock.location'].search([])
            for loc in location:
                if loc.warehouse_id.store_warehouse or loc.shop_location or loc.scrap_location or loc.return_location:
                    stock_quants = self.env['stock.quant'].search(
                        [('product_id', '=', rec._origin.id), ('location_id', '=', loc.id)])
                    total_stock = sum(quant.quantity for quant in stock_quants)
                    stock_list.append({'location_id': loc.id, 'quantity': total_stock})

        return {
            'name': 'Material',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'form',
            'view_id': self.env.ref('zcl_products.zcl_product_count_view').id,
            'target': 'new',
            'context': {'default_product_loc_ids': stock_list}
        }

    def action_confirm(self):
        self.state = 'done'

    @api.onchange('minimal_selling_price', 'cntr_min_price')
    def onchange_minimal_selling_price(self):
        if self.minimal_selling_price > self.cntr_max_price:
            raise ValidationError("Minimal selling price must be less than Cntr Max Price:" + str(self.cntr_max_price))
        if self.cntr_min_price > self.cntr_max_price:
            raise ValidationError("Cntr Min Price must be less than Cntr Max Price:" + str(self.cntr_max_price))


class Unit(models.Model):
    _name = "unit.line"

    unit_model_id = fields.Many2one('product.product')
    unit = fields.Selection([('length', 'Length'), ('meter', 'Meter'), ('centimeter', 'Centimeter')])
    conversion = fields.Float(string='Conversion', digits=(12, 6))


class Reorder(models.Model):
    _name = "reorder.line"

    main_model_id = fields.Many2one('product.product')
    branch = fields.Char(string='Branch')
    reorder = fields.Char(string='Reorder')
    reorder_2 = fields.Char(string='Reorder2')
    lead_time = fields.Float(string='Lead Time')


class ProductCountLine(models.Model):
    _name = "product.count.line"
    _description = "model for showing location details"

    location_id = fields.Many2one('stock.location', string="Location")
    quantity = fields.Float(string="Quantity")
    sales_count = fields.Float(string="Sales count")
    product_loc_id = fields.Many2one('product.product')
    item_mov_id = fields.Many2one('item.movement')
    product_code = fields.Char(string="Product Code")
    unit_price = fields.Float(string="Unit Price")


class ItemMovement(models.Model):
    _name = 'item.movement'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product",required=True)
    item_movement_ids = fields.One2many('product.count.line','item_mov_id',string="Item Movement")

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            today = fields.date.today()
            first_day = today.replace(day=1)
            stock_list = []
            if self.item_movement_ids:
                self.write({'item_movement_ids': [[5, 0, 0]]})
            location = self.env['stock.location'].search([])
            for loc in location:
                if loc.warehouse_id.store_warehouse or loc.shop_location or loc.scrap_location or loc.return_location:
                    stock_quants = self.env['stock.quant'].search(
                        [('product_id', '=', self.product_id.id), ('location_id', '=', loc.id)])
                    total_stock = sum(quant.quantity for quant in stock_quants)

                    sale_count =  self.env['stock.move'].search(
                        [('product_id', '=', self.product_id.id), ('location_id', '=', loc.id),('location_dest_id.name', '=', 'Customers'),('state','=','done'), ('date','>=',first_day)])
                    total_sales = sum(quant.product_uom_qty for quant in sale_count)
                    self.write({'item_movement_ids': [fields.Command.create({'product_code': self.product_id.default_code,'unit_price': self.product_id.cntr_max_price,
                        'location_id': loc.id,'quantity': total_stock, 'sales_count': total_sales,
                    })],})
        else:
            self.write({'item_movement_ids': [[5, 0, 0]]})

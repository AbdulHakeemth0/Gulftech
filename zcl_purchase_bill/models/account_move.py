# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Sayooj T K
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from odoo import fields, models,api,_


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_import = fields.Boolean(string="Purchase Import")
    purchase_local = fields.Boolean(string="Purchase Local")
    project_do = fields.Boolean(string="Project DO")
    vendor_bill_ids = fields.One2many('bill.lines', 'bill_lines_id', string='Vendor', store=True)
    sub_total = fields.Float(string="Sub Total", compute='compute_total_amount', store=True, digits=(16, 3))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user
            if vals.get('purchase_local') == True:
                if user.branch_id.pv_local_prefix:
                    prefix = self.env['ir.sequence'].search([('code', '=', user.branch_id.pv_local_prefix)],limit=1)
                    if prefix:
                        vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
            elif vals.get('purchase_import') == True:
                if user.branch_id.pv_import_prefix:
                    prefix = self.env['ir.sequence'].search([('code', '=', user.branch_id.pv_import_prefix)],limit=1)
                    if prefix:
                        vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
            elif vals.get('move_type'):
                print("555555555555555")
                if user.branch_id.journal_entry_prefix:
                    prefix = self.env['ir.sequence'].search(
                        [('code', '=', user.branch_id.journal_entry_prefix)], limit=1)
                    if prefix:
                        vals['document_no'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
                        vals['name'] = vals['document_no']


        else:
                print("ok")
        return super().create(vals_list)

    @api.depends('vendor_bill_ids.check_box')
    def compute_total_amount(self):
        for rec in self:
            total_sum = 0
            for res in rec.vendor_bill_ids:
                if res.check_box:
                    total_sum += res.amount_total
                    rec.sub_total = total_sum


    @api.onchange('partner_id')
    def _onchange_partner_ids(self):
        """ create lines base on selected vendor purchase orders """
        for data in self:
            if data.partner_id:
                if data.purchase_local == True:
                    rec = self.env['purchase.order'].sudo().search(
                        [('partner_id.id', '=', data.partner_id.id), ('state', '=', 'purchase'), ('purchase_local', '=', True), ('purchase_invoiced', '=', False) ])
                    if rec:
                        for res in rec:
                            if res.total_billed_qty < res.total_qty:
                                if not res.total_billed_qty == res.total_received_qty:
                                    print(res.id)
                                    data.vendor_bill_ids = [fields.Command.create({'order_id': res.id,})]
                    else:
                        for rec in data.vendor_bill_ids:
                            rec.unlink()
                if data.purchase_import == True:
                    rec = self.env['purchase.order'].sudo().search(
                        [('partner_id.id', '=', data.partner_id.id), ('state', '=', 'purchase'), ('purchase_import', '=', True), ('purchase_invoiced', '=', False) ])
                    if rec:
                        for res in rec:
                            if res.total_billed_qty < res.total_qty:
                                if not res.total_billed_qty == res.total_received_qty:
                                    print(res.id)
                                    data.vendor_bill_ids = [fields.Command.create({'order_id': res.id,})]
                    else:
                        for rec in data.vendor_bill_ids:
                            rec.unlink()

    def action_create_bill(self):
        """ remove unchecked lines and create invoice lines based
        on the checked purchase order and send post stage
        """
        for data in self:
            # if data.purchase_local:
            lst = []
            invoice_lines_to_delete = [rec.id for rec in data.vendor_bill_ids if not rec.check_box]
            data.vendor_bill_ids.filtered(lambda rec: rec.id in invoice_lines_to_delete).unlink()

            for rec in data.vendor_bill_ids:
                for line in rec.order_id.order_line:
                    qty_to_invoice = line.qty_received - line.qty_invoiced
                    if qty_to_invoice > 0:
                        values = {
                            'product_id': line.product_id.id,
                            'quantity': qty_to_invoice,
                            'price_unit': line.price_unit,
                            'move_id': data.id,
                        }
                        self.env['account.move.line'].create(values)
                        line.qty_invoiced += qty_to_invoice
                        total_product_qty = sum(lines.product_qty for lines in rec.order_id.order_line)
                        total_billed = sum(lines.qty_invoiced for lines in rec.order_id.order_line)
                        if total_billed == total_product_qty:
                            rec.order_id.purchase_invoiced = True
            data.action_post()



class VendorBillLines(models.Model):
    _name = 'bill.lines'

    check_box = fields.Boolean(string="    ")
    bill_lines_id = fields.Many2one('account.move')
    order_id = fields.Many2one('purchase.order', )
    partner_id = fields.Many2one('res.partner', string='Vendor', related='order_id.partner_id')
    # sales_man_id = fields.Many2one('res.partner', string='Sales Man', related='order_id.salesman_id')
    date_order = fields.Datetime(string='Current Date', related='order_id.create_date')
    amount_total = fields.Float(string='Total', digits=(16, 3), compute='_total_amount', store=True )

    @api.depends('order_id')
    def _total_amount(self):
        for rec in self:
            if rec.order_id:
                amount_totals = 0.0
                for res in rec.order_id.order_line:
                    if not res.product_qty == res.qty_invoiced:
                        if res.price_unit:
                            amount_totals += float((res.qty_received - res.qty_invoiced) * res.price_unit)
                rec.amount_total = amount_totals
            else:
                pass

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    items_id = fields.Many2one('product.product', string="Items", store=True)

    # onchange for display the product that selected in 'items_id(A many2one field which list the product as default code only)' field
    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                record.product_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                record.product_id = product.id
                record.product_id.display_name = product.display_name



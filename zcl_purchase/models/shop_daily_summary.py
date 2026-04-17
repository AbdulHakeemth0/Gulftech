# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Manjima V
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################


from odoo import api, fields, models, _
from datetime import datetime, time



class ShopSummary(models.Model):
    _name = 'shop.summary'
    _description = "Daily Shop Summary"
    _rec_name = "shops_name_id"

    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id, readonly=True)
    shops_name_id = fields.Many2one('stock.location', string="Shop Name", domain="[('shop_location','=',True)]")
    date = fields.Date(String="Date", default=fields.Date.today, readonly=True)
    cash_memo_summary_ids = fields. Many2many('sale.order','relation_table_cash_memo')
    internal_do_summary_ids = fields.Many2many('sale.order', 'relation_table_internal_do')
    project_do_summary_ids = fields.Many2many('sale.order','relation_table_project_do')
    direct_order_summary_ids = fields.Many2many('sale.order','relation_table_direct_order')
    return_order_summary_ids = fields.Many2many('sale.order','relation_table_return_order')
    cash_sale_summary_ids = fields.Many2many('sale.order','relation_table_cas_sale')
    whole_sale_summary_ids = fields.Many2many('sale.order','relation_table_wholesale_sale')
    cash_memo_return_ids = fields.Many2many('sale.order','relation_table_cashmemo_returns')
    purchase_voucher_import_ids = fields.Many2many('purchase.order','relation_purchase_voucher_import')
    purchase_voucher_local_ids = fields.Many2many('purchase.order','relation_purchase_voucher_local')
    cash_purchase_ids = fields.Many2many('purchase.order','relation_cash_purchase')
    bank_receipts_ids = fields.Many2many('bank.receipt')
    cash_receipts_ids = fields.Many2many('cash.receipt')
    pdc_receipts_ids = fields.Many2many('pdc.management')
    company_currency_id = fields.Many2one(comodel_name='res.currency',
                                          default=lambda self: self.env.company.currency_id.id,
                                          string='Company Currency')
    total_cash_purchase = fields.Monetary(currency_field='company_currency_id', string="Cash Purchase Amount")
    total_cash_memo_return = fields.Monetary(currency_field='company_currency_id', string="Cash Memo Return")
    total_wholesale_sale = fields.Monetary(currency_field='company_currency_id', string="Wholesale Sale Amount")
    total_cash_memo = fields.Monetary(currency_field='company_currency_id', string="Cash Memo Amount")
    total_receipt_voucher = fields.Monetary(currency_field='company_currency_id', string="Receipt Voucher Amount")
    total_purchase_voucher_local = fields.Monetary(currency_field='company_currency_id', string="Purchase Voucher Local Amount")
    total_purchase_voucher_import = fields.Monetary(currency_field='company_currency_id', string="Purchase Voucher Import Amount")

    @api.onchange('shops_name_id')
    def _onchange_shops_name_id(self):
        min_time = datetime.combine(self.date, time.min)
        max_time = datetime.combine(self.date, time.max)

        project_do = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('project_direct_order','=', True),('state','=','sale')]).ids
        if project_do:
            self.project_do_summary_ids = project_do
        else:
            self.project_do_summary_ids = False

        direct_order = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('normal_do','=', True),('state','=','sale')]).ids
        if direct_order:
            self.direct_order_summary_ids = direct_order
        else:
            self.direct_order_summary_ids = False

        return_order = self.env['sale.order'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('date', '=', self.date), ('gt_sale_return', '=', True),
             ('state', '=', 'return')])
        if return_order:
            self.return_order_summary_ids = return_order.ids
        else:
            self.return_order_summary_ids = False

        cash_sale = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name), ('date', '=', self.date),('cash_sale','=', True),('state','=','sale')]).ids
        if cash_sale:
            self.cash_sale_summary_ids = cash_sale
        else:
            self.cash_sale_summary_ids = False

        cash_receipt = self.env['cash.receipt'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id), ('create_date', '=', self.date),('state', '=', 'done')]).ids
        if cash_receipt:
            self.cash_receipts_ids = cash_receipt
        else:
            self.cash_receipts_ids = False
        bank_receipt = self.env['bank.receipt'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id), ('create_date', '>=', min_time),
             ('create_date', '<=', max_time),('state', '=', 'done')]).ids
        if bank_receipt:
            self.bank_receipts_ids = bank_receipt
        else:
            self.bank_receipts_ids = False
        pdc_receipt = self.env['pdc.management'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('date', '=', self.date),('state','=','done')]).ids
        if pdc_receipt:
            self.pdc_receipts_ids = pdc_receipt
        else:
            self.pdc_receipts_ids = False
        cash_purchase = self.env['purchase.order'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),('create_date', '>=', min_time),
             ('create_date', '<=', max_time),('shop_purchase', '=', True), ('state','=','purchase')])
        if cash_purchase:
            self.cash_purchase_ids = cash_purchase.ids
            total_cp = 0
            for rec in cash_purchase:
                total_cp += rec.amount_total
            self.total_cash_purchase = total_cp
        wholesale_order = self.env['sale.order'].search(
            [('branch_id.name', '=', self.shops_name_id.branch_id.name),
             ('date', '=', self.date), ('warehouse_sale', '=', True),
             ('state', '=', 'sale')])

        if wholesale_order:
            wh_sale = 0
            for rec in wholesale_order:
                wh_sale += rec.amount_total
            self.total_wholesale_sale = wh_sale
            self.whole_sale_summary_ids = wholesale_order.ids
        else:
            self.whole_sale_summary_ids = False
        cash_memo_return = self.env['sale.order'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('create_date', '>=', min_time),
             ('create_date', '<=', max_time),('gt_cash_memo_return', '=', True), ('state', '=', 'return')])
        if cash_memo_return:
            self.cash_memo_return_ids = cash_memo_return.ids
            total_cmr = 0
            for rec in cash_memo_return:
                total_cmr += rec.amount_total
            self.total_cash_memo_return = total_cmr
        cash_memo = self.env['sale.order'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('create_date', '>=', min_time),
             ('create_date', '<=', max_time),
             ('cash_memo', '=', True), ('state', '=', 'sale')])
        if cash_memo:
            self.cash_memo_summary_ids = cash_memo.ids
            total_cm = 0
            for rec in cash_memo:
                total_cm += rec.amount_total
            self.total_cash_memo = total_cm
        receipt_voucher = self.env['cash.receipt'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('create_date', '=', self.date),('state', '=', 'done')])
        if receipt_voucher:
            total_rv = 0
            for rec in receipt_voucher:
                total_rv += rec.net
            self.total_receipt_voucher = total_rv
        purchase_voucher_local = self.env['account.move'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('create_date', '>=', min_time),
             ('create_date', '<=', max_time),
             ('purchase_local', '=', True), ('state', '=', 'posted')])
        if purchase_voucher_local:
            total_pvl = 0
            for rec in purchase_voucher_local:
                total_pvl += rec.amount_total
            self.total_purchase_voucher_local = total_pvl

        purchase_voucher_import = self.env['account.move'].search(
            [('branch_id.id', '=', self.shops_name_id.branch_id.id),
             ('create_date', '>=', min_time),
             ('create_date', '<=', max_time), ('purchase_import', '=', True),
             ('state', '=', 'posted')])
        if purchase_voucher_import:
            total_pvi = 0
            for rec in purchase_voucher_local:
                total_pvi += rec.amount_total
            self.total_purchase_voucher_import = total_pvi

# -*- coding: utf-8 -*-
###################################################################################

# Author       :  Abin Suresh
# Copyright(c) :  2023-Present Zinfog Codelabs Pvt Ltd (<https://www.zinfog.com>).
# License      :  LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# This program is free software:
# you can modify it under the terms of the GNU Lesser General Public License (LGPL) as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

###################################################################################

from datetime import date, timedelta
import calendar
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SalesmanIncentive(models.Model):
    _name = 'salesman.incentive'
    _description = "Incentive"
    _rec_name = "name"
    _order = 'id desc'


    sequence = fields.Char(string="Number" )
    name = fields.Char(string="Name", required=True)
    branch_id = fields.Many2one('res.branch', string='Branch',
                                default=lambda self: self.env.user.branch_id.id)
    amount = fields.Float(string="Amount", required=True, digits=(16, 3))
    showroom_incharge = fields.Float(string="Showroom Incharge Amount", digits=(16, 3))
    assistant_amount = fields.Float(string="Assistant Amount", digits=(16, 3))
    salesman_amount = fields.Float(string="Salesman Amount", digits=(16, 3))
    amount_achieved = fields.Float(string="Amount Achieved", digits=(16, 3))
    current_date = fields.Date(string="Current Date", store=True)
    date_from = fields.Date(string="Date From", compute="_compute_dates", store=True,)
    date_to = fields.Date(string="Date To", compute="_compute_dates", store=True,)
    line_ids = fields.One2many('salesman.incentive.line', 'incentive_id')

    _sql_constraints = [
        ('name_uniq', 'unique (branch_id)', "Branch already exists !"),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user
            if user.branch_id.target_setting_prefix:
                prefix = self.env['ir.sequence'].search([('code', '=', user.branch_id.target_setting_prefix)], limit=1)
                if prefix:
                    vals['sequence'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
            else:
                print("ok")
        return super().create(vals_list)

    @api.depends('current_date', 'date_from')
    def _compute_dates(self):
        for rec in self:
            if rec.current_date:
                rec.date_from = rec.current_date.replace(day=1)
                last_day = calendar.monthrange(rec.current_date.year,
                                               rec.current_date.month)[1]
                rec.date_to = rec.current_date.replace(day=last_day)

    # Sales man wise incentive calculation
    # def action_compute_incentive(self):
    #     if self.branch_id:
    #         if self.date_from and self.date_to:
    #             total_sale_amt = 0
    #             total_payment_amt = 0
    #             sales = self.env['sale.order'].search(
    #                 [('state', '=', 'sale'), ('branch_id', '=', self.branch_id.id),
    #                  ('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)])
    #             print(sales, "sales")
    #             for rec in sales:
    #                 total_sale_amt += rec.amount_total
    #             payments = self.env['account.payment'].search(
    #                 [('partner_type', '=', 'customer'), ('branch_id', '=', self.branch_id.id), ('is_internal_transfer', '=', False),
    #                  ('state', '=', 'posted')])
    #             for rec in payments:
    #                 total_payment_amt += rec.amount_company_currency_signed
    #             if total_sale_amt > self.amount:
    #                 if total_payment_amt > self.amount:
    #                     self.amount_achieved = total_payment_amt
    #                     balance = total_payment_amt - self.amount
    #                     percentage_achieved = (balance / self.amount) * 100
    #                     if percentage_achieved > 10:
    #                         multiple = int(percentage_achieved / 10) + 1
    #                         self.showroom_incharge = self.showroom_incharge * multiple
    #                         self.assistant_amount = self.assistant_amount * multiple
    #                         self.salesman_amount = self.salesman_amount * multiple
    #                         salesman = self.env['res.partner'].search([('sales_man_true','=',True)])
    #                         for rec in salesman:
    #                             if rec.sales_man_type == 'showroom':
    #                                 rec.incentive_amount = self.showroom_incharge
    #                             elif rec.sales_man_type == 'assistant':
    #                                 rec.incentive_amount = self.assistant_amount
    #                             elif rec.sales_man_type == 'normal':
    #                                 rec.incentive_amount = self.salesman_amount
    #                             else:
    #                                 rec.incentive_amount = 0
    #                 else:
    #                     raise ValidationError('Total payment is less than incentive amount')
    #             else:
    #                 raise ValidationError('Total sale amount is less than incentive amount')
    def check_target_achievement(self):
        '''For calculate the target achieve check based on monthly with cash memo,cash sale
        and wholesale and its return and check the amount would be achieve and add the data
         to the lines'''
        for rec in self.search([]):
            last_day = date.today() - timedelta(days=1)
            final_day = calendar.monthrange(rec.current_date.year, last_day.month)[1]
            first_day = rec.current_date.replace(day=final_day)

            rec.current_date = last_day
            if rec.current_date:
                rec.date_from = rec.current_date.replace(day=1)
                last_day = calendar.monthrange(rec.current_date.year,
                                               rec.current_date.month)[1]
                rec.date_to = rec.current_date.replace(day=last_day)
            if rec.branch_id and rec.amount:

                sales = self.env['sale.order'].search(
                        ['|', ('cash_memo', '=', True), ('warehouse_sale', '=', True), ('state', '=', 'sale'),
                         ('branch_id.id', '=', rec.branch_id.id), ('create_date', '>=', rec.date_from),
                         ('create_date', '<=', rec.date_to)])

                cash_receipt = self.env['cash.receipt'].search(
                        [('state', '=', 'done'), ('branch_id.id', '=', rec.branch_id.id),
                         ('create_date', '>=', rec.date_from), ('create_date', '<=', rec.date_to)])

                sales_return = self.env['sale.order'].search(
                    [('gt_cash_memo_return', '=', True), ('state', '=', 'return'),
                     ('branch_id.id', '=', rec.branch_id.id), ('create_date', '>=', rec.date_from),
                     ('create_date', '<=', rec.date_to)])

                # Calculate Sale amounts
                amt = sum(amt.total_net for amt in sales)
                amt2 = sum(amt.net for amt in cash_receipt)

                # Calculate return amount
                return_amt = sum(amt.total_net for amt in sales_return)

                # Calculate Total amount with minus return amount
                sale_amount = (amt + amt2) - return_amt

                # Create line wise monthly
                dic = {
                    'month': rec.date_to.strftime('%B'),
                    'year': rec.date_to.strftime('%Y'),
                    'branch_id': rec.branch_id.id,
                    'amount': rec.amount,
                    'amount_achieved': sale_amount,
                    'status': 'done' if sale_amount >= rec.amount else 'fail',
                    'incentive_id': rec.id,
                }
                lines = self.env['salesman.incentive.line'].create([dic])


class SalesmanIncentiveLine(models.Model):
    _name = 'salesman.incentive.line'
    _description = "Incentive Line"
    _order = 'id desc'

    month = fields.Char(string="Month", store=True, required=True)
    year = fields.Char(string="Year", store=True, required=True)
    branch_id = fields.Many2one('res.branch', string='Branch')
    amount = fields.Float(string="Target Amount", required=True, digits=(16, 3))
    amount_achieved = fields.Float(string="Amount Achieved", digits=(16, 3))
    status = fields.Selection(string="Status", selection=[('done', 'Achieved'), ('fail', 'Not Achieved')], default='fail')
    incentive_id = fields.Many2one('salesman.incentive')




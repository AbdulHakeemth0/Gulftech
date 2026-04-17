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
from odoo.tests import Form


class PdcManagement(models.Model):
    _name = 'pdc.management'
    _description = "PDC Management"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="Document_no", readonly=True, default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('done', 'Confirmed'),], default='draft')
    cash_bank = fields.Many2one('account.journal', string="Cash/Bank", )
    branch = fields.Many2one('stock.location', string='Branch location', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_l_id, store=True)
    branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: self.env['res.users'].search([('id', '=', int(self.env.uid))], limit=1).branch_id, store=True, readonly=True)
    narration = fields.Char(string="Narration")
    cheque_name = fields.Char(string="Cheque Name")
    manual_no = fields.Char(string="Manual No")
    date = fields.Date(string="Date", default=fields.date.today())
    maturity_date = fields.Date(string="Maturity date")
    cheque_no = fields.Char(string="Cheque No")
    finance_status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('reject', 'Rejected')], default='pending', string='Finance status' )
    line_ids = fields.One2many('pdc.management.line', 'item_id', string='Line ids')
    net = fields.Float(string="Net",compute="_compute_net_amount",store=True)

    @api.depends('line_ids')
    def _compute_net_amount(self):
        for rec in self:
            sum = 0
            if rec.line_ids:
                for res in rec.line_ids:
                    sum += res.amount
            rec.net = sum

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user

            if user.branch_id.pdc_receipt_prefix:
                prefix = self.env['ir.sequence'].search([('code', '=', user.branch_id.pdc_receipt_prefix)], limit=1)
                print("prefix", prefix)
                if prefix:
                    vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
            else:
                print("ok")
        return super().create(vals_list)

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        sno = 1
        for line in self.line_ids:
            line.sno = sno
            sno += 1

    def action_confirm(self):
        self.state = 'done'

    def action_finance_approve(self):
        line_ids = None
        for rec in self.line_ids.reference:
            line_ids = rec.invoice_line_ids
        if self.line_ids:
            for rec in self.line_ids:
                if not rec.reference:
                    payment = self.env['account.payment'].create({
                        'payment_type': 'inbound',
                        'partner_id': rec.customer.id,
                        'amount': rec.amount,
                        'date': fields.Date.today()
                    })
                    if payment:
                        payment.action_post()
                else:
                    return_form = Form(self.env["account.payment.register"].sudo().with_context(
                        active_ids=rec.reference.ids,
                        active_model="account.move",
                        default_amount=rec.amount,
                    ))

                    return_wizard = return_form.save()
                    action = return_wizard._create_payments()

        self.finance_status = 'approved'
        for msg in self:
            body = _('The %s PDC Confirmed', self.name)
            msg.message_post(body=body)

    # def action_finance_approve(self):
    #     self.finance_status = 'approved'

    def action_finance_reject(self):
        self.finance_status = 'reject'

class PdcManagementLine(models.Model):
    _name = 'pdc.management.line'
    _description = "Pdc Management Line"

    item_id = fields.Many2one('pdc.management')
    sno = fields.Integer(string="Sno")
    customer = fields.Many2one('res.partner', string="Customer", domain="[('customer_true', '=', True)]")
    amount = fields.Float(string="Amount", digits=(16, 3))
    reference = fields.Many2one('account.move', string="Reference",
                                domain="[('partner_id', '=', customer), ('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid')]",
                                context={'default_partner_id': 'customer', 'state': 'posted', 'move_type': 'out_invoice'})
    remark = fields.Char(string="Remarks")


    @api.onchange('customer')
    def _onchange_customer(self):
        self.reference = False

    @api.model
    def create(self, values):
        record = super(PdcManagementLine, self).create(values)
        for rec in record.item_id:
            body = _('The line was created with amount %s for customer %s') % (record.amount, record.customer.name)
            rec.message_post(body=body)
        return record

    def write(self, values):
        result = super(PdcManagementLine, self).write(values)
        for record in self:
            for rec in record.item_id:
                body = _('The line was updated with amount %s for customer %s') % (record.amount, record.customer.name)
                rec.message_post(body=body)
        return result



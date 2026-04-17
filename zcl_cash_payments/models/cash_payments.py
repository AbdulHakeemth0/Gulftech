from odoo import api, fields, models, _
from odoo.exceptions import UserError



class CashPayments(models.Model):
    _name = 'cash.payments'
    _description = "Cash Payments"

    # domain = [('branch_id', 'in', self.env.user.branch_ids.ids)]

    name = fields.Char(string="Name", readonly=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string="Partner", required=True, domain=[('customer_true', '=', False)])
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Confirmed'), ('reject', 'Rejected')], default='draft', string="Status", tracking=True)
    payment_date = fields.Date(string="Date", default=fields.date.today())
    account_id = fields.Many2one('account.account', string="Account", domain="[('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card'))]" )
    payment_amount = fields.Monetary(string="Amount", required=True)
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id.id)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env.user

            if user.branch_id.cash_payment_prefix:
                prefix = self.env['ir.sequence'].search([('code', '=', user.branch_id.cash_payment_prefix)], limit=1)
                print("prefix", prefix)
                if prefix:
                    vals['name'] = self.env['ir.sequence'].next_by_code(prefix.code) or _('New')
            else:
                print("ok")
        return super().create(vals_list)

    def cash_payments_confirm(self):
        print("confirm")

        # Check if necessary fields are filled
        if not self.customer_id or not self.account_id or not self.payment_amount:
            raise UserError('Customer, Bank Account, and Payment Amount must be set.')

        # Create the journal entry (account.move)
        move_vals = {
            'journal_id': self.env['account.journal'].search([('type', '=', 'cash')], limit=1).id,
            'date': self.payment_date,
            'ref': 'Cash Payment for {}'.format(self.customer_id.name),
            'line_ids': [
                # Debit entry for the bank account
                (0, 0, {
                    'account_id': self.account_id.id,
                    'partner_id': self.customer_id.id,
                    'name': 'Cash Payment - Bank',
                    'debit': self.payment_amount,
                    'credit': 0.0,
                }),
                # Credit entry for the customer (receivable)
                (0, 0, {
                    'account_id': self.customer_id.property_account_receivable_id.id,
                    'partner_id': self.customer_id.id,
                    'name': 'Cash Payment - Partner',
                    'debit': 0.0,
                    'credit': self.payment_amount,
                }),
            ],
        }
        journal_entry = self.env['account.move'].create(move_vals)

        # Post the journal entry
        journal_entry.action_post()

        # Update state to 'done'
        self.state = 'done'
        return True

    def cash_payments_reject(self):
        # Find the related journal entry
        journal_entries = self.env['account.move'].search(
            [('ref', '=', 'Cash Payment for {}'.format(self.customer_id.name))])
        if not journal_entries:
            raise UserError('No related journal entry found.')

        # Cancel each related journal entry
        for entry in journal_entries:
            if entry.state != 'cancel':
                entry.button_cancel()

        # Update state of the cash payment to 'rejected' even if it's in 'done' state
        self.state = 'reject'
        return True


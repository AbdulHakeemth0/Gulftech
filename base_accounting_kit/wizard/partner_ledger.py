# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountPartnerLedger(models.TransientModel):
    _name = "account.report.partner.ledger"
    _inherit = "account.common.partner.report"
    _description = "Account Partner Ledger"


    name = fields.Char(string="Partner Ledger Report", default="Partner Ledger Report", required=True, translate=True)
    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')
    partners_id = fields.Many2one('res.partner',string='Partner')
    sub_company_id = fields.Many2one('sub.company', string="Sub Company")


    def _print_report(self, data):
        if self.sub_company_id:
            if not self.env['res.branch'].search(
                [('id', 'in', self.env.user.branch_ids.ids), ('sub_company_id', '=', self.sub_company_id.id)]):
                raise UserError(_("Their is no branch under the Sub company for logged user"))
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled,
                             'amount_currency': self.amount_currency})
        data['form'].update({'partner': self.partners_id.id})
        data['form'].update({'sub_company': self.sub_company_id.id if self.sub_company_id else False,'sub_company_name': self.sub_company_id.name if self.sub_company_id else False})
        return self.env.ref(
            'base_accounting_kit.action_report_partnerledger').report_action(
            self, data=data)

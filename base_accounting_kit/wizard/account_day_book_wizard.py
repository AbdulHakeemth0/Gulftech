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
from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError


class DayBookWizard(models.TransientModel):
    _name = 'account.day.book.report'
    _description = 'Account Day Book Report'

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.company)
    journal_ids = fields.Many2many('account.journal', string='Journals',
                                   required=True,
                                   default=lambda self: self.env[
                                       'account.journal'].search([]))
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')], string='Target Moves', required=True,
                                   default='posted')

    account_ids = fields.Many2many('account.account',
                                   'account_report_daybook_account_rel',
                                   'report_id', 'account_id',
                                   'Accounts')

    date_from = fields.Date(string='Start Date', default=date.today(),
                            required=True)
    date_to = fields.Date(string='End Date', default=date.today(),
                          required=True)
    sub_company_id = fields.Many2one('sub.company', string="Sub Company")

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form'][
            'journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form'][
            'target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    def check_report(self):
        self.ensure_one()
        if self.sub_company_id:
            if not self.env['res.branch'].search(
                [('id', 'in', self.env.user.branch_ids.ids), ('sub_company_id', '=', self.sub_company_id.id)]):
                raise UserError(_("Their is no branch under the Sub company for logged user"))
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = \
        self.read(['date_from', 'date_to', 'journal_ids', 'target_move',
                   'account_ids'])[0]
        data['form'].update({'sub_company': self.sub_company_id.id if self.sub_company_id else False})
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,
                                            lang=self.env.context.get(
                                                'lang') or 'en_US')
        return self.env.ref(
            'base_accounting_kit.day_book_pdf_report').report_action(self,
                                                                     data=data)

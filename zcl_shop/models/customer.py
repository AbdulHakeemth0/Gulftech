from odoo import models, api, _,fields


class ResPartnerInherits(models.Model):
    _inherit = "res.partner"
    _description = "customers"

    is_shop_customer = fields.Boolean(default=False, store=True)
    state = fields.Selection([('draft', 'Draft'),('approved','Approved'),('done', 'Confirmed')],
                             string='Status', default='draft', required=True)
    shop_id = fields.Integer(string='shop')
    incentive_amount = fields.Float(string="Incentive Amount")
    branch_id = fields.Many2one(string='Branch',
                                default=lambda self: self.env.user.branch_id.id)

    def action_confirm(self):
        self.state = 'done'



# SHOP WISE CUSTOMER VIEW ACTION
    @api.model
    def action_open_customers_window(self):
        """SHOP WISE CUSTOMER VIEW ACTION"""
        domain = [
            ('customer_true', '=', True),
            ('walkin_customer', '=', False),
            ('is_shop_customer', '=', True),
            ('branch_id', 'in', self.env.user.branch_ids.ids),
        ]

        action = {
            'name': 'Customers',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,form',
            'view_ids': [
                (5, 0, 0),
                (0, 0, {'view_mode': 'kanban', 'view_id': self.env.ref(
                    'zcl_shop.zcl_res_partner_kanban_view').id}),
                (0, 0, {'view_mode': 'form', 'view_id': self.env.ref(
                    'zcl_shop.view_zcl_partner_form').id}),
            ],
            'context': {'default_customer_true': True,
                        'default_is_shop_customer': True},
            'domain': domain,
        }
        return action

    # branch WISE salesman VIEW ACTION
    @api.model
    def salesman_menu_view(self):
        """branch WISE salesman VIEW ACTION"""
        domain = []
        if self.env.user.has_group('sales_team.group_sale_manager'):
            domain = [('sales_man_true', '=', True)]
        else:
            domain = [('sales_man_true', '=', True),
                      ('branch_id', 'in', self.env.user.branch_ids.ids)]
        action = {
            'name': 'Salesman',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'kanban,form',
            'view_id': False,
            'views': [(
                      self.env.ref('zcl_shop.zcl_res_sales_man_kanban_view').id,
                      'kanban'),
                      (self.env.ref('zcl_shop.view_zcl_sales_man_form').id,
                       'form')],
            'target': 'current',
            'context': {'default_sales_man_true': True},
            'domain': domain,
        }
        return action

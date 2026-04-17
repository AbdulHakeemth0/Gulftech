from odoo import fields, models, api, _


class MaterialRequest(models.Model):
    _inherit = "stock.picking"
    _description = "Material Request"

    shop_material_req_out = fields.Boolean(string="Shop Out")
    shop_mat_req = fields.Boolean(string="Shop Out")
    store_mat_req = fields.Boolean(string="Store Out")
    sale_order_no = fields.Char(string="Sale Order No")


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_order_no = fields.Char(string="Sale Order No",compute="_compute_sale_no",store=True)
    shop_mat_req = fields.Boolean(string="Shop Out")
    store_mat_req = fields.Boolean(string="Store Out")
    product_code = fields.Char(related='product_id.default_code',string="Code")


    @api.depends('reference')
    def _compute_sale_no(self):
        for rec in self:
            if rec.reference:
                picking= self.env['stock.picking'].search([('name', '=', rec.reference)])
                if picking.sale_order_no:
                    rec.sale_order_no = picking.sale_order_no
                if picking.shop_mat_req:
                    rec.shop_mat_req = True
                if picking.store_mat_req:
                    rec.store_mat_req = True


    # @api.model
    # def action_shop_mr_report(self):
    #     domain = [('shop_mat_req', '=', True),('state', '!=', 'draft')]
    #     action = {
    #         'name': 'MR IN',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'stock.move',
    #         'view_mode': 'tree',
    #         'view_ids': [
    #             (5, 0, 0),
    #             (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('zcl_material_request.mat_req_report_tree_view').id}),
    #         ],
    #         'domain': domain,
    #     }
    #     return action

    # @api.model
    # def action_store_mr_report(self):
    #     # domain = [('branch_id.id', '=', self.env.user.branch_id.id),
    #     #           ('picking_id.store_mat_req', '=', True), ('state', '=', 'draft')]
    #     domain = [('store_mat_req', '=', True), ('state', '=', 'draft')]
    #     action = {
    #         'name': 'MR OUT',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'stock.move',
    #         'view_mode': 'tree',
    #         'view_ids': [
    #             (5, 0, 0),
    #             (0, 0, {'view_mode': 'tree',
    #                     'view_id': self.env.ref('zcl_material_request.mat_req_report_tree_view').id}),
    #         ],
    #         'domain': domain,
    #     }
    #     return action

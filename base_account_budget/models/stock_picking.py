from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.http import request
from odoo.exceptions import ValidationError, UserError





class StockPicking(models.Model):
    _inherit = 'stock.picking'
    location = fields.Many2one(
        'stock.location', string='Location')
    # warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    # is_internal = fields.Boolean(string='Internal Transfer')

    # @api.depends('is_internal')
    # def _compute_picking_type_id(self):
    #     for record in self:
    #         if record.is_internal:
    #             internal_transfer_type = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
    #             if internal_transfer_type:
    #                 record.picking_type_id = internal_transfer_type
    #         else:
    #             record.picking_type_id = False

    # @api.onchange('is_internal')
    # def _onchange_is_internal(self):
    #     if self.is_internal:
    #         internal_transfer_type = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
    #         if internal_transfer_type:
    #             self.picking_type_id = internal_transfer_type.id
    #     else:
    #         self.picking_type_id = False

class StockPicking(models.Model):
    _inherit = 'stock.picking.type'

    is_internal = fields.Boolean(string='Internal Transfer')
    # , compute = '_compute_is_internal'

    # def _compute_is_internal(self):
    #     for record in self:
    #         if record.code == 'internal':
    #             record.is_internal = True
    #         else:
    #             record.is_internal = False

    # def _compute_is_internal(self):
    #     is_internal_set = False  # Initialize the flag
    #
    #     for record in self:
    #         if record.code == 'internal':
    #             if not is_internal_set:
    #                 record.is_internal = True
    #                 is_internal_set = True
    #             else:
    #                 record.is_internal = False
    #         else:
    #             record.is_internal = False

    @api.onchange('code')
    def _onchange_code(self):
        if self.code == 'internal':
            self.is_internal = True
        else:
            self.is_internal = False

    @api.constrains('is_internal')
    def _check_is_internal(self):
        for record in self:
            if record.is_internal:
                existing_records = self.search([('is_internal', '=', True), ('id', '!=', record.id)])
                if existing_records:
                    raise ValidationError("Another form already has 'is_internal' set to True.")
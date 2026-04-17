from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ShopTransfer(models.Model):
    _name = "shop.transfer"
    _description = "Shop Transfer"
    _order = 'reference desc'
    _rec_name = 'reference'


# ref

    reference = fields.Char(readonly=True, copy=False, default=lambda self: _('New'))
    branch_id = fields.Many2one('res.branch', string="Branch", default=lambda self: self.env.user.branch_id.id, store=True, readonly=True,)
    date = fields.Date(string='Date', default=fields.Date.today())
    narration = fields.Char("Narration")
    order_lines = fields.One2many('shop.transfer.line', 'shop_transfer_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
    ], string='Status', default='draft', track_visibility='onchange')
    location_dest_id = fields.Many2one('stock.picking', string="Transfer To")
    location_id = fields.Many2one('stock.location', default=lambda self: self.env.user.branch_l_id.id, store=True, readonly=True, string="Requested From")


    # def get_stock_locations_for_store_users(self):
    #     stock_locations = []
    #     users = self.env['res.users'].search([('groups_id.name', '=', 'Store')])
    #     for user in users:
    #         stock_location = user.branch_id.stock_location.name
    #         stock_locations.append(stock_location)
    #     return stock_locations

    requested_to = fields.Many2one(
        'stock.warehouse', domain="[('store_warehouse','=',False)]",
        string="Requested To"
    )
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('shop.transfer') or _('New')
        res = super(ShopTransfer, self).create(vals)
        return res

    def action_confirm(self):
        user = self.env.user
        if user.branch_l_id:
            if self.order_lines:
                warehouse = self.env['stock.picking.type'].search(
                    [('warehouse_id', '=', self.requested_to.id), ('code', '=', 'internal')], limit=1)
                transfer = self.env['stock.picking'].create(
                    {'location_dest_id': user.branch_l_id.id, 'location_id': self.requested_to.lot_stock_id.id,'state':'draft',
                     'picking_type_id': warehouse.id, 'shop_transfer': True,'branch_id': self.requested_to.branch_id.id,
                     'move_ids_without_package': [{'name': rec.items_id.name,
                                                   'product_id': rec.items_id.id,
                                                   'product_uom_qty': rec.qty,
                                                   'reserved_availability': rec.qty,
                                                   'quantity_done': rec.qty,
                                                   'req_qty': rec.qty,
                                                   'location_id': self.requested_to.lot_stock_id.id,
                                                   'location_dest_id': user.branch_l_id.id} for rec in self.order_lines]})
                if transfer:
                    self.state = 'requested'
                else:
                    ret = {'warning': {
                                          'title': _('Warning'),
                                          'message': _('Shop Request creation failed')
                                      }}
                    return ret
            else:
                raise ValidationError("Add a product before validating")



# if self.shop_materials:
#     if user.branch_l_id:
#         for rec in self.line_ids:
#             if rec.requested_to:
#                 transfer = self.env['stock.picking.type'].search([('warehouse_id', '=', rec.requested_to.warehouse_id.id), ('code', '=', 'internal')])
#                 self.env['stock.picking'].create({'picking_type_id': transfer.id, 'location_dest_id': user.branch_l_id.id,
#                                                   'location_id': rec.requested_to.id, 'store_mat_req': True, 'move_ids_without_package': [(0, 0, {
#                         'name': rec.items_id.name,
#                         'product_id': rec.items_id.id,'location_id':rec.requested_to.id,'location_dest_id': user.branch_w_id.lot_stock_id.id,
#                         'product_uom_qty': rec.qty, })], })
# self.state = 'requested'

    @api.model
    def shop_transfer_action_python(self):
       domain = [
           ('branch_id', 'in', self.env.user.branch_ids.ids),
       ]

       action = {
           'name': 'Shop Transfer',
           'type': 'ir.actions.act_window',
           'res_model': 'shop.transfer',
           'view_mode': 'tree,form',
           'view_ids': [
               (5, 0, 0),
               (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('zcl_shop.shop_transfer_tree').id}),
               (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('zcl_shop.view_shop_transfer_form').id}),
           ],
           'context': {'show_default_code': True},
           'domain': domain,
       }
       return action







class ShopTransferLine(models.Model):
    _name = "shop.transfer.line"
    _description = "Shop Transfer line"

    serial_no = fields.Integer(string="Sl no" ,default=1)
    items_id = fields.Many2one('product.product',string="Items")
    description = fields.Char(related='items_id.name', string="Description")
    # requested_to = fields.Many2one('stock.location', string="Requested To")
    units = fields.Many2one('uom.uom',string="Units")
    qty = fields.Float(string="Quantity")
    shop_transfer_id = fields.Many2one('shop.transfer', string='Shop Transfer')
    link_1 = fields.Char(string="Link_1")


    @api.model
    def create(self, values):
        if not values.get('serial_no'):
            last_record = self.search([], order='serial_no desc', limit=1)
            values['serial_no'] = last_record.serial_no + 1 if last_record else 1
        return super(ShopTransferLine, self).create(values)

    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                # record.product_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                # record.product_id = product.id
                record.items_id.display_name = product.display_name


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        for rec in self:
            for move_line in rec.move_ids_without_package:
                if rec.picking_type_id.code == 'internal':
                    if move_line.onhand_qty < move_line.req_qty:
                        raise ValidationError(_("Requested quantity is not available in the stock..."))
        return super(StockPicking, self).action_confirm()


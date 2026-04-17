from datetime import datetime

from odoo import fields, models, api, _
from odoo.tests import Form


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True, domain="['&', ('vendor_true', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    # internal_do_partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('vendor_true', '=', True),('purchase_type', '=', 'internal_do')]")
    # project_do_partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('vendor_true', '=', True),('purchase_type', '=', 'project_do')]")
    narration = fields.Text(string="Narration")
    delivery_terms = fields.Char('Delivery Terms')
    delivery_address = fields.Many2one('stock.location', string='Destination Branch',domain="[('usage', '=', 'internal')]",default=lambda self:self.env.user.branch_w_id.lot_stock_id.id, required=True)
    import_delivery_address = fields.Many2one('stock.warehouse', string='Delivery Addr.', domain="[('store_warehouse','=', False)]")
    prq_no = fields.Char(string="PRQ No")
    cargo_details = fields.Char(string="Cargo Details")
    total_qty = fields.Float(string="Quantity")
    total_last_rate = fields.Float(string="Last Rate", digits=(16, 3))
    total_least_rate = fields.Float(string="Least Rate", digits=(16, 3))
    total_gross = fields.Float(string="Gross", digits=(16, 3))
    total_discount_amt = fields.Float(string="Discount Amt", digits=(16, 3))
    total_net_value = fields.Float(string="Net Value", digits=(16, 3))
    total_net = fields.Float(string="Net", digits=(16, 3))
    total_vat = fields.Float(string="VAT 5%", digits=(16, 3))
    shop_purchase = fields.Boolean(string="Shop Purchase")
    store_purchase = fields.Boolean(string="Store Purchase")
    shop_internal_do = fields.Boolean(string='Shop Internal DO')
    store_internal_do = fields.Boolean(string='Store Internal DO')
    shop_project_do = fields.Boolean(string='Shop Project DO')
    store_project_do = fields.Boolean(string='Store Project DO')
    grn_local_import = fields.Boolean(string='Grn local import')
    shop_grn_local_import = fields.Boolean(string='Grn local import')
    purchase_local = fields.Boolean(string='Purchase local')
    purchase_import = fields.Boolean(string='Purchase import')
    purchase_invoiced = fields.Boolean(string='purchase invoiced', default=False)
    total_billed_qty = fields.Float(string="Total billed qty", compute='total_billed_quantity', store=True)
    total_received_qty = fields.Float(string="Total received qty", compute='total_received_quantity', store=True)
    grn_status = fields.Selection(selection=[('pending', 'Pending'), ('partial', 'Partially'),
                                             ('done', 'Completed')],
                                  string='GRN Status',
                                  required=True,
                                  readonly=True,
                                  copy=False,
                                  tracking=True,
                                  default='pending', )
    bill_status = fields.Selection(selection=[('pending', 'Pending'), ('partial', 'Partially'), ('done', 'Completed'), ],
                                   string='Bill Status',
                                   required=True,
                                   readonly=True,
                                   copy=False,
                                   tracking=True,
                                   default='pending',)
    state = fields.Selection(selection_add=[('to_confirm', 'To Confirm')])

    action_source = fields.Selection([
        ('action_1', 'Action 1'),
        ('action_2', 'Action 2')
    ], string='Action Source')

    # def _get_delivery_address_domain(self):
    #     branch_id = self.env.user.branch_w_id.lot_stock_id.id
    #     return [('usage', '=', 'internal'), ('id', '=', branch_id)]

    def auto_workflow(self):
        if self.state == 'purchase':
            self.action_create_invoice()

            if self.invoice_ids:
                bill = self.invoice_ids[0]
                bill.write({
                    'invoice_date': datetime.now()
                })
                bill.action_post()
                journal = self.env["account.journal"].sudo().search([('type', '=', 'bank')], limit=1)
                return_form = Form(self.env["account.payment.register"].sudo().with_context(
                    active_ids=self.invoice_ids[0].id,
                    active_model="account.move",
                    default_amount=self.invoice_ids[0].amount_residual,
                    default_journal_id=journal.id,
                    default_payment_date=datetime.now(),
                    default_branch_id=self.invoice_ids[0].branch_id.id,
                ))
                return_wizard = return_form.save()
                action = return_wizard._create_payments()


    @api.onchange('import_delivery_address')
    def _onchange_import_delivery_address(self):
        if self.import_delivery_address:
            self.delivery_address = self.import_delivery_address.lot_stock_id.id

    # @api.onchange('internal_do_partner_id')
    # def _onchange_internal_do_partner(self):
    #     self.partner_id = self.internal_do_partner_id.id
    #
    # @api.onchange('project_do_partner_id')
    # def _onchange_project_do_partner(self):
    #     self.partner_id = self.project_do_partner_id.id

    @api.onchange('order_line')
    def _onchange_order_lines(self):
        sl_no = 1
        for line in self.order_line:
            line.serial_no = sl_no
            sl_no += 1
            if self.shop_internal_do:
                line.price_unit = line.product_id.traders_price
            if self.store_internal_do:
                line.price_unit = line.product_id.traders_price
            if self.shop_project_do:
                line.price_unit = line.product_id.project_price
            if self.store_project_do:
                line.price_unit = line.product_id.project_price
        total_qty_sum = 0
        total_last_rate_sum = 0
        total_least_rate_sum = 0
        total_gross_sum = 0
        total_discount_amt_sum = 0
        total_net_value_sum = 0
        for rec in self.order_line:
            total_qty_sum += rec.product_qty
            total_last_rate_sum += rec.last_rate
            total_least_rate_sum += rec.least_rate
            total_gross_sum += rec.gross
            total_discount_amt_sum += rec.discount_amt
            total_net_value_sum += rec.price_subtotal
        self.total_qty = total_qty_sum
        self.total_last_rate = total_last_rate_sum
        self.total_least_rate = total_least_rate_sum
        self.total_gross = total_gross_sum
        self.total_discount_amt = total_discount_amt_sum
        self.total_net_value = total_net_value_sum
        self.total_vat = total_net_value_sum * 0.05
        self.total_net = self.total_vat + self.total_net_value

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def action_po(self):
        """This function is defined for validate transfer receipt when
        confirming the purchase order"""
        res = self.button_confirm()
        if res:
            for rec in self.picking_ids:
                if self.purchase_local:
                    rec.local_grn = True
                if self.purchase_import:
                    rec.import_grn = True
                if self.shop_purchase:
                    rec.cash_grn = True
                    rec.local_grn = True
                if self.store_purchase:
                    rec.store_cash_grn = True
                    rec.local_grn = True
                #picking type location changing
                recepit = self.env['stock.picking.type'].search([('id', '=', rec.picking_type_id.id)])
                recepit.update({
                    'default_location_dest_id': self.delivery_address.id
                })
                rec.location_dest_id = self.delivery_address.id
                for res in rec.move_ids_without_package:
                    res.location_dest_id = self.delivery_address.id
                    res.quantity_done = res.product_uom_qty
                # rec.button_validate()

    def action_create_invoice(self):
        res = super(PurchaseOrder,self).action_create_invoice()
        if self.purchase_import:
            self.invoice_ids.purchase_import = True
        if self.purchase_local:
            self.invoice_ids.purchase_local = True
        if self.shop_purchase:
            self.invoice_ids.cash_grn = True
        if self.store_purchase:
            self.invoice_ids.store_cash_grn = True
        return res

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not self.purchase_local and not self.purchase_import:
            if not invoices:
                # Invoice_ids may be filtered depending on the user. To ensure we get all
                # invoices related to the purchase order, we read them in sudo to fill the
                # cache.
                self.invalidate_model(['invoice_ids'])
                self.sudo()._read(['invoice_ids'])
                invoices = self.invoice_ids

            result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
            # choose the view_mode accordingly
            if len(invoices) > 1:
                result['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                res = self.env.ref('account.view_move_form', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = invoices.id
            else:
                result = {'type': 'ir.actions.act_window_close'}

            return result

    @api.depends('order_line.qty_invoiced')
    def total_billed_quantity(self):
        for rec in self:
            rec.total_billed_qty = sum(line.qty_invoiced for line in rec.order_line)
            if rec.total_qty == rec.total_billed_qty:
                rec.bill_status = 'done'
            elif rec.total_billed_qty !=0 and rec.total_billed_qty != rec.total_qty:
                rec.bill_status = 'partial'
            elif not rec.total_billed_qty:
                rec.bill_status = 'pending'

    @api.depends('order_line.qty_received')
    def total_received_quantity(self):
        for rec in self:
            rec.total_received_qty = sum(line.qty_received for line in rec.order_line)
            if rec.total_qty == rec.total_received_qty:
                rec.grn_status = 'done'
            elif rec.total_received_qty !=0 and rec.total_received_qty != rec.total_qty:
                rec.grn_status = 'partial'
            elif not rec.total_received_qty:
                rec.grn_status = 'pending'

    

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    serial_no = fields.Integer(string="SNo.")
    units = fields.Many2one('uom.uom',string="Units")
    last_rate = fields.Float(string="Last Purchase Rate")
    least_rate = fields.Float(string="Least Rate")
    gross = fields.Float(string="Gross", compute='_compute_gross', store=True)
    discount_amt = fields.Float(string="Discount Amt", store=True)
    price_subtotal = fields.Monetary(string="Net Amount", compute='_compute_price_subtotal', store=False)
    price_unit = fields.Float(
        string='Unit Price', required=True, digits='Product Price',readonly=False, store=True)

    items_id = fields.Many2one('product.product',string="Items", store=True)

# onchange for display the product that selected in 'items_id(A many2one field which list the product as default code only)' field
    @api.onchange('items_id')
    def _onchange_items_id(self):
        for record in self:
            if record.items_id:
                record.product_id = record.items_id.id
                product = record.items_id.with_context(show_default_code=False)
                record.product_id = product.id
                record.product_id.display_name = product.display_name


    @api.onchange('product_id','order_id')
    def _onchange_product_ids(self):
        last_purchase_rate = self.env['purchase.order.line'].search([('product_id', '=', self.product_id.id),('order_id', '!=', self.order_id._origin.id),('state', '!=', 'draft')], limit=1, order='id desc')
        if self.product_id:
                self.last_rate = last_purchase_rate.price_unit
                self.least_rate = self.product_id.least_rates


    @api.depends('product_qty', 'price_unit')
    def _compute_gross(self):
        for record in self:
            record.gross = record.product_qty * record.price_unit

    @api.depends('gross', 'discount_amt')
    def _compute_price_subtotal(self):
        for record in self:
            record.price_subtotal = record.gross - record.discount_amt

    # def _compute_qty_invoiced(self):
    #     pass



class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_import = fields.Boolean(string="Purchase Import")
    purchase_local = fields.Boolean(string="Purchase Local")
    cash_grn = fields.Boolean(string='Cash Grn')
    store_cash_grn = fields.Boolean(string='store Cash Grn')




class ProductProductInh(models.Model):
    _inherit = 'product.product'

# only show the code of the product
# should set the context {'show_default_code': False} in the "purchase_local_order_form" view to prevent the product Many2one field from displaying only the default code, as the "purchase_local_order_action" action uses the context {'show_default_code': True}.
    def name_get(self):
        result = []
        for record in self:
            if self._context.get('show_default_code', False):

                name = record.default_code or record.name
            else:
                name = super(ProductProductInh, record).name_get()[0][1]
            result.append((record.id, name))
        return result







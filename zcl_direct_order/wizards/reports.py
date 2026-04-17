from odoo import models, fields


class SaleOrderInherit(models.TransientModel):
    _name = "sale.order.wizards"

    date_to = fields.Date(string="Date TO")
    date_from = fields.Date(string="Date From")

    def sale_order_pdf(self):
        data_list =[]
        if self.date_to and self.date_from:
            sale_orders = self.env['sale.order'].search([('state', '=', 'sale'), ('normal_do', '=', True),

                                                         ('date_order', '>=', self.date_from),
                                                         ('date_order', '<=', self.date_to),
                                                         ])
        elif self.date_from:
            sale_orders = self.env['sale.order'].search([('state', '=', 'sale'), ('normal_do', '=', True),

                                                         ('date_order', '>=', self.date_from)
                                                         ])
        elif self.date_to:
            sale_orders = self.env['sale.order'].search([('state', '=', 'sale'), ('normal_do', '=', True),

                                                         ('date_order', '<=', self.date_to)
                                                         ])
        else:
            sale_orders = self.env['sale.order'].search([('state', '=', 'sale'), ('normal_do', '=', True)])
        for rec in sale_orders:
            for data in rec.order_line:
                if rec.invoice_ids:
                    dict ={
                        'date_from':self.date_from,
                        'date_to': self.date_to,
                        'do_number': rec.name,
                        'invoice_number': rec.invoice_ids.name,
                        'product': data.product_id.name,
                        'quantity': data.product_uom_qty,
                    }
                    data_list.append(dict)
        print(data_list)
        datas = {
            'list_data': data_list
        }
        return self.env.ref('zcl_direct_order.action_report_invoice').report_action(None, data=datas)






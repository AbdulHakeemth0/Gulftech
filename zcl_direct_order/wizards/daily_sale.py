from odoo import models, fields
from datetime import datetime, date


class SaleOrderDailyInherit(models.TransientModel):
    _name = "sale.order.daily.wizards"

    date_from = fields.Date(string="Date From", default=fields.date.today())

    def daily_sale_order_pdf(self):
        if isinstance(self.date_from, date):
            date_from = self.date_from
        else:
            date_from = datetime.strptime(str(self.date_from), '%Y-%m-%d')

        sales_orders = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('normal_do', '=', True),
            ('create_date', '>=', date_from.strftime('%Y-%m-%d 00:00:00')),
            ('create_date', '<=', date_from.strftime('%Y-%m-%d 23:59:59'))
        ])

        data_list = []
        data = {
            'date_from': date_from.strftime('%Y-%m-%d'),
            'sales': sales_orders
        }

        print(data['sales'], "sales")

        for rec in data['sales']:
            for line in rec.order_line:
                if rec.invoice_ids:
                    data_dict = {
                        'product': line.product_id.name,
                        'invoice_number': rec.invoice_ids.name,
                        'quantity': line.product_uom_qty,
                    }
                    data_list.append(data_dict)

        print(data_list)

        datas = {
            'list_data': data_list
        }

        return self.env.ref('zcl_direct_order.action_report_daily_sale').report_action(None, data=datas)

    # def daily_sale_order_pdf(self):
    #     print(self.date_from,"22222222")
    #     print(self.env['sale.order'].search([('state', '=', 'sale')]),"qqqqqqqqqqqqqqqqqq")
    #     data_list = []
    #     data = {
    #         'date_from': self.date_from,
    #         'sales': self.env['sale.order'].search([('state', '=', 'sale'), ('normal_do', '=', True),
    #                                                 ('create_date', '=', self.date_from)])
    #     }
    #     print(data['sales'],"sales")
    #
    #     for rec in data['sales']:
    #         for line in rec.order_line:
    #             if rec.invoice_ids:
    #                 dict = {
    #                     'product': line.product_id.name,
    #                     'invoice_number': rec.invoice_ids.name,
    #                     'quantity': line.product_uom_qty,
    #                 }
    #                 data_list.append(dict)
    #
    #     print(data_list)
    #     datas = {
    #         'list_data': data_list
    #     }
    #     return self.env.ref('zcl_direct_order.action_report_daily_sale').report_action(None, data=datas)

    # def daily_sale_order_pdf(self):
    #     data_list = []
    #     data = {
    #         'date_from': self.date_from,
    #         'sales': self.env['sale.order'].search([('state', '=', 'sale'),('normal_do', '=', True),
    #                   ('date_order', '>=', self.date_from),('date_order', '<=', self.date_from)])
    #         }
    #     for rec in data:
    #         for data in rec.order_line:
    #             if rec.invoice_ids:
    #                 dict = {
    #                     'product': data.product_id.name,
    #                     'invoice_number': rec.invoice_ids.name,
    #                     'quantity': data.product_uom_qty,
    #                 }
    #                 data_list.append(dict)
    #
    #         print(data_list)
    #         datas = {
    #             'list_data': data_list
    #         }
    #         return self.env.ref('zcl_direct_order.action_report_daily_sale').report_action(None, data=datas)







from odoo import models

class DamageStockOUT(models.AbstractModel):
    _name = 'report.zcl_damage_stock.damage_stockout_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):
        stock = self.env['damage.stock'].search([('store_true','=',True)])

        sheet = workbook.add_worksheet("Damage Stock IN")
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'align': 'center', 'bold': True})
        format_2 = workbook.add_format({'align': 'left', 'bg_color': 'gray'})
        format_3 = workbook.add_format({'align': 'left', 'text_wrap': 15, 'bg_color': 'gray'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})


        sheet.merge_range(0, 0, 0+1, 0 + 3, 'Damage Stock IN', format_1)
        sheet.write(2, 0, 'Narration', format_3)
        sheet.write(2, 1, 'Transfer From', format_3)
        sheet.write(2, 2, 'Transfer To', format_3)
        sheet.write(2, 3, 'Product', format_3)
        sheet.write(2, 4, 'Description', format_3)
        sheet.write(2, 5, 'Unit', format_3)
        sheet.write(2, 6, 'Quantity', format_3)
        sheet.write(2, 7, 'Remark', format_3)

        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 25)

        row = 3
        print("**********************************")

        for rec in stock:
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7")
            # sheet.write(row, 0, rec.narration)
            sheet.write(row, 1, rec.transfer_from.name)
            sheet.write(row, 2, rec.transfer_to.name)


            print(rec,"2@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            for line_data in rec.line_ids:
                print(line_data,"##############################")
                sheet.write(row, 3, line_data.product_id.name)
                sheet.write(row, 4, line_data.description)
                sheet.write(row, 5, line_data.units)
                sheet.write(row, 6, line_data.qty)
                sheet.write(row, 7, line_data.remark)
                row += 1

        total_records = len('records')
        last_comb = f"Total records in this page: {total_records}"
        sheet.merge_range(row + 3, 0, row + 3, 3, last_comb, format_2)

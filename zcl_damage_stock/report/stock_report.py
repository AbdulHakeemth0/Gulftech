from odoo import models

class DamageStockReport(models.Model):
    _name = 'damage.stock.wizard'

    def action_damage_stock_report_fn(self):
        data = {
            'id': self.id
        }

        return self.env.ref('zcl_damage_stock.damage_stockout_report_xlsx').report_action(self, data=data)


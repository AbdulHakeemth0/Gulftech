from odoo import api, fields, models

class SubCompany(models.Model):
    _name = 'sub.company'
    _description = 'Sub Company Model'

    name = fields.Char()
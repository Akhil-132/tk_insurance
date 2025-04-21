from odoo import api, fields, models

class CompanyName(models.Model):
    _name = 'insurance.company.name'
    _description = 'Insurance Company Name'
    _rec_name = 'name'

    name = fields.Char(string="Company Name", required=True, translate=True, help="The name of the insurance company.")

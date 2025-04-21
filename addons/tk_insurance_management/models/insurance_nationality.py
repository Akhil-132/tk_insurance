from odoo import api, fields, models


class Nationality(models.Model):
    _name = 'insurance.nationality'
    _description = 'Insurance Nationality'
    _rec_name = 'name'

    name = fields.Char(string="Nationality", required=True, translate=True)
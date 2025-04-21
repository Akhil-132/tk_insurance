from odoo import api, fields, models

class AreaCovered(models.Model):
    _name = 'insurance.area.covered'
    _description = 'Insurance Area Covered'
    _rec_name = 'name'

    name = fields.Char(string="Area Covered", required=True, translate=True)

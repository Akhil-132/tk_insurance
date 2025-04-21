from odoo import api, fields, models

class VehicleType(models.Model):
    _name = 'insurance.vehicle.type'
    _description = 'Insurance Vehicle Type'
    _rec_name = 'name'

    name = fields.Char(string="Vehicle Type", required=True, translate=True)

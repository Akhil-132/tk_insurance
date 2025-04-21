# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models, _


class InsuranceClaim(models.TransientModel):
    _name = 'insurance.claim'
    _description = "Insurance Claim"

    insurance_id = fields.Many2one('insurance.information', string="Insurance", required=True)
    claim_date = fields.Date(string='Date')

    @api.model
    def default_get(self, field):
        res = super(InsuranceClaim, self).default_get(field)
        rec = self._context.get('active_id')
        res['insurance_id'] = self._context.get('insurance_id')
        return res

    def insurance_claim_create(self):
        for rec in self:
            data = {
                'insurance_id': self.insurance_id.id,
                'claim_date': self.claim_date,
                'insured_id': self.insurance_id.insured_id.id,
                'dob': self.insurance_id.dob,
                'age': self.insurance_id.age,
                'phone': self.insurance_id.insured_id.phone,
                'insurance_nominee_id': self.insurance_id.insurance_nominee_id.id,
                'your_nominee_is_your': self.insurance_id.your_nominee_is_your,
                'nominee_dob': self.insurance_id.nominee_dob,
                'insurance_policy_id': self.insurance_id.insurance_policy_id.id,
                'insurance_category_id': self.insurance_id.insurance_category_id.id,
                'insurance_sub_category_id': self.insurance_id.insurance_sub_category_id.id,
                'agent_id': self.insurance_id.agent_id.id,
                'policy_amount': self.insurance_id.total_policy_amount,
            }
            claim = self.env['claim.information'].create(data)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Claim',
                'res_model': 'claim.information',
                'res_id': claim.id,
                'view_mode': 'form',
                'target': 'current'
            }

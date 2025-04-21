# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AccountMove(models.Model):
    """Account Move"""
    _inherit = 'account.move'
    _description = __doc__

    insurance_information_id = fields.Many2one('insurance.information', string="Insurance")
    claim_information_id = fields.Many2one('claim.information', string="Claim")


class ResPartner(models.Model):
    """Res Partner """
    _inherit = 'res.partner'
    _description = __doc__

    is_agent = fields.Boolean(string="Agent")
    agent_fee = fields.Float(string="Agent Fee (%)")
    insurance_information_ids = fields.One2many('insurance.information', 'agent_id', string="Insurance")
    agent_total_commission = fields.Monetary(string="Total Commission", compute="_total_agent_commission", store=True)
    agent_bill_count = fields.Integer(compute='_get_agent_bills')

    @api.depends('insurance_information_ids')
    def _total_agent_commission(self):
        for rec in self:
            agent_total_commission = 0.0
            if rec.insurance_information_ids:
                for commission in rec.insurance_information_ids:
                    if commission.commission_type == 'percentage':
                        agent_total_commission = agent_total_commission + commission.total_commission
                    else:
                        agent_total_commission = agent_total_commission + commission.fixed_commission
                    rec.agent_total_commission = agent_total_commission
            else:
                rec.agent_total_commission = 0.0

    def action_agent_commission(self):
        return True

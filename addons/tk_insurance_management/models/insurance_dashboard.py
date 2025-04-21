# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
import operator


class InsuranceDashboard(models.Model):
    _name = "insurance.dashboard"
    _description = "Insurance Dashboard"

    @api.model
    def get_insurance_dashboard(self):
        insurance_category = self.env['insurance.category'].sudo().search_count([])
        total_insurance = self.env['insurance.information'].sudo().search_count([])
        running_insurance = self.env['insurance.information'].sudo().search_count([('state', '=', 'running')])
        expired_insurance = self.env['insurance.information'].sudo().search_count([('state', '=', 'expired')])
        total_claim = self.env['claim.information'].sudo().search_count([])
        submit_claim = self.env['claim.information'].sudo().search_count([('state', '=', 'submit')])
        approved_claim = self.env['claim.information'].sudo().search_count([('state', '=', 'approved')])
        not_approved_claim = self.env['claim.information'].sudo().search_count([('state', '=', 'not_approved')])
        res_partner_agent = self.env['res.partner'].sudo().search_count([('is_agent', '=', True)])
        total_claim_count_graph = [['Submit', 'Approved', 'Not Approved'], [submit_claim, approved_claim, not_approved_claim]]
        insurance_state_graph = [['Running', 'Expired'], [running_insurance, expired_insurance]]

        male_count = self.env['insurance.information'].sudo().search_count([('gender', '=', 'male')])
        female_count = self.env['insurance.information'].sudo().search_count([('gender', '=', 'female')])
        others_count = self.env['insurance.information'].sudo().search_count([('gender', '=', 'others')])
        gender_count = [['Male', 'Female', 'Other'], [male_count, female_count, others_count]]

        data = {
            'insurance_category': insurance_category,
            'total_insurance': total_insurance,
            'running_insurance': running_insurance,
            'expired_insurance': expired_insurance,
            'total_claim': total_claim,
            'submit_claim': submit_claim,
            'approved_claim': approved_claim,
            'not_approved_claim': not_approved_claim,
            'res_partner_agent': res_partner_agent,
            'total_claim_count_graph': total_claim_count_graph,
            'insurance_state_graph': insurance_state_graph,
            'top_agents': self.get_top_agents(),
            'gender_count': gender_count,
        }
        return data

    def get_top_agents(self):
        agent_data_count = {}
        for group in self.env['insurance.information'].read_group([('state', 'in', ['running', 'expired'])],
                                                                  ['agent_id'],
                                                                  ['agent_id'],
                                                                  orderby="agent_id DESC", limit=5):
            agent_name = self.env['res.partner'].sudo().browse(int(group['agent_id'][0])).name
            agent_data_count[agent_name] = group['agent_id_count']
        agent_data_count = dict(sorted(agent_data_count.items(), key=lambda item: item[1], reverse=True))
        return [list(agent_data_count.keys()), list(agent_data_count.values())]

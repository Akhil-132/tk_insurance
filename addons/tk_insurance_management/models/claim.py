# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ClaimInformation(models.Model):
    """Claim Information"""
    _name = "claim.information"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'claim_number'

    claim_number = fields.Char(string='Claim', required=True, readonly=True, default=lambda self: _('New'), copy=False, translate=True)
    insurance_id = fields.Many2one('insurance.information', string="Insurance", required=True)
    insured_id = fields.Many2one('res.partner', string='Insured')
    phone = fields.Char(string="Phone", translate=True)
    dob = fields.Date()
    age = fields.Char(string="Age", compute="get_insured_age_count", translate=True)
    insurance_nominee_id = fields.Many2one('insurance.nominee', string="Nominee")
    your_nominee_is_your = fields.Selection([('grand_daughter', "Grand Daughter"), ('grand_mother', "Grand Mother"),
                                             ('niece', "Niece"), ('sister', "Sister"), ('aunt', "Aunt"),
                                             ('daughter', "Daughter"), ('mother', "Mother")],
                                            string="Your Nominee is Your")
    nominee_dob = fields.Date()
    insurance_policy_id = fields.Many2one('insurance.policy', string='Insurance Policy',
                                          domain="[('insurance_sub_category_id', '=', insurance_sub_category_id)]",
                                          required=True)
    insurance_category_id = fields.Many2one('insurance.category', string="Policy Category", required=True)
    insurance_sub_category_id = fields.Many2one('insurance.sub.category', string="Sub Category",
                                                domain="[('insurance_category_id', '=', insurance_category_id)]",
                                                required=True)
    insurance_time_period = fields.Char(related="insurance_policy_id.insurance_time_period_id.t_period", translate=True)
    agent_id = fields.Many2one('res.partner', string='Agent', domain=[('is_agent', '=', True)])

    policy_amount = fields.Monetary(string="Policy Amount")
    amount_paid = fields.Monetary(string="Amount Paid")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    claim_date = fields.Date(string='Date', required=True)
    policy_terms_and_conditions = fields.Text(string="Terms & Conditions", translate=True)
    invoice_id = fields.Many2one('account.move', string="Claim Bill")
    payment_status = fields.Selection(related='invoice_id.payment_state', string="Payment Status")
    maturity_of_the_policy = fields.Boolean(string="Maturity of the Policy")
    surrender_of_the_policy = fields.Boolean(string="Surrender of the Policy")
    discounted_value_in_policy = fields.Boolean(string="Discounted Value in Policy")
    death_of_the_insured = fields.Boolean(string="Death of the Insured")
    paid_up_of_lapsed_policy = fields.Boolean(string="Paid up of Lapsed Policy")
    other = fields.Boolean(string="Other")
    furnish_date_of_death = fields.Date(string="Date of Death")

    claim_documents_ids = fields.One2many('claim.documents', 'claim_information_id', string="Claim Documents")

    state = fields.Selection([('draft', "New"), ('submit', "Submit"), ('approved', "Approved"),
                              ('not_approved', "Not Approved")], default='draft')

    def draft_to_submit(self):
        self.state = 'submit'

    def submit_to_approved(self):
        documents_verified = True
        for rec in self.claim_documents_ids:
            if not rec.state == 'verified':
                documents_verified = False
                break
        if not documents_verified:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': "Please complete claim documents",
                    'sticky': False,
                }
            }
            return message
        else:
            self.state = 'approved'

    def approved_to_not_approved(self):
        self.state = 'not_approved'

    @api.model
    def create(self, vals):
        if vals.get('claim_number', 'New') == 'New':
            vals['claim_number'] = self.env['ir.sequence'].next_by_code(
                'claim.information') or 'New'
        return super(ClaimInformation, self).create(vals)

    @api.depends('dob')
    def get_insured_age_count(self):
        today = fields.Date.today()
        for rec in self:
            if rec.dob:
                age = today.year - rec.dob.year - ((today.month, today.day) < (rec.dob.month, rec.dob.day))
                if not age < 0:
                    rec.age = str(age) + ' Years'
                else:
                    rec.age = str(0) + ' Years'
            else:
                rec.age = str(0) + ' Years'

    @api.onchange('insurance_id')
    def get_insurance_details(self):
        for rec in self:
            if rec.insurance_id:
                rec.insured_id = rec.insurance_id.insured_id
                rec.dob = rec.insurance_id.dob
                rec.phone = rec.insurance_id.insured_id.phone
                rec.insurance_nominee_id = rec.insurance_id.insurance_nominee_id.id
                rec.your_nominee_is_your = rec.insurance_id.your_nominee_is_your
                rec.nominee_dob = rec.insurance_id.nominee_dob
                rec.insurance_policy_id = rec.insurance_id.insurance_policy_id.id
                rec.insurance_time_period = rec.insurance_id.insurance_time_period
                rec.insurance_category_id = rec.insurance_id.insurance_category_id.id
                rec.insurance_sub_category_id = rec.insurance_id.insurance_sub_category_id.id
                rec.agent_id = rec.insurance_id.agent_id.id
                rec.policy_amount = rec.insurance_id.policy_amount

    def action_claim_settlement_amount(self):
        for record in self:
            if record.amount_paid == 0:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'title': ('Please note'),
                        'message': "Claim approval amount cannot be zero",
                        'sticky': False,
                    }
                }
                return message
            else:
                claim_record = {
                    'name': 'Claim Settlement Amount',
                    'quantity': 1,
                    'price_unit': self.amount_paid,
                }
                invoice_lines = [(0, 0, claim_record)]
                data = {
                    'partner_id': self.agent_id.id,
                    'move_type': 'in_invoice',
                    'invoice_date': fields.Datetime.now(),
                    'invoice_line_ids': invoice_lines,
                    'claim_information_id': self.id
                }
                invoice_id = self.env['account.move'].sudo().create(data)
                invoice_id.action_post()
                self.invoice_id = invoice_id.id
                mail_template = self.env.ref('tk_insurance_management.insurance_policy_has_been_approved_mail_template')
                if mail_template:
                    mail_template.send_mail(self.id, force_send=True)
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Invoice',
                    'res_model': 'account.move',
                    'res_id': invoice_id.id,
                    'view_mode': 'form',
                    'target': 'current'
                }

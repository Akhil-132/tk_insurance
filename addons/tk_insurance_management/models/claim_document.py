# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class ClaimDocuments(models.Model):
    """Claim Documents"""
    _name = 'claim.documents'
    _description = __doc__
    _rec_name = 'claim_document_type_id'

    claim_document_type_id = fields.Many2one('claim.document.type', string="Document Type", required=True)
    file_name = fields.Char(string="filename", translate=True)
    state = fields.Selection([('verified', "Verified"), ('rejected', "Rejected")], string="Status")
    avatar = fields.Binary(string="Document", required=True)
    claim_information_id = fields.Many2one('claim.information')

    @api.onchange('state')
    def onchange_state(self):
        for record in self:
            if record.state == 'verified':
                record.claim_document_type_id = record.claim_document_type_id
            else:
                record.claim_document_type_id = False

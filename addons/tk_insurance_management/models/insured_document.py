# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class InsuredDocuments(models.Model):
    """Insured Documents"""
    _name = 'insured.documents'
    _description = __doc__
    _rec_name = 'insured_info_id'

    insured_info_id = fields.Many2one("insurance.information", string="Insured No", readonly=True)
    insured_id = fields.Many2one(related="insured_info_id.insured_id", string="Insured", readonly=True)
    file_name = fields.Char(string="filename", translate=True)
    avatar = fields.Binary(string="Document", required=True)
    insured_document_type_id = fields.Many2one('insured.document.type', string="Document Type")

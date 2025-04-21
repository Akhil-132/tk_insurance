# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ClaimDocumentType(models.Model):
    """Claim Document Type"""
    _name = 'claim.document.type'
    _description = __doc__
    _rec_name = 'claim_document_type'

    claim_document_type = fields.Char(string="Document Type", required=True, translate=True)


class InsuredDocumentType(models.Model):
    """Insured Document Type"""
    _name = 'insured.document.type'
    _description = __doc__
    _rec_name = 'insured_document_type'

    insured_document_type = fields.Char(string="Document Type", required=True, translate=True)
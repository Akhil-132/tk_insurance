# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import date


class RevenueRecord(models.Model):
    _name = 'revenue.record'
    _description = 'Revenue Record (For Viewing Only)'
    
    invoice_id = fields.Many2one('account.move', string='Invoice', compute='_compute_invoice_id')
    revenue_entry = fields.Boolean(string="Revenue Entry", default=False)
    insurance_information_id = fields.Many2one('insurance.information', string="Insurance Reference")
    partner_id = fields.Many2one('res.partner', string="Agent")
    invoice_date = fields.Date(string="Date")
    company_name = fields.Char(string="Company Name")
    insurance_type = fields.Char(string="Insurance Type")
    commission = fields.Float(string="Commission")
    policy_tax_amount = fields.Float(string="Policy VAT Amount")
    total_amount = fields.Float(string="Total Revenue", compute="_compute_total")
    invoice_state = fields.Char(string='Invoice Status', compute='_compute_invoice_state', store=True)
    payment_state = fields.Char(string='Payment Status', compute='_compute_payment_state', store=True)

    
    @api.depends('insurance_information_id')
    def _compute_payment_state(self):
        for record in self:
            # Find the invoice that matches the insurance_information_id
            invoice = self.env['account.move'].search([('insurance_information_id', '=', record.insurance_information_id.id)], limit=1)
            if invoice:
                record.payment_state = invoice.payment_state  # The payment state of the invoice (not_paid, partial, paid, etc.)
            else:
                record.payment_state = 'No Payment Found'
    
    @api.depends('insurance_information_id')
    def _compute_invoice_id(self):
        for record in self:
            # Find the invoice that matches the insurance_information_id
            invoice = self.env['account.move'].search([('insurance_information_id', '=', record.insurance_information_id.id)], limit=1)
            if invoice:
                record.invoice_id = invoice  # Set the found invoice as the value for invoice_id
            else:
                record.invoice_id = False
    
    @api.depends('insurance_information_id')
    def _compute_invoice_state(self):
        for record in self:
            # Find the invoice that matches the insurance_information_id
            invoice = self.env['account.move'].search([('insurance_information_id', '=', record.insurance_information_id.id)], limit=1)
            if invoice:
                record.invoice_state = invoice.state  # The state of the invoice (draft, posted, paid, etc.)
            else:
                record.invoice_state = 'No Invoice Found'


    @api.depends('commission', 'policy_tax_amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = rec.commission + rec.policy_tax_amount

class InsuranceInformation(models.Model):
    """Insurance Information"""
    _name = 'insurance.information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'insurance_number'

    insurance_number = fields.Char(string='Insurance', required=True, readonly=True, default=lambda self: _('New'),
                                   copy=False,  translate=True)
    insured_id = fields.Many2one('res.partner', string='Insured')
    insurance_nominee_id = fields.Many2one('insurance.nominee', string="Nominee")
    your_nominee_is_your = fields.Selection([('grand_daughter', "Grand Daughter"), ('grand_mother', "Grand Mother"),
                                             ('niece', "Niece"), ('sister', "Sister"), ('aunt', "Aunt"),
                                             ('daughter', "Daughter"), ('mother', "Mother")],
                                            string="Your Nominee is Your")
    nominee_dob = fields.Date(string="Date of Birth")

    dob = fields.Date(string="Date Of Birth")
    age = fields.Char(string="Age", compute="get_insured_age_count", translate=True)
    gender = fields.Selection([('male', "Male"), ('female', "Female"), ('others', "Others")], string="Gender")
    issue_date = fields.Date(string="Issue Date", required=True, default=fields.Date.context_today)
    expiry_date = fields.Date(string="Expiry Date", readonly=True, compute="_compute_time_period_date")
    agent_id = fields.Many2one('res.partner', string='Agent', domain=[('is_agent', '=', True)])
    agent_phone = fields.Char(related='agent_id.phone', string="Phone", translate=True)
    agent_id = fields.Many2one('res.partner', string="Agent", domain=[('is_agent', '=', True)])
    agent_fee = fields.Float(string="Agent Fee (%)", store=True)
    agent_fee_amount = fields.Float(string="Agent Fee amount", compute="_compute_agent_fee_amount", store=True)
    @api.onchange('agent_id')
    def _onchange_agent_id(self):
        if self.agent_id:
            self.agent_fee = self.agent_id.agent_fee
    premium_type = fields.Selection([('fixed', "Fixed"), ('installment', "Installment")], default='fixed',
                                    string="Premium Type")
    # product_id = fields.Many2one('product.product', string='Product', required=True, help="Product associated with the insurance policy")
    customer_invoice_id = fields.Many2one('account.move', string='Customer Invoice', readonly=True)
    invoice_created = fields.Boolean(string="Invoice Created", default=False, tracking=True)
    vendor_bill_created = fields.Boolean(string="Vendor Bill Created", default=False, tracking=True)
    agent_bill_created = fields.Boolean(string="Agent Bill Created", default=False, tracking=True)
    sp_bill_created = fields.Boolean(string="SP Bill Created", default=False, tracking=True)    
    # customer_id = fields.Many2one('res.partner', string='Customer', help="Customer associated with the insurance policy")
    insurance_category_id = fields.Many2one('insurance.category', string="Policy Category", required=True)
    category = fields.Selection(related="insurance_category_id.category")
    insurance_sub_category_id = fields.Many2one('insurance.sub.category', string="Sub Category",
                                                domain="[('insurance_category_id', '=', insurance_category_id)]",
                                                required=True)
    insurance_sub_category_name = fields.Char(string="Sub Category Name", related='insurance_sub_category_id.name', store=True)

    insurance_policy_id = fields.Many2one('insurance.policy', string='Insurance Policy',
                                          required=True, readonly=False, store=True)
    company_name_id = fields.Many2one('insurance.company.name', string="Company Name", compute='_compute_company_name', readonly=False)
    insurance_buying_for_id = fields.Many2one('insurance.buying.for', string="Buying For",
                                              domain="[('insurance_category_id', '=', insurance_category_id)]")
    insurance_time_period = fields.Char(related="insurance_policy_id.insurance_time_period_id.t_period", translate=True)
    duration = fields.Integer(related="insurance_policy_id.insurance_time_period_id.duration",
                              string="Duration (Months)")
    policy_terms_and_conditions = fields.Text(string="Terms & Conditions", translate=True)
    vehicle_type_id = fields.Many2one('insurance.vehicle.type', string="Vehicle Body Type")
    cylinder_type = fields.Many2one('cylinder.type', string="Cylinder Type")
    doors = fields.Integer(string="No. OF Doors")
    vehicle_ton = fields.Integer(string="Vehicle Ton")    
    usage = fields.Selection([
        ("private", "Private"),
        ("govt.", "Govt."),
        ("commercial", "Commercial")
    ], string="Usage", store=True)
    license_age = fields.Float(string="License age")

    @api.onchange(
        'insurance_sub_category_id',
        'vehicle_type_id',
        'cylinder_type',
        'doors',
        'vehicle_ton',
        'usage',
        'license_age',
        'dob',
        'company_name_id',
    )
    def _onchange_filter_policies(self):
        Policy = self.env['insurance.policy']
        warning = None

        if not self.insurance_sub_category_id:
            policies = Policy.search([])
            companies = policies.mapped('company_name_id').ids
            return {
                'domain': {
                    'insurance_policy_id': [('id', '=', False)],
                    'company_name_id': [('id', 'in', companies)],
                }
            }

        domain = [('insurance_sub_category_id', '=', self.insurance_sub_category_id.id)]

        # Check for mandatory license age when required by the policy
        license_age_required = self.insurance_sub_category_id.name in ["Third-Party Insurance", "Comprehensive Insurance"]
        
        if license_age_required and self.license_age is None:
            warning = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': 'License age is required for this insurance type. Please enter the license age to see available policies.',
                    'sticky': False,
                 }
            }
        elif license_age_required and self.license_age < 0:
            warning = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': 'License age cannot be negative. Please enter a valid license age.',
                    'sticky': False,
                }
            }

        if self.insurance_sub_category_id.name == "Third-Party Insurance":
            if not self.vehicle_type_id or not self.cylinder_type or not self.doors or not self.usage:
                policies = Policy.search(domain)
                companies = policies.mapped('company_name_id').ids
                result = {
                    'domain': {
                        'insurance_policy_id': [('id', '=', False)],
                        'company_name_id': [('id', 'in', companies)],
                    }
                }
                if warning:
                    result['warning'] = warning
                return result

            domain += [
                ('vehicle_type_id', '=', self.vehicle_type_id.id),
                ('cylinder_type', '=', self.cylinder_type.id),
                ('doors', '=', self.doors),
                ('usage', '=', self.usage),
            ]

        elif self.insurance_sub_category_id.name == "Comprehensive Insurance":
            if not self.vehicle_type_id or not self.usage:
                policies = Policy.search(domain)
                companies = policies.mapped('company_name_id').ids
                result = {
                    'domain': {
                        'insurance_policy_id': [('id', '=', False)],
                        'company_name_id': [('id', 'in', companies)],
                    }
                }
                if warning:
                    result['warning'] = warning
                return result

            domain += [
                ('vehicle_type_id', '=', self.vehicle_type_id.id),
                ('usage', '=', self.usage),
            ]

        # Only apply license age filter if it's provided and valid
        if license_age_required and self.license_age is not None and self.license_age >= 0:
            domain += [('license_age_from', '<=', self.license_age), ('license_age_to', '>=', self.license_age)]
        elif license_age_required:
            # Don't return any policies if license age is required but not properly provided
            matching_policies = Policy.browse([])
            matching_companies = []
        else:
            # License age not required or not provided (but not required) - proceed with other filters
            matching_policies = Policy.search(domain)
            matching_companies = matching_policies.mapped('company_name_id').ids

        # Owner Age Filter
        if self.dob:
            today = date.today()
            owner_age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
            domain += [('owner_age_from', '<=', owner_age), ('owner_age_to', '>=', owner_age)]

        if not (license_age_required and (self.license_age is None or self.license_age < 0)):
            matching_policies = Policy.search(domain)
            matching_companies = matching_policies.mapped('company_name_id').ids

        mandatory_fields_filled = bool(
            self.insurance_sub_category_id and
            self.vehicle_type_id and
            self.usage and
            (not license_age_required or self.license_age is not None)
        )

        if self.insurance_sub_category_id.name == "Third-Party Insurance":
            mandatory_fields_filled = mandatory_fields_filled and all([self.cylinder_type, self.doors])

        if self.company_name_id and mandatory_fields_filled:
            matching_policies = matching_policies.filtered(lambda p: p.company_name_id == self.company_name_id)
            if not matching_policies:
                return {
                    'warning': {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'warning',
                            'message': 'No policy matched with the selected company and the entered details.',
                            'sticky': False,
                        }
                    },
                    'domain': {
                        'insurance_policy_id': [('id', '=', False)],
                        'company_name_id': [('id', 'in', self.env['insurance.policy'].search([]).mapped('company_name_id').ids)],
                    },
                }

        if self.insurance_policy_id and self.insurance_policy_id not in matching_policies:
            self.insurance_policy_id = False

        if len(matching_policies) == 1:
            self.insurance_policy_id = matching_policies
        elif self.insurance_policy_id and self.insurance_policy_id not in matching_policies:
            self.insurance_policy_id = False

        result = {
            'domain': {
                'insurance_policy_id': [('id', 'in', matching_policies.ids)],
                'company_name_id': [('id', 'in', matching_companies)],
            }
        }
        
        if warning:
            result['warning'] = warning
            
        return result



        
    # @api.onchange('vehicle_type_id', 'cylinder_type', 'doors', 'vehicle_ton')
    # def _onchange_insurance_policy(self):
    #     """Dynamically update available insurance policies"""
    #     for record in self:
    #         domain = [
    #             ('vehicle_type_id', '=', record.vehicle_type_id.id),
    #             ('cylinder_type', '=', record.cylinder_type.id),
    #             ('doors', '=', record.doors),
    #             ('vehicle_ton', '=', record.vehicle_ton),
    #         ]
    #         policies = self.env['insurance.policy'].search(domain)
    #         if policies:
    #             record.insurance_policy_id = policies[0]  # Auto-select first match
    #         else:
    #             record.insurance_policy_id = False  # Reset field if no match

    # @api.model
    # def default_get(self, fields_list):
    #     """Apply dynamic domain when creating a new record"""
    #     res = super(InsuranceInformation, self).default_get(fields_list)
    #     domain = []
    #     if 'vehicle_type_id' in res and 'cylinder_type' in res and 'doors' in res and 'vehicle_ton' in res:
    #         domain = [
    #             ('vehicle_type_id', '=', res.get('vehicle_type_id')),
    #             ('cylinder_type', '=', res.get('cylinder_type')),
    #             ('doors', '=', res.get('doors')),
    #             ('vehicle_ton', '=', res.get('vehicle_ton')),
    #         ]
    #     res['insurance_policy_id'] = self.env['insurance.policy'].search(domain, limit=1).id if domain else False
    #     return res
    
    commission_type = fields.Selection([('fixed', "Fixed"), ('percentage', "Percentage")],
                                       string="Commission Type")
    fixed_commission = fields.Monetary(string="Fixed Amount")
    total_commission = fields.Monetary(string="Total", compute="total_agent_commission")
    total_policy_amount = fields.Monetary(string="Total Policy Amount", compute="_compute_total_policy_amount",inverse="_inverse_total_policy_amount", store=True, readonly=False)
    total_policy_amount_in_words = fields.Char(string="Total Policy Amount in Words", compute='_compute_total_policy_amount_in_words')   
    duration = fields.Integer(related="insurance_policy_id.duration", string="Duration (Months)")
    monthly_installment = fields.Monetary(string="Monthly Installment", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    policy_amount = fields.Monetary(string="Premium Amount", required=False)
    invoice_id = fields.Many2one('account.move')
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Invoice Status")
    agent_bill_id = fields.Many2one('account.move', string="Commission Bill")

    insurance_emi_ids = fields.One2many('insurance.emi', 'insurance_information_id')
    state = fields.Selection([('draft', "New"),('completed', "Completed"), ('running', "Running"), ('expired', "Expired")], default='draft',
                             string="Status", tracking=True)
    is_readonly = fields.Boolean(compute="_compute_field_readonly", store=True)

    @api.depends('state')
    def _compute_field_readonly(self):
        for rec in self:
            rec.is_readonly = rec.state == 'completed'

    def write(self, vals):
        excluded_fields = ['customer_invoice_id','agent_bill_id', 'state']
        for rec in self:
            if rec.state == 'completed' and 'state' not in vals and not any(field in vals for field in excluded_fields): #allow state change to other state.
                raise ValidationError("This record is completed and cannot be modified.")
        return super(InsuranceInformation, self).write(vals)

    def action_mark_completed(self):
        for rec in self:
            rec.sudo().write({'state': 'completed'})

    def action_reset_to_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'draft'}) #corrected to 'draft'

    instalment_complete = fields.Boolean()

    insured_document_id = fields.Many2one("insured.documents", string="Document")
    document_count = fields.Integer(compute='_compute_document_count')
    claim_count = fields.Integer(compute='_compute_claim_count')

    # Life Insurance:
    life_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")])
    desired_death_amount = fields.Monetary(string="Death Amount")
    life_deductible_amount = fields.Monetary()
    is_smoking_status = fields.Selection([('yes', "Yes"), ('no', "No")], string="Smoking Status")
    length_of_coverage_term = fields.Text(string="Length of Coverage Terms", translate=True)
    life_health_history = fields.Text(string="Insured Health History", translate=True)
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies Insured", translate=True)
    family_medical_history = fields.Text(string="Family Medical History", translate=True)

    # Health Insurance:
    health_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")], string="Insured Age")
    desired_coverage_type = fields.Selection([('individual', "Individual"), ('family', "Family"), ('group', "Group")])
    health_deductible_amount = fields.Monetary()
    copay_amount = fields.Monetary(string="Co-pay Amount")
    out_of_pocket_maximum = fields.Text(string="Out-of-Pocket Maximum", translate=True)
    health_history_of_insured = fields.Text(translate=True)
    drug_coverage = fields.Text(string="Prescription Drug Coverage", translate=True)
    healthcare_provider_network = fields.Text(string="Preferred Healthcare Provider Network", translate=True)

    # Property Insurance:
    construct_year = fields.Char(string="Construct Year", translate=True)
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")
    property_value = fields.Monetary(string="Estimated Value")
    property_damage_coverage = fields.Monetary(string="Damage Coverage")
    property_deductible_amount = fields.Monetary()
    desired_coverage_types = fields.Selection(
        [('dwelling', "Dwelling"), ('personal_property', "Personal Property"), ('liability', "Liability"),
         ('additional_living_expenses', "Additional Living Expenses")])
    property_coverage_limits = fields.Text(string="Property Coverage Limits", translate=True)
    construction_type_and_materials = fields.Text(string="Construction Type and Materials", translate=True)
    special_features_of_the_property = fields.Text(string="Special Features of the Property", translate=True)
    personal_property_inventory = fields.Text(string="Personal Property Inventory", translate=True)

    # Liability Insurance:
    type_of_liability_risk = fields.Selection(
        [('auto', "Auto"), ('homeowner', "HomeOwner's"), ('business', "Business")], string="Liability Risk")
    liability_coverage_type = fields.Selection(
        [('general_liability', "General Liability"), ('professional_liability', "Professional Liability")])
    desired_coverage_limits = fields.Text(string="Desired Coverage Limits", translate=True)
    business_type_and_operations = fields.Text(translate=True)

    # Disability Insurance:
    occupation = fields.Char(string="Occupation", translate=True)
    income = fields.Monetary(string="Income")
    disability_desired_benefit_amount = fields.Monetary(string="Desired Amount")
    insured_is_smoking = fields.Boolean(string="Insured is Smoking")
    length_coverage_disability_period = fields.Text(string="Length of Coverage Period", translate=True)
    disability_health_history = fields.Text(translate=True)
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies", translate=True)

    # Travel Insurance:
    types_of_coverage = fields.Selection(
        [('trip_cancellation', "Trip Cancellation"), ('medical_emergency', "Medical Emergency"),
         ('lost_luggage', "Lost Luggage")], string="Type of Coverage")
    trip_length = fields.Integer(string="Trip Length")
    trip_coverage_amount = fields.Monetary(string="Coverage Amount")
    odometer_unit = fields.Selection([('km', 'Kilometers'), ('mi', 'Miles')], 'Odometer Unit', default='km')
    traveler_health_history = fields.Text(string="Traveler Health History", translate=True)

    # Pet Insurance:
    age_of_breed_of_the_pet = fields.Integer(string="Age of Breed")
    pet_desired_coverage_type = fields.Selection(
        [('accident', "Accident"), ('illness', "Illness"), ('comprehensive', "Comprehensive")])
    exclusions = fields.Selection(
        [('pre_existing_conditions', "Pre-Existing Conditions"), ('certain_breeds', "Certain Breeds")],
        string="Exclusions")

    accident_coverage = fields.Monetary(string="Accident Amount")
    illness_coverage = fields.Monetary(string="Illness Amount")
    pet_deductible_amount = fields.Monetary()
    pet_coverage_limits = fields.Text(string="Coverage Limits", translate=True)

    # Business Insurance:
    business_desired_coverage_type = fields.Selection(
        [('property_damage', "Property Damage"), ('liability', "Liability"), ('workers', "Workers Compensation")])
    number_of_employees = fields.Integer(string="No. of Employees")
    business_property_value = fields.Monetary(string="Property Value")
    business_deductible_amount = fields.Monetary()
    business_type_operation = fields.Text(translate=True)
    business_coverage_limits = fields.Text(string="Business Coverage Limits", translate=True)
    industry_specific_risks = fields.Text(string=" Industry-Specific Risks", translate=True)

    # Vehicle Insurance:
    brand_name_id = fields.Many2one('insurance.brand.name', string="Brand Name")
    brand_model_id = fields.Many2one('insurance.brand.model', string="Brand Model",
                                    domain="[('brand_name_id', '=', brand_name_id)]",
                                     attrs={'invisible': True, 'required': True})
    brand_variant_id = fields.Many2one('insurance.brand.variant', string="Brand Variant", 
                                        domain="[('brand_model_id', '=', brand_model_id)]",
                                       attrs={'invisible': True, 'required': True})
    vehicle_name = fields.Char(string="Vehicle", translate=True)
    model = fields.Char(string="Model", translate=True)
    year = fields.Char(string="Year of MFG", translate=True)

    #vehicle_name = fields.Many2one('insurance.vehiclebrand', string="Vehicle Brand", translate=True)
    vin_no = fields.Char(string="VIN No", translate=True)
    reg_no = fields.Char(string="Registration No", translate=True)
    place_of_reg = fields.Selection([('abu_dhabi', 'Abu Dhabi'),
        ('dubai', 'Dubai'),
        ('sharjah', 'Sharjah'),
        ('ajman', 'Ajman'),
        ('umq', 'Umm Al-Quwain'),
        ('fujairah', 'Fujairah'),
        ('rak', 'Ras Al Khaimah')], default="dubai")
    cubic_capacity = fields.Integer(string="Cubic Capacity")
    setting_capacity = fields.Integer(string="Seating Capacity")
    usage_of_vehicle = fields.Selection([('personal', "Private"), ('commercial', "Commercial")],
                                        string="Usage of Vehicle")
    coverage_type = fields.Selection([('liability', "Liability"), ('collision', "Collision"),
                                      ('comprehensive', "Comprehensive")])

    # Policy Details
    policy_certificate_no = fields.Char(string="Policy/Certificate No", translate=True)
    _sql_constraints = [("policy_certificate_no_unique",'UNIQUE(policy_certificate_no)', "Policy/Certificate No should be unique")]
    previous_policy_no = fields.Char(string="Previous Policy No", translate=True, unique=True)

    # Vehicle IDV
    for_the_vehicle = fields.Monetary(string="For the Vehicle")
    for_trailer = fields.Monetary(string="For Trailer")
    non_electric_accessories = fields.Monetary(string="Non Electric Accessories")
    electric_accessories = fields.Monetary(string="Electric Accessories")
    value_of_cng_lpg_kit = fields.Monetary(string="Value of CNG/LPG Kit")
    total_idv = fields.Monetary(string="Total IDV Value")

    # Own Damage
    basic_od = fields.Monetary(string="Basic OD")
    od_package_premium = fields.Monetary()
    service_tax = fields.Monetary(string="Service Tax")
    special_discount = fields.Monetary(string="Special Discount (-)")
    final_premium = fields.Monetary(string="Final Premium")

    # Liability
    basic_tp_liability = fields.Monetary(string="Basic TP Liability")
    pa_cover_for_owner_driver = fields.Monetary(string="PA Cover for Owner-Driver")
    package_premium = fields.Monetary()
    liability_service_tax = fields.Monetary(string=" Service Tax")
   

    limitation_as_to_use = fields.Text(string="Limitations as to Use", translate=True)
    limits_of_liability = fields.Text(string="Limits of Liability", translate=True)
    deductibles_under_section = fields.Text(string="Deductibles Under Section", translate=True)
    special_conditions = fields.Text(string="Special Conditions", translate=True)
    driving_history = fields.Text(string="Driving History of the Insured", translate=True)
    vehicle_insurance_image_ids = fields.One2many('vehicle.insurance.image', 'insurance_information_id',
                                                  string="Images")
    
    # Added fields
    cover_tpl = fields.Float(related='insurance_policy_id.cover_tpl', store=True, readonly=True)
    insurance_charge = fields.Float(related='insurance_policy_id.insurance_charge', store=True, readonly=True)
    use_previous_cover_tpl = fields.Boolean(string="Cover TPL", default=False)
    use_previous_insurance_charge = fields.Boolean(string="Insurance Charge", default=False)
    percentage_commission = fields.Float(string="Commission")
    commission = fields.Float(string='Total Commission', compute='_compute_commission', store=True, readonly=False)
    ins_payable = fields.Float(string="INS Payable", compute="_compute_ins_payable")
    discount = fields.Float(string="Other fee/ Discount", compute="_compute_discount")
    ins_tax_amount = fields.Float(string="INS VAT Amt", compute="_compute_ins_vat_amt")
    sale_amt_excl_tax = fields.Float(string="Sale Amt (Excl. Tax)", help="Sale amount cannot exceed ins_payable.")
    sale_amt_incl_tax = fields.Float(string="Sale Amt (Incl. Tax)", compute="_compute_saleamt_inctax")
    tax_amount = fields.Float(string="Total VAT Amount", compute="_compute_total_vat",store=True)
    policy_tax_amount = fields.Float(string="Policy VAT Amt", compute="_compute_policy_vat_amt")
    rent_a_car_5 = fields.Float(related='insurance_policy_id.rent_a_car_5', store=True, readonly=True)
    use_rent_a_car_5 = fields.Boolean(string="Rent A Car 5",default=False)
    rent_a_car_10 = fields.Float(related='insurance_policy_id.rent_a_car_10', store=True, readonly=True)
    use_rent_a_car_10 = fields.Boolean(string="Rent A Car 10",default=False)
    natural_perils = fields.Float(related='insurance_policy_id.natural_perils', store=True, readonly=True)
    use_natural_perils = fields.Boolean(string="Natural Perils",default=False)
    road_side_assistance_gold = fields.Float(related='insurance_policy_id.road_side_assistance_gold', store=True, readonly=True)
    use_road_side_assistance_gold = fields.Boolean(string="Road Side Assistance Gold",default=False)
    road_side_assistance_silver = fields.Float(related='insurance_policy_id.road_side_assistance_silver', store=True, readonly=True)
    use_road_side_assistance_silver = fields.Boolean(string="Road Side Assistance Silver",default=False)
    cover_tpl_od = fields.Float(related='insurance_policy_id.cover_tpl_od', store=True, readonly=True)
    use_cover_tpl_od = fields.Boolean(string="Oman Cover TPL OD",default=False)
    cover_tpl_od_tpl = fields.Float(related='insurance_policy_id.cover_tpl_od_tpl', store=True, readonly=True)
    use_cover_tpl_od_tpl = fields.Boolean(string="Oman Cover TPL OD TPL",default=False)
    EVG = fields.Float(related='insurance_policy_id.EVG', store=True, readonly=True)
    use_EVG = fields.Boolean(string="EVG",default=False)
    off_road_cover = fields.Float(related='insurance_policy_id.off_road_cover', store=True, readonly=True)
    use_off_road_cover = fields.Boolean(string="Off Road Cover",default=False)
    gcc_cover = fields.Float(related='insurance_policy_id.gcc_cover', store=True, readonly=True)
    use_gcc_cover = fields.Boolean(string="Gcc Cover",default=False)                       
    ambulance_fee = fields.Float(related='insurance_policy_id.ambulance_fee', store=True, readonly=True)
    ambulance_fee_commission = fields.Float(related='insurance_policy_id.ambulance_fee_commission', store=True, readonly=True)
    EVG_commission = fields.Float(related='insurance_policy_id.ambulance_fee_commission', store=True, readonly=True)
    use_ambulance_fee = fields.Boolean(string="Ambulance Fee",default=False)
    vehicle_value = fields.Float(string="Vehicle Value")
    daynatrade_premium = fields.Float(string="Premium %", compute="compute_daynatrade_premium")
    use_daynatrade_premium = fields.Boolean(string='Use Daynatrade Premium', default=False)
    workshop_premium = fields.Float(string="Premium %", compute="compute_workshop_premium")
    use_workshop_premium = fields.Boolean(string='Use Workshop Premium', default=False)
    non_agency_premium = fields.Float(string="Premium %", compute="compute_non_agency_premium")
    use_non_agency_premium = fields.Boolean(string='Use Non-Agency Premium', default=False)
    scheme_agency_premium = fields.Float(string="Premium %", compute="compute_scheme_agency_premium")
    use_scheme_agency_premium = fields.Boolean(string='Use Scheme Agency Premium', default=False)
    agency_premium = fields.Float(string="Premium %", compute="compute_agency_premium")
    use_agency_premium = fields.Boolean(string="Use Agency Repair", default=False)
    premium_option = fields.Selection([
        ('use_daynatrade_premium', 'Use Daynatrade Premium'),
        ('use_workshop_premium', 'Use Workshop Premium'),
        ('use_scheme_agency_premium', 'Use Scheme Agency Premium'),
        ('use_non_agency_premium', 'Use Non-Agency Premium'),
        ('use_agency_premium', 'Use Agency Repair'),
    ], string='Premium Option', default='')
    
    @api.depends("commission", "agent_fee")
    def _compute_agent_fee_amount(self):
        for record in self:
            if record.commission:
                calculated_fee = (record.agent_fee / 100) * record.commission
                if calculated_fee > record.commission:
                    raise ValidationError("Agent Fee amount cannot exceed the Commission amount!")
                record.agent_fee_amount = calculated_fee
            else:
                record.agent_fee_amount = 0.0

    @api.depends('insurance_policy_id')
    def _compute_company_name(self):
        for record in self:
            if record.insurance_policy_id:
                # Get the company associated with the selected insurance policy
                record.company_name_id = record.insurance_policy_id.company_name_id
            else:
                record.company_name_id = False

    @api.onchange('premium_option')
    def onchange_premium_option(self):
        if self.premium_option:
            self.use_daynatrade_premium = False
            self.use_workshop_premium = False
            self.use_scheme_agency_premium = False
            self.use_non_agency_premium = False
            self.use_agency_premium = False
            setattr(self, self.premium_option, True)
  
    @api.onchange('insurance_policy_id')
    def policy_terms_and_condition(self):
        for rec in self:
            if rec.insurance_policy_id:
                rec.policy_terms_and_conditions = rec.insurance_policy_id.policy_terms_and_conditions

    @api.onchange('insurance_nominee_id')
    def insurance_nominee_details(self):
        for rec in self:
            if rec.insurance_nominee_id:
                rec.your_nominee_is_your = rec.insurance_nominee_id.your_nominee_is_your
                rec.nominee_dob = rec.insurance_nominee_id.nominee_dob

 
    @api.onchange('use_previous_cover_tpl')
    def onchange_use_previous_cover_tpl(self):
      for record in self:
        if self.use_previous_cover_tpl:
                self.cover_tpl = record.insurance_policy_id.cover_tpl
            
    @api.onchange('use_ambulance_fee')
    def onchange_use_ambulance_fee(self):
      for record in self:
        if self.use_ambulance_fee:
                self.ambulance_fee = record.insurance_policy_id.ambulance_fee
                
  
    @api.onchange('use_previous_insurance_charge')
    def onchange_use_previous_insurance_charge(self):
      for record in self:
        if self.use_previous_insurance_charge:
                self.insurance_charge = record.insurance_policy_id.insurance_charge
                
    @api.onchange('use_rent_a_car_5')
    def onchange_use_rent_a_car_5(self):
      for record in self:
        if self.use_rent_a_car_5:
                self.rent_a_car_5 = record.insurance_policy_id.rent_a_car_5 
                
    @api.onchange('use_rent_a_car_10')
    def onchange_use_rent_a_car_10(self):
      for record in self:
        if self.use_rent_a_car_10:
                self.rent_a_car_10 = record.insurance_policy_id.rent_a_car_10

    @api.onchange('use_natural_perils')
    def onchange_use_natural_perils(self):
      for record in self:
        if self.use_natural_perils:
                self.natural_perils = record.insurance_policy_id.natural_perils

    @api.onchange('use_road_side_assistance_gold')
    def onchange_use_road_side_assistance_gold(self):
      for record in self:
        if self.use_road_side_assistance_gold:
                self.road_side_assistance_gold = record.insurance_policy_id.road_side_assistance_gold

    @api.onchange('use_road_side_assistance_silver')
    def onchange_use_road_side_assistance_silver(self):
      for record in self:
        if self.use_road_side_assistance_silver:
                self.road_side_assistance_silver = record.insurance_policy_id.road_side_assistance_silver

    @api.onchange('use_cover_tpl_od')
    def onchange_use_cover_tpl_od(self):
      for record in self:
        if self.use_cover_tpl_od:
                self.cover_tpl_od = record.insurance_policy_id.cover_tpl_od

    @api.onchange('use_cover_tpl_od_tpl')
    def onchange_use_cover_tpl_od_tpl(self):
      for record in self:
        if self.use_cover_tpl_od_tpl:
                self.cover_tpl_od_tpl = record.insurance_policy_id.cover_tpl_od_tpl

    @api.onchange('use_EVG')
    def onchange_use_EVG(self):
      for record in self:
        if self.use_EVG:
                self.EVG = record.insurance_policy_id.EVG

    @api.onchange('use_off_road_cover')
    def onchange_use_off_road_cover(self):
      for record in self:
        if self.use_off_road_cover:
                self.off_road_cover = record.insurance_policy_id.off_road_cover

    @api.onchange('use_gcc_cover')
    def onchange_use_gcc_cover(self):
      for record in self:
        if self.use_gcc_cover:
                self.gcc_cover = record.insurance_policy_id.gcc_cover
                          
    @api.onchange('brand_name_id')
    def onchange_brand_name_id(self):
     if self.brand_name_id:
        return {'attrs': {'brand_model_id': {'invisible': False}}}
     else:
        return {'attrs': {'brand_model_id': {'invisible': True},
                          'brand_variant_id': {'invisible': True}}}

    @api.onchange('brand_model_id')
    def onchange_brand_model_id(self):
     if self.brand_model_id:
        return {'attrs': {'brand_variant_id': {'invisible': False}}}
     else:
        return {'attrs': {'brand_variant_id': {'invisible': True}}}

    @api.onchange('insurance_category_id')
    def get_insurance_cetogary(self):
        for rec in self:
            if rec.insurance_category_id:
                # Life Insurance:
                rec.length_of_coverage_term = rec.insurance_category_id.length_of_coverage_term
                rec.life_health_history = rec.insurance_category_id.life_health_history
                rec.occupation_and_hobbies = rec.insurance_category_id.occupation_and_hobbies
                rec.family_medical_history = rec.insurance_category_id.family_medical_history
                # Health Insurance:
                rec.out_of_pocket_maximum = rec.insurance_category_id.out_of_pocket_maximum
                rec.health_history_of_insured = rec.insurance_category_id.health_history_of_insured
                rec.drug_coverage = rec.insurance_category_id.drug_coverage
                rec.healthcare_provider_network = rec.insurance_category_id.healthcare_provider_network
                # Property Insurance:
                rec.property_coverage_limits = rec.insurance_category_id.property_coverage_limits
                rec.construction_type_and_materials = rec.insurance_category_id.construction_type_and_materials
                rec.special_features_of_the_property = rec.insurance_category_id.special_features_of_the_property
                rec.personal_property_inventory = rec.insurance_category_id.personal_property_inventory
                # Liability Insurance:
                rec.desired_coverage_limits = rec.insurance_category_id.desired_coverage_limits
                rec.business_type_and_operations = rec.insurance_category_id.business_type_and_operations
                # Disability Insurance:
                rec.length_coverage_disability_period = rec.insurance_category_id.length_coverage_disability_period
                rec.disability_health_history = rec.insurance_category_id.disability_health_history
                rec.occupation_and_hobbies = rec.insurance_category_id.occupation_and_hobbies
                # Travel Insurance:
                rec.traveler_health_history = rec.insurance_category_id.traveler_health_history
                # Pet Insurance:
                rec.pet_coverage_limits = rec.insurance_category_id.pet_coverage_limits
                # Business Insurance:
                rec.business_type_operation = rec.insurance_category_id.business_type_operation
                rec.business_coverage_limits = rec.insurance_category_id.business_coverage_limits
                rec.industry_specific_risks = rec.insurance_category_id.industry_specific_risks
                # Vehicle Insurance:
                rec.driving_history = rec.insurance_category_id.driving_history
                rec.limitation_as_to_use = rec.insurance_category_id.limitation_as_to_use
                rec.limits_of_liability = rec.insurance_category_id.limits_of_liability
                rec.deductibles_under_section = rec.insurance_category_id.deductibles_under_section
                rec.special_conditions = rec.insurance_category_id.special_conditions

    @api.onchange('for_the_vehicle', 'for_trailer', 'non_electric_accessories', 'electric_accessories',
                  'value_of_cng_lpg_kit')
    def _vehicle_idv_value(self):
        for rec in self:
            rec.total_idv = rec.for_the_vehicle + rec.for_trailer + rec.non_electric_accessories + rec.electric_accessories + rec.value_of_cng_lpg_kit

    @api.onchange('basic_od', 'od_package_premium', 'service_tax', 'special_discount')
    def _own_damage_value(self):
        for record in self:
            record.final_premium = record.basic_od + record.od_package_premium + record.service_tax - record.special_discount

    # @api.onchange('basic_tp_liability', 'pa_cover_for_owner_driver', 'package_premium', 'liability_service_tax')
    # def _liability_value(self):
    #     for value in self:
    #         value.total_premium = value.basic_tp_liability + value.pa_cover_for_owner_driver + value.package_premium + value.liability_service_tax

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

    def draft_to_running(self):
        self.state = 'running'

    def running_to_expired(self):
        self.state = 'expired'
        mail_template = self.env.ref('tk_insurance_management.insurance_policy_has_expired_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    @api.model
    def create(self, vals):
        if vals.get('insurance_number', 'New') == 'New':
            vals['insurance_number'] = self.env['ir.sequence'].next_by_code(
                'insurance.information') or 'New'
        return super(InsuranceInformation, self).create(vals)

    def _compute_document_count(self):
        for rec in self:
            document_count = self.env['insured.documents'].search_count([('insured_info_id', '=', rec.id)])
            rec.document_count = document_count
        return True

    def action_insured_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'insured.documents',
            'domain': [('insured_info_id', '=', self.id)],
            'context': {'default_insured_info_id': self.id},
            'view_mode': 'tree',
            'target': 'current',
        }

    def _compute_claim_count(self):
        for rec in self:
            claim_count = self.env['claim.information'].search_count([('insurance_id', '=', rec.id)])
            rec.claim_count = claim_count
        return True

    def action_insured_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Claims',
            'res_model': 'claim.information',
            'domain': [('insurance_id', '=', self.id)],
            'context': {'default_insurance_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.depends('issue_date', 'duration')
    def _compute_time_period_date(self):
        for rec in self:
            if rec.issue_date:
                rec.expiry_date = rec.issue_date + relativedelta(months=rec.duration) - relativedelta(days=1)
            else:
                rec.expiry_date = fields.Date.today()

    @api.onchange('insurance_policy_id')
    def get_insurance_policy_amount(self):
        for rec in self:
            if rec.insurance_policy_id:
                rec.policy_amount = rec.insurance_policy_id.policy_amount

    @api.depends('total_policy_amount')
    def _compute_total_policy_amount_in_words(self):
        for record in self:
            record.total_policy_amount_in_words = num2words(record.total_policy_amount)      

    # @api.depends('insurance_policy_id.policy_amount', 'insurance_policy_id.commission_premium')
    # def _compute_commission(self):
    #     for record in self:
    #         if record.insurance_policy_id:
    #             record.commission = (record.total_policy_amount * record.insurance_policy_id.commission_premium) / 100
    #         else:
    #             record.commission = 0.0
    subject_to_approval = fields.Boolean(string="Subject to Approval", default=False)
    @api.depends(
        'premium_option',
        'total_policy_amount',
        'ins_payable',
        'subject_to_approval',
        'agent_fee_amount',
        'insurance_policy_id.commission_premium',
        'insurance_policy_id.daynatrade_premium',
        'insurance_policy_id.daynatrade_commission',
        'insurance_policy_id.daynatrade_excess',
        'insurance_policy_id.workshop_premium',
        'insurance_policy_id.workshop_excess',
        'insurance_policy_id.workshop_commission',
        'insurance_policy_id.scheme_agency_premium',
        'insurance_policy_id.scheme_agency_commission',
        'insurance_policy_id.scheme_agency_excess',
        'insurance_policy_id.non_agency_premium',
        'insurance_policy_id.non_agency_excess',
        'insurance_policy_id.non_agency_commission',
        'insurance_policy_id.agency_premium',
        'insurance_policy_id.agency_excess',
        'insurance_policy_id.agency_commission',
        'vehicle_value',
        'use_ambulance_fee',
        'insurance_policy_id.ambulance_fee',
        'insurance_policy_id.ambulance_fee_commission',
        'use_previous_cover_tpl',
        'insurance_policy_id.cover_tpl',
        'insurance_policy_id.commission_cover_tpl',
        'use_previous_insurance_charge',
        'insurance_policy_id.insurance_charge',
        'insurance_policy_id.commission_insurance_charge',
        'use_rent_a_car_5',
        'insurance_policy_id.rent_a_car_5',
        'insurance_policy_id.rent_a_car_5_commission',
        'use_rent_a_car_10',
        'insurance_policy_id.rent_a_car_10',
        'insurance_policy_id.rent_a_car_10_commission',
        'use_natural_perils',
        'insurance_policy_id.natural_perils',
        'insurance_policy_id.natural_perils_commission',
        'use_road_side_assistance_gold',
        'insurance_policy_id.road_side_assistance_gold',
        'insurance_policy_id.road_side_assistance_gold_commission',
        'use_road_side_assistance_silver',
        'insurance_policy_id.road_side_assistance_silver',
        'insurance_policy_id.road_side_assistance_silver_commission',
        'use_cover_tpl_od',
        'insurance_policy_id.cover_tpl_od',
        'insurance_policy_id.cover_tpl_od_commission',
        'use_cover_tpl_od_tpl',
        'insurance_policy_id.cover_tpl_od_tpl',
        'insurance_policy_id.cover_tpl_od_tpl_commission',
        'use_EVG',
        'insurance_policy_id.EVG',
        'insurance_policy_id.EVG_commission',
        'use_off_road_cover',
        'insurance_policy_id.off_road_cover',
        'insurance_policy_id.off_road_cover_commission',
        'use_gcc_cover',
        'insurance_policy_id.gcc_cover',
        'insurance_policy_id.gcc_cover_commission'
    )
    def _compute_commission(self):
        for record in self:
            debug_info = []

            policy = record.insurance_policy_id

            if not policy:
                record.commission = 0.0
                continue

            commission = 0.0
            base_policy_amount = record.total_policy_amount

            debug_info.append(f"[Policy ID: {policy.id}] Initial Base Policy Amount: {base_policy_amount}")

            # Step 1: Deduct coverages from base amount
            coverages = [
                ('use_ambulance_fee', 'ambulance_fee'),
                ('use_previous_cover_tpl', 'cover_tpl'),
                ('use_previous_insurance_charge', 'insurance_charge'),
                ('use_rent_a_car_5', 'rent_a_car_5'),
                ('use_rent_a_car_10', 'rent_a_car_10'),
                ('use_natural_perils', 'natural_perils'),
                ('use_road_side_assistance_gold', 'road_side_assistance_gold'),
                ('use_road_side_assistance_silver', 'road_side_assistance_silver'),
                ('use_cover_tpl_od', 'cover_tpl_od'),
                ('use_cover_tpl_od_tpl', 'cover_tpl_od_tpl'),
                ('use_EVG', 'EVG'),
                ('use_off_road_cover', 'off_road_cover'),
                ('use_gcc_cover', 'gcc_cover')
            ]

            for flag, amount_field in coverages:
                if record[flag]:
                    amount = getattr(policy, amount_field, 0.0)
                    base_policy_amount -= amount
                    debug_info.append(f" - Deducted {amount_field}: -{amount} (Flag: {flag})")

            debug_info.append(f"Adjusted Base Policy Amount: {base_policy_amount}")

            # Step 2: Default commission calculation from policy commission premium
            commission_premium = policy.commission_premium or 0.0
            base_commission = 0.0

            if commission_premium:
                base_commission = (base_policy_amount * commission_premium) / 100
                commission += base_commission
                debug_info.append(f"Base Commission: {base_policy_amount} × {commission_premium}% = {base_commission}")
            else:
                debug_info.append("No commission premium set, skipping base commission.")

            # Step 3: Add additional coverages commissions
            additional_coverages = [
                ('use_ambulance_fee', 'ambulance_fee', 'ambulance_fee_commission'),
                ('use_previous_cover_tpl', 'cover_tpl', 'commission_cover_tpl'),
                ('use_previous_insurance_charge', 'insurance_charge', 'commission_insurance_charge'),
                ('use_rent_a_car_5', 'rent_a_car_5', 'rent_a_car_5_commission'),
                ('use_rent_a_car_10', 'rent_a_car_10', 'rent_a_car_10_commission'),
                ('use_natural_perils', 'natural_perils', 'natural_perils_commission'),
                ('use_road_side_assistance_gold', 'road_side_assistance_gold', 'road_side_assistance_gold_commission'),
                ('use_road_side_assistance_silver', 'road_side_assistance_silver', 'road_side_assistance_silver_commission'),
                ('use_cover_tpl_od', 'cover_tpl_od', 'cover_tpl_od_commission'),
                ('use_cover_tpl_od_tpl', 'cover_tpl_od_tpl', 'cover_tpl_od_tpl_commission'),
                ('use_EVG', 'EVG', 'EVG_commission'),
                ('use_off_road_cover', 'off_road_cover', 'off_road_cover_commission'),
                ('use_gcc_cover', 'gcc_cover', 'gcc_cover_commission')
            ]

            for flag, amount_field, commission_field in additional_coverages:
                if record[flag]:
                    amount = getattr(policy, amount_field, 0.0)
                    commission_percent = getattr(policy, commission_field, 0.0)

                    if amount and commission_percent:
                        additional_commission = (amount * commission_percent) / 100
                        commission += additional_commission
                        debug_info.append(f"{amount_field}: {amount} × {commission_percent}% = {additional_commission}")
                    else:
                        debug_info.append(f"{amount_field}: Skipped (Amount: {amount}, Commission %: {commission_percent})")

            # Step 4: Subject to Approval check and override
            if record.subject_to_approval and record.ins_payable:
                approval_commission = record.total_policy_amount - record.ins_payable
                debug_info.append(f"Subject to Approval: {record.total_policy_amount} - {record.ins_payable} = {approval_commission}")

                # Ensure not below agent fee amount
                if approval_commission < record.agent_fee_amount:
                    debug_info.append(f"Adjusted to agent_fee_amount ({record.agent_fee_amount}) as commission was too low.")
                    approval_commission = record.agent_fee_amount

                # Apply override
                commission = approval_commission

            # Step 5: Final assignment
            debug_info.append(f"Final Commission Set: {commission}")
            record.commission = commission

            # Step 6: Logging debug info safely (disable in production if needed)
    # ✅ Real-time update in form view (onchange)
    @api.onchange('total_policy_amount', 'ins_payable', 'subject_to_approval')
    def _onchange_total_policy_amount(self):
        self._compute_commission()

        # Live warning if Subject to Approval and commission < agent fee
        if self.subject_to_approval and self.ins_payable:
            calculated_commission = self.total_policy_amount - self.ins_payable
            if calculated_commission < self.agent_fee_amount:
                return {
                    'warning': {
                        'title': _('Warning'),
                        'message': _('The commission was adjusted to the agent fee amount because the calculated commission was too low.'),
                    }
                }




    @api.depends('insurance_policy_id.policy_amount', 'total_policy_amount')
    def _compute_total_vat(self):
        for record in self:
            if record.insurance_policy_id:
                record.tax_amount = record.total_policy_amount * 0.05
            else:
                record.tax_amount = 0.0        

    @api.depends('insurance_policy_id.policy_amount', 'total_policy_amount', 'commission')
    def _compute_ins_vat_amt(self):
        for record in self:
            if record.insurance_policy_id:
                record.ins_tax_amount = (record.total_policy_amount - record.commission )* 0.05
            else:
                record.ins_tax_amount = 0.0 

    @api.depends('use_daynatrade_premium', 'vehicle_value', 'insurance_policy_id')
    def compute_daynatrade_premium(self):
        for record in self:
            if record.use_daynatrade_premium and record.insurance_policy_id:
                daynatrade_premium = (record.vehicle_value * record.insurance_policy_id.daynatrade_premium) / 100
                daynatrade_excess = record.insurance_policy_id.daynatrade_excess
                record.daynatrade_premium = max(daynatrade_premium, daynatrade_excess)
            else:
                record.daynatrade_premium = 0.0
       

    @api.depends('use_workshop_premium', 'vehicle_value', 'insurance_policy_id')
    def compute_workshop_premium(self):
        for record in self:
            if record.use_workshop_premium and record.insurance_policy_id:
                workshop_premium = (record.vehicle_value * record.insurance_policy_id.workshop_premium) / 100 
                workshop_excess = record.insurance_policy_id.workshop_excess
                record.workshop_premium = max(workshop_premium, workshop_excess)
            else:
                record.workshop_premium = 0.0

    @api.depends('use_non_agency_premium', 'vehicle_value', 'insurance_policy_id')
    def compute_non_agency_premium(self):
        for record in self:
            if record.use_non_agency_premium and record.insurance_policy_id:
                non_agency_premium = (record.vehicle_value * record.insurance_policy_id.non_agency_premium) / 100
                non_agency_excess = record.insurance_policy_id.non_agency_excess
                record.non_agency_premium = max(non_agency_premium, non_agency_excess)
            else:
                record.non_agency_premium = 0.0  

    @api.depends('use_scheme_agency_premium', 'vehicle_value', 'insurance_policy_id')
    def compute_scheme_agency_premium(self):
        for record in self:
            if record.use_scheme_agency_premium and record.insurance_policy_id:
                scheme_agency_premium = (record.vehicle_value * record.insurance_policy_id.scheme_agency_premium) / 100
                scheme_agency_excess = record.insurance_policy_id.scheme_agency_excess
                record.scheme_agency_premium = max(scheme_agency_premium, scheme_agency_excess)
            else:
                record.scheme_agency_premium = 0.0

    @api.depends('use_agency_premium', 'vehicle_value', 'insurance_policy_id')
    def compute_agency_premium(self):
        for record in self:
            if record.use_agency_premium and record.insurance_policy_id:
                agency_premium = (record.vehicle_value * record.insurance_policy_id.agency_premium) / 100
                agency_excess = record.insurance_policy_id.agency_excess
                record.agency_premium = max(agency_premium, agency_excess)
            else:
                record.agency_premium = 0.0

    @api.depends('commission')
    def _compute_policy_vat_amt(self):
        for record in self:
            if record.insurance_policy_id:
                record.policy_tax_amount = (record.commission * 0.05)
            else:
                record.policy_tax_amount = 0.0  

    @api.depends('sale_amt_excl_tax', 'commission')
    def _compute_discount(self):
     for record in self:
        if record.sale_amt_excl_tax == 0:
            record.discount = 0.0
        elif record.sale_amt_excl_tax > record.commission:
            record.discount = 0.0
        elif record.insurance_policy_id:
            record.discount = max(record.total_policy_amount - record.sale_amt_excl_tax, 0)
        else:
            record.discount = 0.0

    @api.constrains('sale_amt_excl_tax', 'commision')
    def _check_sale_amt(self):
        for record in self:
            if record.sale_amt_excl_tax > record.commission:
                raise ValidationError("Sale amount cannot exceed commission.") 
            
    @api.depends('total_policy_amount','tax_amount')
    def _compute_saleamt_inctax(self):
        for record in self:
            if record.insurance_policy_id:
                record.sale_amt_incl_tax = (record.total_policy_amount + record.tax_amount)
            else:
                record.sale_amt_incl_tax = 0.0                        

    @api.depends('insurance_policy_id.policy_amount','commission')
    def _compute_ins_payable(self):
        for record in self:
            if record.insurance_policy_id:
                record.ins_payable = (record.total_policy_amount - record.commission)
            else:
                record.ins_payable = 0.0                           

    @api.depends('commission_type', 'percentage_commission', 'policy_amount')
    def total_agent_commission(self):
        for rec in self:
            if rec.commission_type == "percentage":
                rec.total_commission = (rec.percentage_commission * rec.policy_amount) / 100
            else:
                rec.total_commission = 0.0
                                

    @api.depends('policy_amount','commission_type', 'total_commission',
                'scheme_agency_premium', 'non_agency_premium', 'daynatrade_premium',
                'workshop_premium', 'agency_premium', 'fixed_commission',
                'use_previous_cover_tpl', 'use_previous_insurance_charge',
                'use_ambulance_fee','use_rent_a_car_5','use_rent_a_car_10',
                'use_natural_perils','use_road_side_assistance_gold',
                'use_road_side_assistance_silver','use_cover_tpl_od','use_cover_tpl_od_tpl',
                'use_EVG','use_off_road_cover','use_gcc_cover','subject_to_approval')
    def _compute_total_policy_amount(self):
        for rec in self:
            policy = rec.insurance_policy_id

            addons = {
                'use_previous_cover_tpl': policy.cover_tpl,
                'use_previous_insurance_charge': policy.insurance_charge,
                'use_ambulance_fee': policy.ambulance_fee,
                'use_rent_a_car_5': policy.rent_a_car_5,
                'use_rent_a_car_10': policy.rent_a_car_10,
                'use_natural_perils': policy.natural_perils,
                'use_road_side_assistance_gold': policy.road_side_assistance_gold,
                'use_road_side_assistance_silver': policy.road_side_assistance_silver,
                'use_cover_tpl_od': policy.cover_tpl_od,
                'use_cover_tpl_od_tpl': policy.cover_tpl_od_tpl,
                'use_EVG': policy.EVG,
                'use_off_road_cover': policy.off_road_cover,
                'use_gcc_cover': policy.gcc_cover,
            }

            extra_premiums = (
                rec.daynatrade_premium + rec.workshop_premium +
                rec.non_agency_premium + rec.scheme_agency_premium + rec.agency_premium
            )

            if rec.subject_to_approval:
                # If no baseline is saved yet, use current total and store it
                if not rec.baseline_total_policy_amount:
                    base = rec.insurance_policy_id.policy_amount or 0.0
                    rec.baseline_total_policy_amount = base
                else:
                    base = rec.baseline_total_policy_amount

                total = base + sum(value for key, value in addons.items() if getattr(rec, key)) + extra_premiums
                rec.total_policy_amount = total

            else:
                base = rec.insurance_policy_id.policy_amount or 0.0
                total = base + sum(value for key, value in addons.items() if getattr(rec, key)) + extra_premiums
                rec.total_policy_amount = total
                # Reset baseline if subject_to_approval is unchecked
                rec.baseline_total_policy_amount = 0.0


    def _inverse_total_policy_amount(self):
        for rec in self:
            if rec.subject_to_approval:
                # Save manually entered value as the base
                rec.baseline_total_policy_amount = rec.total_policy_amount


    baseline_total_policy_amount = fields.Monetary(
        string="Base Policy Amount (Manual)",
        help="Stored base value when subject_to_approval is checked"
    )


    @api.onchange('total_policy_amount', 'duration')
    def _total_monthly_installment_amount(self):
        for rec in self:
            if rec.duration > 0:
                rec.monthly_installment = rec.total_policy_amount / rec.duration

    def action_create_agent_bill(self):
        for rec in self:
            if not rec.commission_type:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "Please first select the commission type.",
                        'sticky': False,
                    }
                }

            insurance = " ".join(rec.mapped('insurance_number'))
            invoice_lines = []

            if rec.commission_type == 'fixed':
                if not rec.fixed_commission:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'warning',
                            'message': "Please add the required commission fixed value before proceeding!",
                            'sticky': False,
                        }
                    }
                invoice_lines.append((0, 0, {
                    'product_id': self.env.ref('tk_insurance_management.agent_commission_bill').id,
                    'name': insurance,
                    'quantity': 1,
                    'price_unit': rec.fixed_commission,
                }))

            if rec.commission_type == 'percentage':
                if not rec.total_commission:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'warning',
                            'message': "Please add the required commission percentage value before proceeding!",
                            'sticky': False,
                        }
                    }
                invoice_lines.append((0, 0, {
                    'product_id': self.env.ref('tk_insurance_management.agent_commission_bill').id,
                    'name': insurance,
                    'quantity': 1,
                    'price_unit': rec.total_commission,
                }))

            data = {
                'partner_id': rec.agent_id.id,
                'move_type': 'in_invoice',  # Ensure it's categorized as an Incoming Bill
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
                'insurance_information_id': rec.id,
                'bill_type': 'revenue'  # Set the bill type to Revenue
            }
            agent_bill_id = self.env['account.move'].sudo().create(data)
            agent_bill_id.action_post()
            rec.agent_bill_id = agent_bill_id.id

            return {
                'type': 'ir.actions.act_window',
                'name': 'Commission Bill',
                'res_model': 'account.move',
                'res_id': agent_bill_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

            
    def action_create_vendor_bill(self):
        for rec in self:
            existing_bill = self.env['account.move'].search([
                ('insurance_information_id', '=', rec.id),
                ('move_type', '=', 'in_invoice'),
                ('bill_type', '=', 'vendor')
            ], limit=1)

            if existing_bill:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "A vendor bill with this insurance reference already exists!",
                        'sticky': False,
                    }
                }            
            
            if not rec.ins_payable:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "Please ensure both the payable and tax amounts are entered before proceeding!",
                        'sticky': False,
                    }
                }
            
            # Calculate the total amount
            total_amount = rec.ins_payable

            # Fetch a purchase tax
            tax = self.env['account.tax'].search([
                ('type_tax_use', '=', 'purchase'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            # Check if the 'ins_payable' product exists, if not, create it
            product = self.env['product.product'].search([('default_code', '=', 'ins_payable')], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': 'Insurance Payable',
                    'default_code': 'ins_payable',
                    'type': 'service',
                    'list_price': 0.0,
                    'sale_ok': False,
                    'purchase_ok': False,
                })

            # Create the bill line with tax
            bill_line = {
                'product_id': product.id,
                'name': "Insurance Payable and Tax",
                'quantity': 1,
                'price_unit': total_amount,
                'tax_ids': [(6, 0, tax.ids)] if tax else [(6, 0, [])],  # Add tax if available
            }

            # Use the correct partner or vendor field
            partner_field = self.agent_id.id  # Replace 'partner_id' with the actual field name if different

            # Prepare the vendor bill data
            invoice_lines = [(0, 0, bill_line)]
            data = {
                'partner_id': partner_field,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
                'insurance_information_id': rec.id,
                'bill_type': 'vendor',
                'company_name':rec.company_name_id.name,
                'insurance_type':rec.insurance_sub_category_id.name
            }

            # Create and post the vendor bill
            agent_bill_id = self.env['account.move'].sudo().create(data)
            agent_bill_id.action_post()
            self.agent_bill_id = agent_bill_id.id
            rec.write({'vendor_bill_created': True})
            # Return an action to open the vendor bill form view
            return {
                'type': 'ir.actions.act_window',
                'name': 'Vendor Bill',
                'res_model': 'account.move',
                'res_id': agent_bill_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
    revenue_entry = fields.Boolean(string="Revenue Entry", default=False)        
    invoice_date = fields.Date(string="Date")
    partner_id = fields.Many2one('res.partner', string="Agent")
    company_name = fields.Char(string="Company Name")
    insurance_type = fields.Char(string="Insurance Type")
    total_amount = fields.Float(string="Total Revenue", compute="_compute_total", store=True)

    @api.depends('commission', 'policy_tax_amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = rec.commission + rec.policy_tax_amount if rec.commission and rec.policy_tax_amount else 0.0
            

    def action_create_myagent_bill(self):
        for rec in self:
            # Check if a revenue record already exists for this insurance ID
            existing_record = self.env['revenue.record'].search([('insurance_information_id', '=', rec.id)], limit=1)

            if existing_record:

                # Display a warning message and prevent duplicate creation
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "A revenue entry for this insurance already exists!",
                        'sticky': False,  # Message disappears after a few seconds
                    }
                }

            # Create a new revenue record if none exists
            self.env['revenue.record'].sudo().create({
                'insurance_information_id': rec.id,
                'partner_id': rec.agent_id.id,
                'invoice_date': fields.Date.today(),
                'company_name': rec.company_name_id.name,
                'insurance_type': rec.insurance_sub_category_id.name,
                'commission': rec.commission,
                'policy_tax_amount': rec.policy_tax_amount,
            })
            rec.write({'agent_bill_created': True})
            # Return the action to show the Revenue Records related to this Insurance ID
            return {
                'type': 'ir.actions.act_window',
                'name': 'Revenue Records',
                'res_model': 'revenue.record',
                'view_mode': 'tree,form',
                'domain': [('insurance_information_id', '=', rec.id)],  # Show only relevant records
                'target': 'current'
            }

    def action_create_customer_invoice(self):
        for rec in self:
            # Check if an invoice already exists for this policy
            if rec.customer_invoice_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "An invoice has already been created for this policy.",
                        'sticky': False,
                    }
                }

            # Ensure the necessary fields exist and are set
            if not rec.insured_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "No insured associated with this insurance policy.",
                        'sticky': False,
                    }
                }

            # Find the 5% tax record, or create it if it doesn't exist
            tax_record = self.env['account.tax'].search([('amount', '=', 5)], limit=1)

            if not tax_record:
                tax_record = self.env['account.tax'].create({
                    'name': "5% VAT",
                    'amount': 5,
                    'type_tax_use': 'sale',
                    'amount_type': 'percent',
                })

            invoice_line = {
                'name': rec.insurance_number,
                'quantity': 1,
                'price_unit': rec.total_policy_amount,  # Adjust price to be tax-inclusive
                'tax_ids': [(6, 0, tax_record.ids)],  # Assign only 5% tax
            }

            data = {
                'partner_id': rec.insured_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, invoice_line)],
                'insurance_information_id': rec.id,
                'company_name': rec.company_name_id.name,
                'insurance_type': rec.insurance_sub_category_id.name
            }

            # Debugging: Confirm the correct tax calculation
            print(f"Creating invoice for insured customer: {rec.insured_id.id}, applying only 5% tax.")

            customer_invoice_id = self.env['account.move'].sudo().create(data)
            customer_invoice_id.action_post()
            rec.customer_invoice_id = customer_invoice_id.id
            rec.state = 'running'
            rec.write({'invoice_created': True})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Invoice',
                'res_model': 'account.move',
                'res_id': customer_invoice_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

        
    def action_generate_sp_bill(self):
        for rec in self:
            # Check if an existing bill was created specifically for agent_fee_amount
            existing_agent_fee_bill = self.env["account.move"].search([
                ("insurance_information_id", "=", rec.id),
                ("move_type", "=", "in_invoice"),
                
                ("invoice_line_ids.product_id.default_code", "=", "agent_fee")  # Only check agent fee bills
            ], limit=1)

            if existing_agent_fee_bill:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "warning",
                        "message": "A vendor bill for this Agent Fee Amount already exists!",
                        "sticky": False,
                    },
                }

            # Ensure agent_fee_amount is provided
            if not rec.agent_fee_amount:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "type": "warning",
                        "message": "Agent Fee Amount cannot be zero!",
                        "sticky": False,
                    },
                }

            # Get or create the "Agent Fee" product
            product = self.env["product.product"].search([("default_code", "=", "agent_fee")], limit=1)
            if not product:
                product = self.env["product.product"].create({
                    "name": "Agent Fee",
                    "default_code": "agent_fee",
                    "type": "service",
                    "list_price": 0.0,
                    "sale_ok": False,
                    "purchase_ok": True,
                })

            # Get the expense account for agent fees
            expense_account = self.env["account.account"].search([("account_type", "=", "expense")], limit=1)
            if not expense_account:
                raise ValidationError("No default expense account found. Please configure an expense account.")

            # Create the bill line for agent fee amount
            bill_line = {
                "product_id": product.id,
                "name": "Agent Commission Fee",
                "quantity": 1,
                "price_unit": rec.agent_fee_amount,
                "account_id": expense_account.id,
                "tax_ids": [(6, 0, [])],
            }

            # Ensure a valid partner (agent)
            if not rec.agent_id:
                raise ValidationError("Agent is required to generate a vendor bill!")

            # Prepare the vendor bill data
            invoice_lines = [(0, 0, bill_line)]
            bill_vals = {
                "partner_id": rec.agent_id.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines,
                "insurance_information_id": rec.id,
                "bill_type": "sp",
                'company_name':rec.company_name_id.name,
                'insurance_type':rec.insurance_sub_category_id.name
            }

            # Create and post the vendor bill
            agent_bill_id = self.env["account.move"].sudo().create(bill_vals)
            agent_bill_id.action_post()
            rec.agent_bill_id = agent_bill_id.id  # Store the bill reference
            rec.write({'sp_bill_created': True})
            # Return an action to open the vendor bill form view
            return {
                "type": "ir.actions.act_window",
                "name": "Vendor Bill",
                "res_model": "account.move",
                "res_id": agent_bill_id.id,
                "view_mode": "form",
                "target": "current",
            }


    # Seduler
    def action_create_emi_installment(self):
        self.instalment_complete = True
        date = fields.date.today()
        for rec in self:
            if rec.issue_date:
                for i in range(rec.insurance_policy_id.duration):
                    date = rec.issue_date + relativedelta(months=i)
                    data = {
                        'insurance_information_id': self.id,
                        'name': 'Installment ' + str(i + 1),
                        'installment_date': date,
                        'installment_amount': self.monthly_installment
                    }
                    self.env['insurance.emi'].create(data)
                self.state = 'running'

    def action_insurance_invoice(self):
        self.instalment_complete = True
        insurance_invoice = {
            'product_id': self.env.ref('tk_insurance_management.insurance_invoice').id,
            'name': self.insurance_policy_id.policy_name,
            'quantity': 1,
            'price_unit': self.total_policy_amount,
        }
        invoice_lines = [(0, 0, insurance_invoice)]
        data = {
            'partner_id': self.insured_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
            'insurance_information_id': self.id
        }
        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.invoice_id = invoice_id.id
        self.state = 'running'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super(InsuranceInformation, self).default_get(fields_list)
        context = self.env.context
        
        insurance_type = context.get('default_insurance_type')
        
        # Ensure Odoo creates a new record instead of reusing an existing one
        if context.get('force_create', False):
            defaults['id'] = False

        # Fetch categories dynamically from the database
        vehicle_insurance_category = self.env['insurance.category'].search(
            [('name', '=', 'Motor Insurance')], limit=1)
        third_party_sub_category = self.env['insurance.sub.category'].search(
            [('name', '=', 'Third-Party Insurance')], limit=1)
        comprehensive_sub_category = self.env['insurance.sub.category'].search(
            [('name', '=', 'Comprehensive Insurance')], limit=1)

        if insurance_type == 'third_party':
            defaults['insurance_category_id'] = vehicle_insurance_category.id if vehicle_insurance_category else False
            defaults['insurance_sub_category_id'] = third_party_sub_category.id if third_party_sub_category else False
        elif insurance_type == 'comprehensive':
            defaults['insurance_category_id'] = vehicle_insurance_category.id if vehicle_insurance_category else False
            defaults['insurance_sub_category_id'] = comprehensive_sub_category.id if comprehensive_sub_category else False

        return defaults    

class InsuranceEMI(models.Model):
    """Insurance EMI"""
    _name = 'insurance.emi'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    installment_date = fields.Date(string="Installment Date")
    installment_amount = fields.Monetary(string="Installment Amount")
    premium_type = fields.Selection(related="insurance_information_id.premium_type", string="Premium Type")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    insurance_information_id = fields.Many2one('insurance.information')
    invoice_id = fields.Many2one('account.move')
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Invoice Status")

    def action_insurance_invoice(self):
        insurance_invoice = {
            'product_id': self.env.ref('tk_insurance_management.insurance_invoice').id,
            'name': self.name,
            'quantity': 1,
            'price_unit': self.installment_amount,
        }
        invoice_lines = [(0, 0, insurance_invoice)]
        data = {
            'partner_id': self.insurance_information_id.insured_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
            'insurance_information_id': self.insurance_information_id.id
        }

        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.invoice_id = invoice_id.idpolicy
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
        
    

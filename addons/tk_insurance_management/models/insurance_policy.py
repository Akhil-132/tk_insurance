# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from io import StringIO
import csv

class InsuranceTimePeriod(models.Model):
    """Insurance Time Period"""
    _name = 'insurance.time.period'
    _description = __doc__
    _rec_name = 't_period'

    t_period = fields.Char(string="Policy Term", required=True, translate=True)
    duration = fields.Integer(string="Duration (Months)")


class InsuranceBuyingFor(models.Model):
    """Insurance Buying For"""
    _name = 'insurance.buying.for'
    _description = __doc__
    _rec_name = 'buying_for'

    buying_for = fields.Char(string="Buying For", required=True, translate=True)
    insurance_category_id = fields.Many2one('insurance.category', string="Policy Category", required=True)

    
class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'
    _rec_name = 'name'

    name = fields.Char(string="Vehicle Type")
    insurance_policy_id = fields.Many2one(
        'insurance.policy', string='Insurance Policy'
    )

class CylinderType(models.Model):
    _name = 'cylinder.type'
    _description = 'Cylinder Type'
    _rec_name = 'name'

    name = fields.Char(string="Cylinder Type")    
    

class InsurancePolicy(models.Model):
    """Insurance Policy"""
    _name = 'insurance.policy'
    _description = __doc__
    _rec_name = 'policy_name'

    company_name_id = fields.Many2one('insurance.company.name', string="Company Name")
    policy_name = fields.Char(string="Insurance Company Name", translate=True)
    policy_number = fields.Char(string="Policy Number", translate=True, readonly="True")
    _sql_constraints = [("policy_number_unique",'UNIQUE(policy_number)', "Policy Number should be unique")] 
    insurance_category_id = fields.Many2one('insurance.category', string="Policy Category", required=True)
    category = fields.Selection(related="insurance_category_id.category", string='Category')
    insurance_sub_category_id = fields.Many2one('insurance.sub.category', string="Sub Category",
                                                domain="[('insurance_category_id', '=', insurance_category_id)]",
                                                required=True)
    insurance_sub_category_name = fields.Char(string="Sub Category Name", related='insurance_sub_category_id.name', store=True)
    insurance_time_period_id = fields.Many2one('insurance.time.period', string="Policy Terms", required=True)
    duration = fields.Integer(related="insurance_time_period_id.duration", string="Duration (Months)")
    owner_age_from = fields.Float(string="Owner Age From")
    license_age_from = fields.Float(string="License Age From")
    owner_age_to = fields.Float(string="Owner Age To")
    license_age_to = fields.Float(string="Owner Age To")
    area_covered_id = fields.Many2one('insurance.area.covered', string="Area Covered")
    nationality = fields.Many2one('insurance.nationality', string="Nationality")
    nationality_percent = fields.Float(string="Nationality %")
    nationality_minimum = fields.Float(string="Minimum")
    daynatrade_premium = fields.Float(string="Premium %")
    daynatrade_excess = fields.Float(string="Minimum")
    daynatrade_driver = fields.Float(string="Driver")
    daynatrade_sum_assured_from = fields.Float(string="Sum Assured From")
    daynatrade_minimum = fields.Float(string="Excess")
    daynatrade_commission = fields.Float(string="Commission %")
    daynatrade_passenger = fields.Float(string="Passenger")
    daynatrade_sum_assured_to = fields.Float(string="Sum Assured To")
    workshop_premium = fields.Float(string="Premium %")
    workshop_excess = fields.Float(string="Minimum")
    workshop_driver = fields.Float(string="Driver")
    workshop_sum_assured_from = fields.Float(string="Sum Assured From")
    workshop_minimum = fields.Float(string="Excess")
    workshop_commission = fields.Float(string="Commission %")
    workshop_passenger = fields.Float(string="Passenger")
    workshop_sum_assured_to = fields.Float(string="Sum Assured To")
    agency_premium = fields.Float(string="Premium %")
    agency_driver = fields.Float(string="Driver")
    agency_year1 = fields.Float(string="Year 1%")
    agency_year2 = fields.Float(string="Year 2%")
    agency_year3 = fields.Float(string="Year 3%")
    agency_year4 = fields.Float(string="Year 4%")
    agency_year5 = fields.Float(string="Year 5%")
    agency_excess = fields.Float(string="Minimum")
    agency_sum_assured_from = fields.Float(string="Sum Assured From")
    agency_passenger = fields.Float(string="Passenger")
    agency_minimum = fields.Float(string="Excess")
    agency_commission = fields.Float(string="Commission %")
    agency_sum_assured_to = fields.Float(string="Sum Assured To")
    non_agency_premium = fields.Float(string="Premium %")
    non_agency_excess = fields.Float(string="Minimum")
    non_agency_driver = fields.Float(string="Driver")
    non_agency_sum_assured_from = fields.Float(string="Sum Assured From")
    non_agency_minimum = fields.Float(string="Excess")
    non_agency_commission = fields.Float(string="Commission %")
    non_agency_passenger = fields.Float(string="Passenger")
    non_agency_sum_assured_to = fields.Float(string="Sum Assured To")   
    scheme_agency_premium = fields.Float(string="Premium %")
    scheme_agency_excess = fields.Float(string="Minimum")
    scheme_agency_driver = fields.Float(string="Driver")
    scheme_agency_sum_assured_from = fields.Float(string="Sum Assured From")
    scheme_agency_minimum = fields.Float(string="Excess")
    scheme_agency_commission = fields.Float(string="Commission %")
    scheme_agency_passenger = fields.Float(string="Passenger")
    scheme_agency_sum_assured_to = fields.Float(string="Sum Assured To") 
    ambulance_fee = fields.Float(string="Ambulance Fee")
    ambulance_fee_commission = fields.Float(string="Ambulance Fee Commission")
    # ambulance_fee_refund = fields.Boolean(default=False)
    rent_a_car_5 = fields.Float(string="Rent A Car 5 days")
    rent_a_car_5_commission = fields.Float(string="Rent A Car Commission 5")
    rent_a_car_10 = fields.Float(string="Rent A Car 10 days")
    rent_a_car_10_commission = fields.Float(string="Rent A Car Commission 10")
    cover_tpl_od = fields.Float(string="Oman Cover TPL OD")
    cover_tpl_od_commission = fields.Float(string="Commission Cover TPL OD")
    cover_tpl_od_tpl = fields.Float(string="Oman Cover TPL OD TPL")
    cover_tpl_od_tpl_commission = fields.Float(string="Commission Cover TPL OD TPL")
    gcc_cover = fields.Float(string="Gcc Cover")
    gcc_cover_commission = fields.Float(string="Gcc cover commission")
    natural_perils = fields.Float(string="Natural Perils")
    natural_perils_commission = fields.Float(string="Natural Perils Commission")
    vehicle_type_id = fields.Many2one( 'insurance.vehicle.type',string="Vehicle Body Type")
    cylinder_type = fields.Many2one( 'cylinder.type',string="Cylinder Type")
    doors = fields.Integer(string="No. OF Doors")
    # _sql_constraints = [('unique_combination', 'unique(vehicle_type_id, doors, cylinder_type, company_name_id, usage)', 'Combination of Vehicle Body Type, Doors, Cylinder, Company Name & Usage Type must be unique!')     ]
    vehicle_ton = fields.Integer(string="Vehicle Ton")
    cover_tpl = fields.Float(string="Oman Cover TPL")
    commission_cover_tpl = fields.Float(string="Commission (Cover TPL)")
    insurance_charge = fields.Float(string="Insurance Charge")
    commission_insurance_charge = fields.Float(string="Commission (Insurance charge)")
    commission_premium = fields.Float(string="Commission(Premium)")
    EVG = fields.Float(string="EVG")
    EVG_commission = fields.Float(string="EVG Commission")
    road_side_assistance_gold = fields.Float(string="Road Side Assistance Gold")
    road_side_assistance_gold_commission = fields.Float(string="RSA commission Gold")
    road_side_assistance_silver = fields.Float(string="Road Side Assistance Silver")
    road_side_assistance_silver_commission = fields.Float(string="RSA commission Silver")
    driver = fields.Float(string="Driver")
    passenger = fields.Float(string="Passenger")
    usage = fields.Selection([("private","private"),("govt.","Govt."),("commercial","Commercial")])
    window_screen_cover = fields.Float(string="Window Screen Cover")
    window_screen_cover_commission = fields.Float(string="Window Screen Cover Commission")
    off_road_cover = fields.Float(string="Off Road Cover")
    off_road_cover_commission = fields.Float(string="Off Road Cover Commission")
    policy_amount = fields.Monetary(string="Total Policy Amount", required=False)    
    file_name = fields.Char(string="filename", translate=True)
    avatar = fields.Binary(string="Document")
    policy_terms_and_conditions = fields.Text(string="Terms & Conditions", translate=True)
    phone = fields.Char(related='company_id.phone', string="Phone", translate=True)
    street = fields.Char(related="company_id.street", string="Street", translate=True)
    street2 = fields.Char(related="company_id.street2", string="Street 2", translate=True)
    city = fields.Char(related="company_id.city", string="City", translate=True)
    state_id = fields.Many2one(related="company_id.state_id", string="State")
    country_id = fields.Many2one(related="company_id.country_id", string="Country")
    zip = fields.Char(related="company_id.zip", string="Zip", size=6, translate=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string="Company", required=True)

    # Life Insurance:
    life_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")])
    desired_death_amount = fields.Monetary(string="Death Amount")
    life_deductible_amount = fields.Monetary()
    length_of_coverage_term = fields.Text(string="Length of Coverage Terms", translate=True)
    life_health_history = fields.Text(string="Insured Health History", translate=True)
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies", translate=True)
    family_medical_history = fields.Text(string="Family Medical History", translate=True)

    # Health Insurance:
    health_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")])
    desired_coverage_type = fields.Selection([('individual', "Individual"), ('family', "Family"), ('group', "Group")])
    health_deductible_amount = fields.Monetary()
    out_of_pocket_maximum = fields.Text(string="Out-of-Pocket Maximum", translate=True)
    health_history_of_insured = fields.Text(translate=True)
    drug_coverage = fields.Text(string="Prescription Drug Coverage", translate=True)
    healthcare_provider_network = fields.Text(string="Preferred Healthcare Provider Network", translate=True)

    # Property Insurance:
    construct_year = fields.Integer(string="Construct Year")
    property_value = fields.Monetary()
    property_damage_coverage = fields.Monetary(string="Damage Coverage")
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
    income = fields.Monetary(string="Income")
    disability_deductible_amount = fields.Monetary()
    length_coverage_disability_period = fields.Text(string="Length of Coverage Period", translate=True)
    disability_health_history = fields.Text(translate=True)
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies", translate=True)

    # Travel Insurance:
    types_of_coverage = fields.Selection(
        [('trip_cancellation', "Trip Cancellation"), ('medical_emergency', "Medical Emergency"),
         ('lost_luggage', "Lost Luggage")], string="Type of Coverage")
    trip_coverage_amount = fields.Monetary(string="Coverage Amount")
    traveler_health_history = fields.Text(string="Traveler Health History", translate=True)

    # Pet Insurance:
    pet_desired_coverage_type = fields.Selection(
        [('accident', "Accident"), ('illness', "Illness"), ('comprehensive', "Comprehensive")], string="Coverage Type ")
    exclusions = fields.Selection(
        [('pre_existing_conditions', "Pre-Existing Conditions"), ('certain_breeds', "Certain Breeds")],
        string="Exclusions")
    accident_coverage = fields.Monetary(string="Accident Coverage Amount")
    illness_coverage = fields.Monetary(string="Illness Coverage Amount")
    pet_coverage_limits = fields.Text(string="Coverage Limits", translate=True)

    # Business Insurance:
    business_desired_coverage_type = fields.Selection(
        [('property_damage', "Property Damage"), ('liability', "Liability"), ('workers', "Workers Compensation")])
    business_property_value = fields.Monetary()
    business_type_operation = fields.Text(translate=True)
    business_coverage_limits = fields.Text(string="Business Coverage Limits", translate=True)
    industry_specific_risks = fields.Text(string=" Industry-Specific Risks", translate=True)

    # Vehicle Insurance:
    # coverage_type = fields.Selection(
    #     [('liability', "Liability"), ('collision', "Collision"), ('comprehensive', "Comprehensive")])
    driving_history = fields.Text(string="Driving History of the Insured", translate=True)
    limitation_as_to_use = fields.Text(string="Limitation as to Use", translate=True)
    limits_of_liability = fields.Text(string="Limits of Liability", translate=True)
    deductibles_under_section = fields.Text(string="Deductibles under Section", translate=True)
    special_conditions = fields.Text(string="Special Conditions", translate=True)
    vehicle_insurance_image_ids = fields.One2many('vehicle.insurance.image', 'insurance_policy_id', string="Images")

    def name_get(self):
        result = []
        seen_names = set()  # To track unique names

        for record in self:
            name = record.company_name_id.name or ''
            if name not in seen_names:
                seen_names.add(name)
                result.append((record.id, name))

        return result


    def total_policy_amount_in_words(self):
        # Implementation of converting total_policy_amount to words
        # You can use any method/library to convert the amount to words
        # Here's a simple implementation using num2words library
        
        return num2words(self.total_policy_amount)

      # Define related field to link commission_cover_tpl_amount with cover_tpl
    @api.onchange('cover_tpl')
    def _onchange_cover_tpl(self):
        # If commission_cover_tpl is not set, set it to 0
        if not self.commission_cover_tpl:
            self.commission_cover_tpl = 0.0

    @api.constrains('commission_cover_tpl')
    def _check_commission_cover_tpl(self):
        for record in self:
            # Ensure commission_cover_tpl is not greater than cover_tpl
            if record.commission_cover_tpl > record.cover_tpl:
                raise ValidationError("Commission cannot exceed Oman Cover TPL value.")

    @api.onchange('insurance_charge')
    def _onchange_insurance_charge(self):
        # If commission_cover_tpl is not set, set it to 0
        if not self.commission_insurance_charge:
            self.commission_insurance_charge = 0.0

    @api.constrains('commission_insurance_charge')
    def _check_commission_insurance_charge(self):
        for record in self:
            # Ensure commission_cover_tpl is not greater than cover_tpl
            if record.commission_insurance_charge > record.cover_tpl:
                raise ValidationError("Commission cannot exceed Insurance charge value.")  

    @api.onchange('policy_amount')
    def _onchange_policy_amount(self):
        # If commission_premium is not set, set it to 0
        if not self.commission_premium:
            self.commission_premium = 0.0

    @api.constrains('commission_premium', 'insurance_sub_category_id')
    def _check_commission_premium(self):
        for record in self:
            # Skip the validation if insurance_sub_category_id is "Comprehensive Insurance"
            if record.insurance_sub_category_id.name == "Comprehensive Insurance":
                continue

            # Ensure commission_premium is not greater than policy_amount
            if record.commission_premium > record.policy_amount:
                raise ValidationError("Commission cannot exceed Policy Amount.")
            
    
    @api.onchange('insurance_category_id')
    def get_insurance_policy(self):
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

    @api.model
    def create(self, vals):
        if not vals.get('policy_number'):
            vals['policy_number'] = self.env['ir.sequence'].next_by_code('insurance.policy') or 'NEW'
        return super(InsurancePolicy, self).create(vals)
    
    @api.constrains("vehicle_type_id", "doors", "cylinder_type", "company_name_id", "usage")
    def _check_unique_combination(self):
        for record in self:
            existing_record = self.search([
                ("vehicle_type_id", "=", record.vehicle_type_id.id),
                ("doors", "=", record.doors),
                ("cylinder_type", "=", record.cylinder_type.id),
                ("company_name_id", "=", record.company_name_id.id),
                ("usage", "=", record.usage),
                ("id", "!=", record.id)  # Exclude current record (for updates)
            ], limit=1)

            if existing_record:
                raise ValidationError(
                    f"This combination already exists in Policy Number '{existing_record.policy_number}' "
                    f"for Company '{existing_record.company_name_id.name}'."
                )
            
    @api.constrains("vehicle_type_id", "usage", "insurance_sub_category_name", "company_name_id")
    def _check_comprehensive_uniqueness(self):
        """ Ensure Comprehensive Insurance is unique within the same company """
        for record in self:
            if record.insurance_sub_category_name == "Comprehensive Insurance":  # Apply only for Comprehensive Insurance
                existing_record = self.search([
                    ("vehicle_type_id", "=", record.vehicle_type_id.id),
                    ("usage", "=", record.usage),
                    ("insurance_sub_category_name", "=", "Comprehensive Insurance"),
                    ("company_name_id", "=", record.company_name_id.id),  # Check within the same company
                    ("id", "!=", record.id)
                ], limit=1)

                if existing_record:
                    raise ValidationError(
                        f"A Comprehensive Insurance policy already exists for Vehicle Type '{record.vehicle_type_id.name}' "
                        f"and Usage '{record.usage}' under Policy Number '{existing_record.policy_number}' "
                        f"for Company '{existing_record.company_name_id.name}'."
                    )  



    @api.model
    def default_get(self, fields_list):
        defaults = super(InsurancePolicy, self).default_get(fields_list)
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

# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "All in one Insurance Management | All types Insurance Management",
    'version': "1.4",
    'description': """All in one Insurance Management""",
    'summary': "Insurance Management",
    'author': 'TechKhedut Inc.',
    'category': 'Industry',
    'website': "https://techkhedut.com",
    'depends': ['mail', 'contacts', 'account', 'base', 'sale_management', 'project'],
    'data': [
        # data
        'data/insurance_policy_sequence.xml',
        'data/insurance_management_data.xml',
        'data/insurance_invoice_data_views.xml',
        'data/claim_document_type_data_views.xml',
        'data/insured_document_type_data_views.xml',
        'data/insurance_category_data_views.xml',
        'data/sub_category_data_views.xml',
        # Security
        'security/ir.model.access.csv',
        # wizards
        'wizards/insurance_claim_views.xml',
        # Views
        'views/assets.xml',
        'views/claim_views.xml',
        'views/insurance_views.xml',
        'views/insurance_policy_views.xml',
        'views/insurance_emi_views.xml',
        'views/insurance_time_period_views.xml',
        'views/insured_document_views.xml',
        'views/claim_document_views.xml',
        'views/claim_document_type_views.xml',
        'views/insured_document_type_views.xml',
        'views/model_views.xml',
        'views/insurance_sub_category_views.xml',
        'views/insurance_category_views.xml',
        'views/insurance_nominee_views.xml',
        'views/insurance_buying_for_views.xml',
        'views/vehicle_insurance_images_views.xml',
        'views/insurance_testnominee_views.xml',
        'views/insurance_company_name_views.xml',
        'views/insurance_vehicle_type_views.xml',
        'views/insurance_area_covered_views.xml',
        'views/insurance_nationality_views.xml',
        # report
        'report/insurance_report.xml',
        'report/insurance_claim_report.xml',
        'report/vehicle_insurance_report.xml',
        # data
        'data/insurance_expired_mail.xml',
        'data/claim_approved_mail.xml',
        # Menus
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tk_insurance_management/static/src/xml/template.xml',
            'tk_insurance_management/static/src/css/lib/dashboard.css',
            'tk_insurance_management/static/src/css/style.scss',
            'tk_insurance_management/static/src/js/lib/apexcharts.js',
            'tk_insurance_management/static/src/js/insurance_dashboard.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 99,
    'currency': 'EUR'
}

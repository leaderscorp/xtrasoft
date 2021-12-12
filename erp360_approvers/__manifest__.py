# -*- coding: utf-8 -*-
{
    'name': "erp360_approvers",
    'shortdesc':'ERP-360-Approvers',
    'summary': """
        Approval Workflow""",

    'description': """
        Approval Workflow
    """,

    'author': "ESSl, KICS, UET Lahore",
    'website': "https://www.kics.edu.pk/essl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Other',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr_expense'],

    # always loaded
    'data': [
        'account/security/groups.xml',
        'account/security/ir.model.access.csv',
        'account/views/views.xml',
        'account/views/inherit_report_invoice.xml',
        'account/views/inherit_expense_report.xml'        
        
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
#         'demo/demo.xml',
        
    ],
}
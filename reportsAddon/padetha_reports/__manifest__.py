# -*- coding: utf-8 -*-
{
    'name': 'Template Report Module',
    'version': '1.0',
    'summary': 'Basic structure for QWeb report in Odoo',
    'category': 'Reporting',
    'author': 'YHA',
    'depends': ['base', 'sale'],
    'data': [
        'reports/sale_a5_voucher_template.xml',
        'reports/report_action.xml',
        'reports/sales_customize_template.xml',
    ],
    'installable': True,
    'application': False,
}
# -*- coding: utf-8 -*-
{
    'name': "production_flow",

    'summary': "Production Flow Management",

    'description': """
Production Flow Management
==========================

This application enables you to manage production flows


You can manage:
---------------
* Vendor capabilities and capacities
* Production flow templates
* Production scheduling
* Production status updates and tracking
    """,

    'author': "Batom",
    'website': "http://www.greattaiwangear.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
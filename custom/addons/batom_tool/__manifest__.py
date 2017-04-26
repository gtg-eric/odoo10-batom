# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Batom Tool Management',
    'version': '10.0.1.0.1',
    'category': 'Tools',
    'author': "Eric Chou, Batom Co., Ltd.",
    'website': 'http://www.greattaiwangear.com/',
    'license': 'AGPL-3',
#    'images': [
#    ],
    'depends': [
        'product',
        'batom_mrp',
    ],
    'data': [
        'security/tool_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

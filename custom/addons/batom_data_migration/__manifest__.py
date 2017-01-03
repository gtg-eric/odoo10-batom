# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Batom Data Migration',
    'version': '10.0.1.0.1',
    'category': 'Tools',
    'author': "Eric Chou, Batom Co., Ltd.",
    'website': 'http://www.greattaiwangear.com/',
    'license': 'AGPL-3',
#    'images': [
#    ],
    'depends': [
        'base',
        'base_external_dbsource',
        'stock',
        'account',
        'mrp',
    ],
    'data': [
        'views/batom_data_migration.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
}

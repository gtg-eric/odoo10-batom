# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class BatomMrpBom(models.Model):
    #_name = 'batom.mrp.bom'
    _inherit = 'mrp.bom'
    
    x_batom_bom_no = fields.Integer('CHI BoM #')
    x_version_description = fields.Char('Version Description')

class BatomMrpWorkcenter(models.Model):
    #_name = 'batom.mrp.workcenter'
    _inherit = 'mrp.workcenter'
    
    x_supplier_id = fields.Many2one('res.partner', 'Supplier for Generated Work Center')
    x_process_id = fields.Many2one('product.template', 'Process for Generated Work Center')

class BatomMrpRouting(models.Model):
    #_name = 'batom.mrp.routing'
    _inherit = 'mrp.routing'
    
    x_product_id = fields.Many2one('product.template', 'Product for Generated Routing')
    x_batom_bom_no = fields.Integer('CHI BoM # for Generated Routing')

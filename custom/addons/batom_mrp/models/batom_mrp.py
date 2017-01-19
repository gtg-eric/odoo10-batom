# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

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

class BatomMrpWorkorder(models.Model):
    #_name = 'batom.mrp.workorder'
    _inherit = 'mrp.workorder'

    qty_in = fields.Float(
        'Quantity received', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products received and to be handled by this work order")
    qty_out = fields.Float(
        'Quantity handed out', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already handled and hanaded out by this work order")
    qty_wasted = fields.Float(
        'Quantity wasted', default=0.0,
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products wasted in the process by this work order")

    @api.model
    def create(self, values):
        if values.get('production_id', False):
            production = self.env["mrp.production"].browse(values['production_id']);
            if (production.product_id.tracking == 'lot' and
                    (not values.get('final_lot_id', False) or values['final_lot_id'] == None)):
                lots = self.env["stock.production.lot"].search([('name', '=', production.name)])
                if len(lots) > 0:
                    values['final_lot_id'] = lots[0].id
                else:
                    lot = self.env["stock.production.lot"].create({
                        'product_id': production.product_id.id,
                        'name': production.name,
                        'product_uom_id': production.product_id.uom_id.id,
                        })
                    values['final_lot_id'] = lot.id
        workorder = super(BatomMrpWorkorder, self).create(values)
        return workorder
    
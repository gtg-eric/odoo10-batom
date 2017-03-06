# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import math
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class BatomMrpRoutingWorkcenter(models.Model):
    #_name = "batom.mrp.routing.workcenter"
    _inherit = "mrp.routing.workcenter"
    
    inspection_method = fields.Selection([
        ('self', 'Self QC'),
        ('percentage', 'By Percentage'),
        ('all', 'All')],
        string='Inspection Method',
        default='percentage', index=True,
        )
    auto_received = fields.Boolean(
        string='Automatic Receving Input Parts',
        default=False, index=True,
        )

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

class BatomMrpProduction(models.Model):
    #_name = 'batom.mrp.production'
    _inherit = 'mrp.production'

    x_product_qty_origin = fields.Float(
        'Original Quantity To Produce',
        readonly=True, required=True,
        )

    @api.model
    def create(self, values):
        if not values.get('x_product_qty_origin'):
            values['x_product_qty_origin'] = values['product_qty']
        return super(BatomMrpProduction, self).create(values)

    @api.multi
    def _generate_workorders(self, exploded_boms):
        workorders = super(BatomMrpProduction, self)._generate_workorders(exploded_boms)
        prev_workorder = False
        for workorder in workorders:
            values = {}
            if workorder.operation_id:
                values['inspection_method'] = workorder.operation_id.inspection_method
                values['auto_received'] = workorder.operation_id.auto_received
            if prev_workorder:
                values['prev_work_order_id'] = prev_workorder.id
                values['inprocess_move_trigger'] = workorder.inprocess_move_trigger + 1
            if values:
                workorder.write(values)
            prev_workorder = workorder
        return workorders

class BatomChangeProductionQty(models.TransientModel):
    #_name = 'batom.change.production.qty'
    _inherit = 'change.production.qty'
    triggered_by_scrapping = fields.Boolean(default=False)

    @api.multi
    def change_prod_qty(self, triggered_by_scrapping = False):
        super(BatomChangeProductionQty, self).change_prod_qty()
        for wizard in self:
            production = wizard.mo_id
            if production.exists():
                if not self.triggered_by_scrapping:
                    # manual update from manufacture order 
                    scrap_qty = 0
                    crap_product_quants_data = self.env['stock.scrap'].read_group(
                        [('production_id', '=', production.id)],
                        ['product_id', 'scrap_qty'],
                        ['product_id']
                        )
                    for product_scrap_qty in crap_product_quants_data:
                        bom_product_quants = self.env['mrp.bom.line'].search([
                            ('bom_id', '=', production.bom_id.id), ('product_id', '=', product_scrap_qty['product_id'][0])
                            ])
                        bom_product_quant_total = sum(bom_product_quants.mapped('product_qty'))
                        if bom_product_quant_total > 0:
                            new_scrap_qty = math.ceil(product_scrap_qty['scrap_qty'] / bom_product_quant_total)
                            if scrap_qty < new_scrap_qty:
                                scrap_qty = new_scrap_qty
                    production.x_product_qty_origin = production.product_qty + scrap_qty
                for wo in production.workorder_ids:
                    operation = wo.operation_id
                    if production.product_id.tracking == 'serial':
                        quantity = 1.0
                    else:
                        quantity = wo.qty_production - wo.qty_processed
                        quantity = quantity if (quantity > 0) else 0
                    wo.qty_producing = quantity
                    if wo.qty_produced < wo.qty_production and wo.state == 'done':
                        wo.state = 'progress'
                    
                    wo.inprocess_move_trigger = wo.inprocess_move_trigger + 1

class BatomMrpWorkorder(models.Model):
    #_name = 'batom.mrp.workorder'
    _inherit = 'mrp.workorder'

    prev_work_order_id = fields.Many2one('mrp.workorder', "Previous Work Order")
    inprocess_move_trigger = fields.Integer('field recomputing trigger', default=0)
    inspection_method = fields.Selection([
        ('self', 'Self QC'),
        ('percentage', 'By Percentage'),
        ('all', 'All')],
        string='Inspection Method',
        default='percentage', index=True,
        )
    auto_received = fields.Boolean(
        string='Automatic Receving Input Parts',
        default=False, index=True,
        )
    qty_processed = fields.Float(
        'Quantity', compute='_compute_qty_processed',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed by this work order")
    qty_arrived = fields.Float(
        'Quantity Arrived', compute='_compute_qty_arrived',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products to be received by this work order")
    qty_in = fields.Float(
        'Quantity Received', compute='_compute_qty_in',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products received and to be processed by this work order")
    qty_to_qc = fields.Float(
        'Quantity to QC', compute='_compute_qty_to_qc',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed and ready for inspection by this work order")
    qty_qc = fields.Float(
        'Quantity under QC', compute='_compute_qty_qc',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed and under inspection by this work order")
    qty_qcok = fields.Float(
        'Quantity Passed QC', compute='_compute_qty_qcok',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed and inspected by this work order")
    qty_out = fields.Float(
        'Quantity Out', compute='_compute_qty_out',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed and sent to the next process")
    qty_produced = fields.Float(
        'Quantity Produced', compute='_compute_qty_produced',
        readonly=True, store=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products already processed and accepted by this work order")
    qty_wasted = fields.Float(
        'Quantity wasted', compute='_compute_qty_wasted',
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products wasted in the process by this work order")
    qty_wasted_accumulated = fields.Float(
        'Quantity wasted accumulated', compute='_compute_qty_wasted_accumulated',
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="The number of products wasted up to this work order")

    @api.model
    def create(self, values):
        if values.get('production_id', False):
            production = self.env["mrp.production"].browse(values['production_id']);
            if (production.product_id.tracking == 'lot' and
                    (not values.get('final_lot_id', False) or not values['final_lot_id'])):
                lots = self.env["stock.production.lot"].search([
                    ('product_id', '=', production.product_id.id),
                    ('name', '=', production.name)
                    ])
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

    @api.one
    @api.depends('production_id.product_qty', 'qty_produced', 'inprocess_move_trigger')
    def _compute_is_produced(self):
        self.is_produced = (self.qty_produced >= self.production_id.product_qty and
            self.qty_produced >= self.qty_in - self.qty_wasted and
            (not self.prev_work_order_id or self.prev_work_order_id.is_produced))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_processed(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['processed', 'qc', 'qcok', 'transport', 'done']),
            ])
        self.qty_processed = sum(moves.mapped('product_qty'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_arrived(self):
        if self.prev_work_order_id:
            moves = self.env['batom.mrp.inprocess_move'].search([
                ('production_id', '=', self.production_id.id),
                ('source_workorder_id', '=', self.prev_work_order_id.id),
                ('state', 'in', ['transport']),
                ])
            self.qty_arrived = sum(moves.mapped('product_qty'))
        else:
            self.qty_arrived = 0

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_in(self):
        if self.prev_work_order_id:
            moves = self.env['batom.mrp.inprocess_move'].search([
                ('production_id', '=', self.production_id.id),
                ('source_workorder_id', '=', self.prev_work_order_id.id),
                ('state', 'in', ['done']),
                ])
            self.qty_in = sum(moves.mapped('product_qty'))
        else:
            quants = self.env['stock.scrap'].search([
                ('production_id', '=', self.production_id.id),
                ('workorder_id', '=', False)
                ])
            self.qty_in = self.production_id.x_product_qty_origin - sum(quants.mapped('x_production_qty_to_decrease'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_to_qc(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['processed']),
            ])
        self.qty_to_qc = sum(moves.mapped('product_qty'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_qc(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['qc']),
            ])
        self.qty_qc = sum(moves.mapped('product_qty'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_qcok(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['qcok']),
            ])
        self.qty_qcok = sum(moves.mapped('product_qty'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_out(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['transport']),
            ])
        self.qty_out = sum(moves.mapped('product_qty'))

    @api.one
    @api.depends('inprocess_move_trigger')
    def _compute_qty_produced(self):
        moves = self.env['batom.mrp.inprocess_move'].search([
            ('production_id', '=', self.production_id.id),
            ('source_workorder_id', '=', self.id),
            ('state', 'in', ['done']),
            ])
        self.qty_produced = sum(moves.mapped('product_qty'))

    @api.one
    def _compute_qty_wasted(self):
        quants = self.env['stock.scrap'].search([
            ('production_id', '=', self.production_id.id),
            ('workorder_id', '=', self.id)
            ])
        self.qty_wasted = sum(quants.mapped('x_production_qty_to_decrease'))

    @api.one
    def _compute_qty_wasted_accumulated(self):
        if self.prev_work_order_id:
            self.qty_wasted_accumulated = self.qty_wasted + self.prev_work_order_id.qty_wasted_accumulated
        else:
            quants = self.env['stock.scrap'].search([
                ('production_id', '=', self.production_id.id),
                ('workorder_id', '=', False)
                ])
            self.qty_wasted_accumulated = self.qty_wasted + sum(quants.mapped('x_production_qty_to_decrease'))
            

class BatomMrpWorkcenter(models.Model):
    #_name = 'batom.mrp.workcenter.productivity.loss'
    _inherit = 'mrp.workcenter.productivity.loss'

    name = fields.Char('Reason', required=True, translate=True)

class BatomStockScrap(models.Model):
    _inherit = 'stock.scrap'
    x_update_production_qty = fields.Boolean('Update quantity of manufacturing oder accordingly', default=True)
    x_production_qty_to_decrease = fields.Float('Production quantity to descrease', default=0.0)

    @api.multi
    def do_scrap(self):
        rc = super(BatomStockScrap, self).do_scrap()
        if rc:
            for scrap in self:
                if scrap.x_update_production_qty and scrap.workorder_id != False:
                    production = scrap.production_id
                    if production.exists():
                        bom_product_quants = self.env['mrp.bom.line'].search([('bom_id', '=', scrap.production_id.bom_id.id), ('product_id', '=', scrap.product_id.id)])
                        bom_product_quant_total = sum(bom_product_quants.mapped('product_qty'))
                        if bom_product_quant_total > 0:
                            scrap_product_quants = self.env['stock.scrap'].search([('production_id', '=', scrap.production_id.id), ('product_id', '=', scrap.product_id.id)])
                            scrap_product_quant_total = sum(scrap_product_quants.mapped('scrap_qty'))
                            total_qty_to_decrease = math.ceil(scrap_product_quant_total / bom_product_quant_total)
                            if production.x_product_qty_origin < production.product_qty:
                                qty_to_decrease = 0
                            else:
                                qty_to_decrease = total_qty_to_decrease - (production.x_product_qty_origin - production.product_qty)
                            if qty_to_decrease > 0:
                                scrap.x_production_qty_to_decrease = qty_to_decrease
                                if production.product_qty > qty_to_decrease:
                                    product_qty = production.product_qty - qty_to_decrease
                                else:
                                    product_qty = 0
                                change_product_qty = self.env['change.production.qty'].create({
                                        'mo_id': self.production_id.id,
                                        'product_qty': product_qty,
                                        'triggered_by_scrapping': True,
                                    })
                                change_product_qty.change_prod_qty()
                                
                                for wo in production.workorder_ids:
                                    operation = wo.operation_id
                                    if production.product_id.tracking == 'serial':
                                        quantity = 1.0
                                    else:
                                        quantity = wo.qty_production - wo.qty_processed
                                        quantity = quantity if (quantity > 0) else 0
                                    wo.qty_producing = quantity
                                    if wo.qty_produced < wo.qty_production and wo.state == 'done':
                                        wo.state = 'progress'
                                    
                                move_lots = self.env['stock.move.lots'].search([
                                    ('production_id', '=', scrap.production_id.id),
                                    ('product_id', '=', scrap.product_id.id),
                                    ('lot_id', '=', scrap.lot_id.id),
                                    ])
                                i = 0
                                while qty_to_decrease > 0 and i < len(move_lots):
                                    if move_lots[i].quantity_done > qty_to_decrease:
                                        move_lots[i].quantity_done = move_lots[i].quantity_done - qty_to_decrease
                                        qty_to_decrease = 0
                                    elif move_lots[i].quantity_done > 0:
                                        qty_to_decrease = qty_to_decrease - move_lots[i].quantity_done
                                        move_lots[i].quantity_done = 0
                                    i = i + 1
                                    
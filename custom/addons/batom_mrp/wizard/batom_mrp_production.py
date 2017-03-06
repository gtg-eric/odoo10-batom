# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math

class BatomRecordProduction(models.Model):
    _name = 'batom.record.production'
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order', required=True)
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    material_id = fields.Many2one('product.product', 'Material')
    qty_processed_addition = fields.Float('Processed Quantity Addition',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be added to the quanity processed")
    consumed_lot_id = fields.Many2one('stock.production.lot', 'Consumed Lot',
        domain="[('product_id', '=', material_id)]")
    qty_to_inspect = fields.Float('Quantity to Send for Inspection',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity to be sent for inspection")
    qty_to_receive = fields.Float('Quantity to Receive',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be added to the quanity received")
    qty_to_reject = fields.Float('Quantity to Reject Receiving',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be returned to the previous process")
    qty_to_qcok = fields.Float('Quantity to be QC passed',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be added for sending to the next process")
    qty_to_return = fields.Float('Quantity to be returned',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be descreased from the quantity to be inspected")
    qty_to_rework = fields.Float('Quantity to be reworked',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be descreased from the quantity processed")
    qty_to_next_process = fields.Float('Quantity to be sent to next process',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be added to the quantity out")
    qty_processed_to_new_routing = fields.Float('Quantity Processed to New Routing',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be removed from current production order and a new sub-production order will be created accordingly")
    qty_unprocessed_to_new_routing = fields.Float('Quantity Unprocessed to New Routing',
        digits=dp.get_precision('Product Unit of Measure'),
        help="The quantity will be removed from current production order and a new sub-production order will be created accordingly")

    @api.model
    def default_get(self, fields):
        res = super(BatomRecordProduction, self).default_get(fields)
        if 'workorder_id' in fields and not res.get('workorder_id') and self._context.get('active_model') == 'mrp.workorder' and self._context.get('active_id'):
            res['workorder_id'] = self._context['active_id']
        workorder = False
        production = False
        product = False
        if res.get('workorder_id'):
            workorder = self.env['mrp.workorder'].browse(res.get('workorder_id'))
            production = workorder.production_id
            product = workorder.product_id
        if 'production_id' in fields and not res.get('production_id') and production:
            res['production_id'] = production.id
        if 'product_id' in fields and not res.get('product_id') and product:
            res['product_id'] = product.id
        if 'material_id' in fields and not res.get('material_id') and workorder:
            if workorder.active_move_lot_ids:
                res['material_id'] = workorder.active_move_lot_ids[0].product_id.id
        if 'qty_processed_addition' in fields and not res.get('qty_processed_addition') and workorder:
            qty = workorder.qty_in - workorder.qty_processed - workorder.qty_wasted
            res['qty_processed_addition'] = qty if qty > 0 else 0
        if 'qty_to_inspect' in fields and not res.get('qty_to_inspect') and workorder:
            qty = workorder.qty_processed - self._in_process_move_qty_by_state(workorder, False, ['qc', 'qcok', 'transport', 'done'])
            res['qty_to_inspect'] = qty if qty > 0 else 0
        if 'qty_to_receive' in fields and not res.get('qty_to_receive') and workorder:
            qty = self._in_process_move_qty_by_state(False, workorder, ['transport'])
            res['qty_to_receive'] = qty if qty > 0 else 0
        if 'qty_to_reject' in fields and not res.get('qty_to_reject') and workorder:
            qty = self._in_process_move_qty_by_state(False, workorder, ['transport'])
            res['qty_to_reject'] = qty if qty > 0 else 0
        if 'qty_to_qcok' in fields and not res.get('qty_to_qcok') and workorder:
            qty = self._in_process_move_qty_by_state(workorder, False, ['qc'])
            res['qty_to_qcok'] = qty if qty > 0 else 0
        if 'qty_to_return' in fields and not res.get('qty_to_return') and workorder:
            qty = self._in_process_move_qty_by_state(workorder, False, ['qc'])
            res['qty_to_return'] = qty if qty > 0 else 0
        if 'qty_to_rework' in fields and not res.get('qty_to_rework') and workorder:
            qty = workorder.qty_processed - self._in_process_move_qty_by_state(workorder, False, ['qc', 'qcok', 'transport', 'done'])
            res['qty_to_rework'] = qty if qty > 0 else 0
        if 'qty_to_next_process' in fields and not res.get('qty_to_next_process') and workorder:
            qty = self._in_process_move_qty_by_state(workorder, False, ['qcok'])
            res['qty_to_next_process'] = qty if qty > 0 else 0
        if 'qty_processed_to_new_routing' in fields and not res.get('qty_processed_to_new_routing') and workorder:
            qty = workorder.qty_processed - self._in_process_move_qty_by_state(workorder, False, ['qc', 'qcok', 'transport', 'done'])
            res['qty_processed_to_new_routing'] = qty if qty > 0 else 0
        if 'qty_unprocessed_to_new_routing' in fields and not res.get('qty_unprocessed_to_new_routing') and workorder:
            qty = workorder.qty_in - workorder.qty_processed - workorder.qty_wasted
            res['qty_unprocessed_to_new_routing'] = qty if qty > 0 else 0
        
        return res

    @api.multi
    def receive_product(self):
        self.ensure_one()
        error_message = False
        if self.qty_to_receive <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(False, self.workorder_id, ['transport'])
            if self.qty_to_receive > max_qty:
                error_message = _("The quantity to be received, %d, is greater than available %d.")%(self.qty_to_receive, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_receive, False, self.workorder_id, ['transport'], 'done')
                if self.workorder_id.prev_work_order_id:
                    self.workorder_id.prev_work_order_id.qty_producing = self.qty_to_receive
                    self.workorder_id.prev_work_order_id.record_production()
                self._trigger_field_recomputing(self.workorder_id, True, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def reject_product(self):
        self.ensure_one()
        error_message = False
        if self.qty_to_reject <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(False, self.workorder_id, ['transport'])
            if self.qty_to_reject > max_qty:
                error_message = _("The quantity to be rejected, %d, is greater than available %d.")%(self.qty_to_reject, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_reject, False, self.workorder_id, ['transport'], 'qc')
                self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def add_processed_qty(self):
        self.ensure_one()
        error_message = False
        if self.qty_processed_addition <= 0:
            error_message = _("Please enter a quantity higher than 0 for the processed quantity to be added.")
        else:
            max_addition = self.workorder_id.qty_in - self.workorder_id.qty_processed - self.workorder_id.qty_wasted
            if self.qty_processed_addition > max_addition:
                error_message = _("The quantity to be added, %d, is greater than available %d.")%(self.qty_processed_addition, max_addition)
            elif self.material_id:
                if not self.consumed_lot_id:
                    error_message = _("Please provide a lot for the consumed material.")
                else:
                    quants = self.env['stock.quant'].search([
                        ('location_id.usage', '=', 'internal'),
                        ('reservation_id', '=', False),
                        ('product_id', '=', self.material_id.id),
                        ('lot_id', '=', self.consumed_lot_id.id),
                        ])
                    qty_material = sum(quants.mapped('qty'))
                    if qty_material < self.qty_processed_addition:
                        error_message = _("The quantity of the lot you selected is %d that is leass than %d.")%(qty_material, self.qty_processed_addition)
                if not error_message:
                    self.workorder_id.qty_producing = self.qty_processed_addition
                    if self.workorder_id.active_move_lot_ids and len(self.workorder_id.active_move_lot_ids) > 0:
                        self.workorder_id.active_move_lot_ids[0].write({
                            'qty': self.qty_processed_addition,
                            'quantity_done': self.qty_processed_addition,
                            'lot_id': self.consumed_lot_id.id,
                            })
                    current_lot_id = self.workorder_id.final_lot_id
                    self.workorder_id.record_production()
                    if self.workorder_id.qty_producing > 0:
                        self.workorder_id.final_lot_id = current_lot_id
                    self.env['batom.mrp.inprocess_move'].create({
                        'name': self.production_id.name + u'/' + self.workorder_id.name,
                        'product_id': self.product_id.id,
                        'product_qty': self.qty_processed_addition,
                        'production_id': self.production_id.id,
                        'source_workorder_id': self.workorder_id.id,
                        'dest_workorder_id': self.workorder_id.next_work_order_id.id,
                        'source_operation_id': self.workorder_id.operation_id.id,
                        'dest_operation_id': self.workorder_id.next_work_order_id.operation_id.id,
                        'source_partner_id': self.workorder_id.operation_id.workcenter_id.x_supplier_id.id,
                        'dest_partner_id': self.workorder_id.next_work_order_id.operation_id.workcenter_id.x_supplier_id.id,
                        'state': 'done',
                        })
                    self._trigger_field_recomputing(self.workorder_id, False, True)
            else:
                max_addition = self.workorder_id.qty_in - self.workorder_id.qty_processed - self.workorder_id.qty_wasted
                if self.qty_processed_addition > max_addition:
                    error_message = _("The quantity to be added, %d, is greater than available %d.")%(self.qty_processed_addition, max_addition)
                else:
                    if self.workorder_id.inspection_method == 'self':
                        state = 'qcok'
                    else:
                        state = 'processed'
                    self.env['batom.mrp.inprocess_move'].create({
                        'name': self.production_id.name + u'/' + self.workorder_id.name,
                        'product_id': self.product_id.id,
                        'product_qty': self.qty_processed_addition,
                        'production_id': self.production_id.id,
                        'source_workorder_id': self.workorder_id.id,
                        'dest_workorder_id': self.workorder_id.next_work_order_id.id,
                        'source_operation_id': self.workorder_id.operation_id.id,
                        'dest_operation_id': self.workorder_id.next_work_order_id.operation_id.id,
                        'source_partner_id': self.workorder_id.operation_id.workcenter_id.x_supplier_id.id,
                        'dest_partner_id': self.workorder_id.next_work_order_id.operation_id.workcenter_id.x_supplier_id.id,
                        'state': state,
                        })
                    self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def send_inspection(self):
        self.ensure_one()
        error_message = False
        if self.qty_to_inspect <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(self.workorder_id, False, ['processed'])
            if self.qty_to_inspect > max_qty:
                error_message = _("The quantity to inspect, %d, is greater than available %d.")%(self.qty_to_inspect, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_inspect, self.workorder_id, False, ['processed'], 'qc')
                self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def inspection_ok(self):
        error_message = False
        if self.qty_to_qcok <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(self.workorder_id, False, ['qc'])
            if self.qty_to_qcok > max_qty:
                error_message = _("The quantity for QC passed, %d, is greater than available %d.")%(self.qty_to_qcok, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_qcok, self.workorder_id, False, ['qc'], 'qcok')
                self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def inspection_return(self):
        error_message = False
        if self.qty_to_return <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(self.workorder_id, False, ['qc'])
            if self.qty_to_return > max_qty:
                error_message = _("The quantity to return, %d, is greater than available %d.")%(self.qty_to_return, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_return, self.workorder_id, False, ['qc'], 'processed')
                self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def rework(self):
        self.ensure_one()
        error_message = False
        if self.qty_to_rework <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(self.workorder_id, False, ['processed'])
            if self.qty_to_rework > max_qty:
                error_message = _("The quantity to rework, %d, is greater than available %d.")%(self.qty_to_rework, max_qty)
            else:
                self._change_in_process_move_state(self.qty_to_rework, self.workorder_id, False, ['processed'], 'cancel')
                self._trigger_field_recomputing(self.workorder_id, False, False)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def to_next(self):
        self.ensure_one()
        error_message = False
        if self.qty_to_next_process <= 0:
            error_message = _("Please enter a quantity higher than 0 for the quantity to receieve.")
        else:
            max_qty = self._in_process_move_qty_by_state(self.workorder_id, False, ['qcok'])
            if self.qty_to_next_process > max_qty:
                error_message = _("The quantity to send to next process, %d, is greater than available %d.")%(self.qty_to_next_process, max_qty)
            else:
                if not self.workorder_id.next_work_order_id or self.workorder_id.next_work_order_id.auto_received:
                    self._change_in_process_move_state(self.qty_to_next_process, self.workorder_id, False, ['qcok'], 'done')
                    self.workorder_id.qty_producing = self.qty_to_next_process
                    self.workorder_id.record_production()
                else:
                    self._change_in_process_move_state(self.qty_to_next_process, self.workorder_id, False, ['qcok'], 'transport')
                self._trigger_field_recomputing(self.workorder_id, False, True)
            
        if error_message:
            raise UserError(error_message)

    @api.multi
    def processed_to_new_routing(self):
        self.ensure_one()
        return

    @api.multi
    def unprocessed_to_new_routing(self):
        self.ensure_one()
        return

    def _in_process_move_qty_by_state(self, source_workorder, dest_workorder, states):
        quants = False
        if source_workorder:
            quants = self.env['batom.mrp.inprocess_move'].search([
                ('source_workorder_id', '=', source_workorder.id),
                ('state', 'in', states),
                ])
        elif dest_workorder:
            quants = self.env['batom.mrp.inprocess_move'].search([
                ('dest_workorder_id', '=', dest_workorder.id),
                ('state', 'in', states),
                ])
        return sum(quants.mapped('product_qty')) if quants else 0

    def _change_in_process_move_state(self, qty_to_change, source_workorder, dest_workorder, from_states, to_state):
        quants = False
        if source_workorder:
            quants = self.env['batom.mrp.inprocess_move'].search([
                ('source_workorder_id', '=', source_workorder.id),
                ('state', 'in', from_states),
                ])
        elif dest_workorder:
            quants = self.env['batom.mrp.inprocess_move'].search([
                ('dest_workorder_id', '=', dest_workorder.id),
                ('state', 'in', from_states),
                ])
        
        if quants and len(quants) > 0:
            for quant in quants:
                if qty_to_change <= 0:
                    break
                else:
                    if quant.product_qty <= qty_to_change:
                        qty_to_change = qty_to_change - quant.product_qty
                        quant.state = to_state
                    else:
                        quant.product_qty = quant.product_qty - qty_to_change
                        self.env['batom.mrp.inprocess_move'].create({
                            'name': quant.name,
                            'product_id': quant.product_id.id,
                            'product_qty': qty_to_change,
                            'production_id': quant.production_id.id,
                            'source_workorder_id': quant.source_workorder_id.id,
                            'dest_workorder_id': quant.dest_workorder_id.id,
                            'source_operation_id': quant.source_operation_id.id,
                            'dest_operation_id': quant.dest_operation_id.id,
                            'source_partner_id': quant.source_partner_id.id,
                            'dest_partner_id': quant.dest_partner_id.id,
                            'state': to_state,
                            })
                        qty_to_change = 0

    def _trigger_field_recomputing(self, workorder, trigger_prev, trigger_next):
        workorder.inprocess_move_trigger = workorder.inprocess_move_trigger + 1
        if trigger_prev and workorder.prev_work_order_id:
            workorder.prev_work_order_id.inprocess_move_trigger = workorder.prev_work_order_id.inprocess_move_trigger + 1
        if trigger_next and workorder.next_work_order_id:
            workorder.next_work_order_id.inprocess_move_trigger = workorder.next_work_order_id.inprocess_move_trigger + 1

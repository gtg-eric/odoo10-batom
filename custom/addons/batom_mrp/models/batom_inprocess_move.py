# -*- coding: utf-8 -*-
# Copyright <2017> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil import relativedelta
import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class BatomMrpInProcessMove(models.Model):
    _name = "batom.mrp.inprocess_move"
    _description = "Batom Custom Model MRP InProcess Move"
    _order = 'sequence, id'

    name = fields.Char('Description', index=True, required=True)
    sequence = fields.Integer('Sequence', default=10)
    create_date = fields.Datetime('Creation Date', index=True, readonly=True)
    date = fields.Datetime(
        'Date', default=fields.Datetime.now, index=True, required=True,
        states={'done': [('readonly', True)]},
        help="Move date: scheduled date until move is done, then date of actual move processing")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu'])], index=True, required=True,
        states={'done': [('readonly', True)]})
    product_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, required=True, states={'done': [('readonly', True)]},
        )
    production_id = fields.Many2one('mrp.production', 'Production Order',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    source_workorder_id = fields.Many2one(
        'mrp.workorder', 'Source Workorder',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    dest_workorder_id = fields.Many2one(
        'mrp.workorder', 'Destination Workorder',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    source_operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Source Operation',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    dest_operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Destination Operation',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    source_partner_id = fields.Many2one(
        'res.partner', 'Source Operation Partner',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    dest_partner_id = fields.Many2one(
        'res.partner', 'Destination Operation Partner',
        auto_join=True, index=True, required=False, states={'done': [('readonly', True)]},
        )
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('processed', 'Ready for QC'), ('qc', 'Under QC'), ('qcok', 'QC OK'),
        ('transport', 'In Transport'), ('done', 'Done')], string='Status',
        copy=False, default='draft', index=True, readonly=True,
        )

# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import math
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)
    
class BatomTeslaQrCode(models.Model):
    _name = "batom.tesla.qrcode"
    _description = 'Tesla QR Code Information'
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    pressfit_qr = fields.Char('Pressfit QR')
    gear_qr = fields.Char('Gear QR')
    pinion_qr = fields.Char('Pinion QR')
    press_info_ids = fields.One2many('batom.tesla.press_info', 'qr_id', 'Press Information', copy=True)

    @api.one
    @api.depends('pressfit_qr', 'gear_qr', 'pinion_qr')
    def _compute_name(self):
        self.name = (
            self.pressfit_qr if self.pressfit_qr else
            self.gear_qr if self.gear_qr else
            self.pinion_qr)
    
class BatomTeslaPressInfo(models.Model):
    _name = "batom.tesla.press_info"
    _description = 'Tesla Press Information'
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    gear_qr = fields.Char(string='Gear QR', compute='_compute_gear_qr', store=True)
    pinion_qr = fields.Char(string='Pinion QR', compute='_compute_pinion_qr', store=True)
    timestamp = fields.Char('Timestamp')
    qr_id = fields.Many2one('batom.tesla.qrcode', 'Qr Code', index=True)
    product_model = fields.Char('Product Model')
    press_distance = fields.Float('Press Distance')
    press_duration = fields.Float('Press Duration')
    compressor_pressure = fields.Float('Compressor Pressure')
    final_pressure = fields.Float('Final Pressure')
    pos1_pressure = fields.Float('Position 1 Pressure')
    pos2_pressure = fields.Float('Position 2 Pressure')
    pos3_pressure = fields.Float('Position 3 Pressure')
    pos4_pressure = fields.Float('Position 4 Pressure')
    pos5_pressure = fields.Float('Position 5 Pressure')
    result = fields.Char('Result')
    ng_reason = fields.Char('NG Reason')
    chart_file_name = fields.Char('Pressure Chart File Name')
    chart = fields.Binary('Pressure Chart')

    @api.one
    @api.depends('qr_id', 'qr_id.name')
    def _compute_name(self):
        self.name = self.qr_id.name if self.qr_id else self.timestamp

    @api.one
    @api.depends('qr_id', 'qr_id.gear_qr')
    def _compute_gear_qr(self):
        self.gear_qr = self.qr_id.gear_qr if self.qr_id else False

    @api.one
    @api.depends('qr_id', 'qr_id.pinion_qr')
    def _compute_pinion_qr(self):
        self.pinion_qr = self.qr_id.pinion_qr if self.qr_id else False
    
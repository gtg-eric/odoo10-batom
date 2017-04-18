# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import math
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class BatomCutterGroup(models.Model):
    _name = 'batom.cutter.group'
    _description = 'Cutter Group'
    
    name = fields.Char('Cutter Group Name')
    
class BatomCutter(models.Model):
    _name = "batom.cutter"
    _description = 'Cutter Information'
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    cutter_group_id = fields.Many2one('batom.cutter.group', string='Cutter Group')
    image_file = fields.Binary('Image File') # 圖面
    image_file_name = fields.Char('Image File Name')
    state = fields.Selection([ # 狀態
        ('material', u'物料'),
        ('bought', u'進貨'),
        ('consigned', u'進貨-客供'),
        ('sold', u'進貨-轉賣')],
        string='State',
        index=True,
        )
    batom_code = fields.Char('Batom Code') # 本土編號
    history_ids = fields.One2many('batom.cutter.history', 'cutter_id', 'History List') # 履歷表
    history_file = fields.Binary('History File') # 圖面
    history_file_name = fields.Char('History File Name')
    inquiry_number = fields.Char('Inquiry/Order Number') # 詢/訂價編號
    product_code = fields.Char('Product Code') # 工件編號
    product_ids = fields.Many2many(
        comodel_name='product.product', relation='batom_cutter_product_rel',
        column1='cutter_id', column2='product_id', string='Used by Products')
    supplier = fields.Char('Cutter Supplier') # 刀具製造商
    supplier_ids = fields.Many2many(
        comodel_name='res.partner', relation='batom_cutter_supplier_rel',
        column1='cutter_id', column2='partner_id', string='Supplied by')
    cutter_class = fields.Char('Cutter Class') # 刀具種類
    cutter_code = fields.Char('Cutter Code') # 刀具編號
    material = fields.Char('Material') # Material
    type = fields.Char('TYPE') # TYPE
    mod = fields.Float('MOD') # MOD
    dp = fields.Float('DP') # DP
    pa = fields.Float('PA') # PA
    teeth = fields.Char('Teeth (Workpiece)') # Teeth(工件)
    od = fields.Float('OD') # OD
    length = fields.Float('Length') # Length
    bore = fields.Float('Bore') # Bore
    df = fields.Float('D+F (Workpiece)') # D+F(工件)
    dtr_sn = fields.Float('DTR s/n') # DTR s/n
    price = fields.Float('Price') # 單價
    price_currency_id = fields.Many2one('res.currency', string='Price Currency')
    exchange_rate = fields.Float('Exchange Rate') # 匯率
    tax = fields.Float('Tax') # 稅
    tax_currency_id = fields.Many2one('res.currency', string='Tax Currency')
    shipping = fields.Float('Shipping Cost') # 運費
    shipping_currency_id = fields.Many2one('res.currency', string='Shipping Cost Currency')
    coating = fields.Char('Coating') # coating
    dressing_cost = fields.Float('Dressing Cost') # 修刀費用
    dressing_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    sharpening_cost = fields.Float('Dressing Cost') # 磨刀費
    sharpening_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    titanium_cost = fields.Float('Dressing Cost') # 鍍鈦費
    titanium_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    year = fields.Date('Year') # 年份
    total = fields.Float('Quantity') # Total
    consigned_to = fields.Char('Consigned To') # 保管廠商
    consigned_to_id = fields.Many2one('res.partner', string='Consigned To')
    consigned_date = fields.Char('Consigned Date') # 保管日期
    returned_date = fields.Char('Returned Date') # 歸還日期
    storage = fields.Char('Batom Storage') # 本土保管處
    remarks = fields.Text('Remarks') # 備註
    inquiry_form = fields.Binary('Inquiry Form') # 詢價單
    inquiry_form_name = fields.Char('Inquiry Form File Name')
    supplier_quotation = fields.Binary('Supplier Quotation') # 供應商報價單
    supplier_quotation_name = fields.Char('Supplier Quotation File Name')
    purchase_request = fields.Binary('Purchase Request') # 採購申請單
    purchase_request_name = fields.Char('Purchase Request File Name')
    purchase_order = fields.Binary('Purchase Order') # 訂購單
    purchase_order_name = fields.Char('Purchase Order File Name')
    order_confirmation = fields.Binary('Order Confirmation') # 訂單確認
    order_confirmation_name = fields.Char('Order Confirmation File Name')
    invoice = fields.Binary('Invoice') # Invoice
    invoice_name = fields.Char('Invoice File Name')
    order_date = fields.Date('Order Date') # 訂購日期
    expected_delivery_date = fields.Date('Expected Delivery Date') # 期望交期
    status = fields.Char('Status') # 現況
    allowed_sharpening = fields.Char('Allowed Sharpening') # 可磨刃長
    standard_sharpening = fields.Char('Standard Sharpening') # 標準研磨量
    allowed_sharpening_times = fields.Integer('Allowed Sharpening Times') # 可磨次數

    @api.one
    @api.depends('batom_code')
    def _compute_name(self):
        if self.batom_code:
            self.name = self.batom_code

class BatomCutterHistoryAction(models.Model):
    _name = 'batom.cutter.action'
    _description = 'Cutter History Action'
    
    name = fields.Char('Cutter History Action')
    is_out = fields.Boolean('Out Action', default=False)
    is_in = fields.Boolean('In Action', default=False)

class BatomCutterHisory(models.Model):
    _name = "batom.cutter.history"
    _description = 'Cutter History'
    
    cutter_id = fields.Many2one('batom.cutter', 'Cutter', index=True)
    date = fields.Date('Date', required=False, default=lambda self: fields.datetime.now())
    action_id = fields.Many2one('batom.cutter.action', string='Action')
    sharpening_mm = fields.Float('Sharpening Amount (mm)')
    processed_quantity = fields.Float('# Parts Processed')
    cost = fields.Float('Cost')
    cost_currency_id = fields.Many2one('res.currency', string='Cost Currency')
    remarks = fields.Text('Remarks') # 備註

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cutter_count = fields.Integer('# Cutters', compute='_compute_cutter_count')

    def _compute_cutter_count(self):
        self.cutter_count = sum(self.mapped('product_variant_ids').mapped('cutter_count'))
    
    @api.multi
    def action_template_view_cutter(self):
        action = self.env.ref('batom_tool.template_open_cutter').read()[0]
        action['domain'] = [('id', 'in', self.product_variant_ids.cutter_ids.ids)]
        return action
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    cutter_ids = fields.Many2many(
        comodel_name='batom.cutter', relation='batom_cutter_product_rel',
        column1='product_id', column2='cutter_id', string='Using Cutters')
    cutter_count = fields.Integer('# Cutters', compute='_compute_cutter_count')

    def _compute_cutter_count(self):
        if self.cutter_ids:
            self.cutter_count = len(self.cutter_ids)
        else:
            self.cutter_count = 0
    
    @api.multi
    def action_view_cutter(self):
        action = self.env.ref('batom_tool.product_open_cutter').read()[0]
        action['domain'] = [('id', 'in', self.cutter_ids.ids)]
        return action

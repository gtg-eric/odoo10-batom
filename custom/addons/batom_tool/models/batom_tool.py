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
    image_file = fields.Char('Image File') # 圖面
    state = fields.Selection([ # 狀態
        ('material', u'物料'),
        ('bought', u'進貨'),
        ('consigned', u'進貨-客供'),
        ('sold', u'進貨-轉賣')],
        string='State',
        index=True,
        )
    batom_code = fields.Char('Batom Code') # 本土編號
    history_list = fields.Char('History List') # 履歷表
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
    mod = fields.Char('MOD') # MOD
    dp = fields.Char('DP') # DP
    pa = fields.Char('PA') # PA
    teeth = fields.Char('Teeth (Workpiece)') # Teeth(工件)
    od = fields.Char('OD') # OD
    length = fields.Char('Length') # Length
    bore = fields.Char('Bore') # Bore
    df = fields.Char(' D+F (Workpiece)') # D+F(工件)
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
    year = fields.Char('Year') # 年份
    total = fields.Float('Quantity') # Total
    consigned_to = fields.Char('Consigned To') # 保管廠商
    consigned_to_id = fields.Many2one('res.partner', string='Consigned To')
    consigned_date = fields.Char('Consigned Date') # 保管日期
    returned_date = fields.Char('Returned Date') # 歸還日期
    storage = fields.Char('Batom Storage') # 本土保管處
    remarks = fields.Text('Remarks') # 備註
    inquiry_form = fields.Char('Inquiry Form') # 詢價單
    supplier_quotation = fields.Char('Supplier Quotation') # 供應商報價單
    purchase_request = fields.Char('Purchase Request') # 採購申請單
    purchase_order = fields.Char('Purchase Order') # 訂購單
    order_confirmation = fields.Char('Order Confirmation') # 訂單確認
    invoice = fields.Char('Invoice') # Invoice
    order_date = fields.Char('Order Date') # 訂購日期
    expected_delivery_date = fields.Char('Expected Delivery Date') # 期望交期
    status = fields.Char('Status') # 現況                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         

    @api.one
    @api.depends('batom_code')
    def _compute_name(self):
        if self.batom_code
            self.name = self.batom_code

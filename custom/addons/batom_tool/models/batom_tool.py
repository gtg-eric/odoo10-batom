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
    
class BatomCutterModel(models.Model):
    _name = "batom.cutter.model"
    _description = 'Cutter Model'
    _order = 'cutter_group_id, cutter_model_code'
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    cutter_model_code = fields.Char('Cutter Model Code', ) # 刀具型號
    cutter_group_id = fields.Many2one('batom.cutter.group', string='Cutter Group')
    image_file = fields.Binary('Image File', attachment=True) # 圖面
    image_file_name = fields.Char('Image File Name')
    model_history_ids = fields.One2many('batom.cutter.model.history', 'cutter_model_id', 'History List') # 履歷表
    product_ids = fields.Many2many(
        comodel_name='product.product', relation='batom_cutter_model_product_rel',
        column1='cutter_model_id', column2='product_id', string='Used by Products')
    product_code = fields.Char(string='Product code', compute='_compute_product_code', store=True)
    supplier = fields.Char('Cutter Supplier') # 刀具製造商
    supplier_ids = fields.Many2many(
        comodel_name='res.partner', relation='batom_cutter_model_supplier_rel',
        column1='cutter_model_id', column2='partner_id', string='Supplied by')
    cutter_class = fields.Char('Cutter Class') # 刀具種類
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
    coating = fields.Char('Coating') # coating
    dressing_cost = fields.Float('Dressing Cost') # 修刀費用
    dressing_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    sharpening_cost = fields.Float('Dressing Cost') # 磨刀費
    sharpening_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    titanium_cost = fields.Float('Dressing Cost') # 鍍鈦費
    titanium_cost_currency_id = fields.Many2one('res.currency', string='Dressing Cost Currency')
    allowed_sharpening = fields.Char('Allowed Sharpening') # 可磨刃長
    standard_sharpening = fields.Char('Standard Sharpening') # 標準研磨量
    allowed_sharpening_times = fields.Integer('Allowed Sharpening Times') # 可磨次數
    notes = fields.Text('Notes') # 注意事項

    _sql_constraints = [
        ('code_uniq', 'unique (cutter_model_code)', 'The modle code must be unique.')
    ]

    @api.one
    @api.depends('cutter_model_code')
    def _compute_name(self):
        if self.cutter_model_code:
            self.name = self.cutter_model_code

    @api.one
    @api.depends('product_ids')
    def _compute_product_code(self):
        product_code = None
        if self.product_ids:
            for product in self.product_ids:
                if product_code:
                    product_code += ", "
                else:
                    product_code = ""
                product_code += product.default_code
        self.product_code = product_code
    
class BatomCutter(models.Model):
    _name = "batom.cutter"
    _description = 'Cutter Information'
    _inherits = {'batom.cutter.model': 'cutter_model_id'}
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    state = fields.Selection([ # 狀態
        ('material', u'物料'),
        ('bought', u'進貨'),
        ('consigned', u'進貨-客供'),
        ('sold', u'進貨-轉賣'),
        ('scrapped', u'報廢'),
        ],
        string='State',
        index=True,
        )
    cutter_model_id = fields.Many2one('batom.cutter.model', string='Cutter Model')
    batom_code = fields.Char('Batom Code') # 本土編號
    history_ids = fields.One2many('batom.cutter.history', 'cutter_id', 'History List') # 履歷表
    history_file = fields.Binary('History File', attachment=True) # 圖面
    history_file_name = fields.Char('History File Name')
    inquiry_number = fields.Char('Inquiry/Order Number') # 詢/訂價編號
    product_code = fields.Char('Product Code') # 工件編號
    supplier = fields.Char('Cutter Supplier') # 刀具製造商
    price = fields.Float('Price') # 單價
    price_currency_id = fields.Many2one('res.currency', string='Price Currency')
    exchange_rate = fields.Float('Exchange Rate') # 匯率
    tax = fields.Float('Tax') # 稅
    tax_currency_id = fields.Many2one('res.currency', string='Tax Currency')
    shipping = fields.Float('Shipping Cost') # 運費
    shipping_currency_id = fields.Many2one('res.currency', string='Shipping Cost Currency')
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

    _sql_constraints = [
        ('code_uniq', 'unique (batom_code)', 'The Batom cutter code must be unique.')
    ]

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
    attached_file = fields.Binary('Attached File', attachment=True)
    attached_file_name = fields.Char('Attached File Name')

class BatomCutterModelHisory(models.Model):
    _name = "batom.cutter.model.history"
    _description = 'Cutter Model History'
    
    cutter_model_id = fields.Many2one('batom.cutter.model', 'Cutter Model', index=True)
    date = fields.Date('Date', required=False, default=lambda self: fields.datetime.now())
    remarks = fields.Text('Remarks') # 備註
    attached_file = fields.Binary('Attached File', attachment=True)
    attached_file_name = fields.Char('Attached File Name')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cutter_model_count = fields.Integer('# Cutters', compute='_compute_cutter_model_count')

    def _compute_cutter_model_count(self):
        self.cutter_model_count = sum(self.mapped('product_variant_ids').mapped('cutter_model_count'))
    
    @api.multi
    def action_template_view_cutter(self):
        action = self.env.ref('batom_tool.template_open_cutter_model').read()[0]
        action['domain'] = [('id', 'in', self.product_variant_ids.cutter_model_ids.ids)]
        return action
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    cutter_model_ids = fields.Many2many(
        comodel_name='batom.cutter.model', relation='batom_cutter_model_product_rel',
        column1='product_id', column2='cutter_model_id', string='Using Cutters')
    cutter_model_count = fields.Integer('# Cutters', compute='_compute_cutter_model_count')

    def _compute_cutter_model_count(self):
        if self.cutter_model_ids:
            self.cutter_model_count = len(self.cutter_model_ids)
        else:
            self.cutter_model_count = 0
    
    @api.multi
    def action_view_cutter_model(self):
        action = self.env.ref('batom_tool.product_open_cutter_model').read()[0]
        action['domain'] = [('id', 'in', self.cutter_model_ids.ids)]
        return action

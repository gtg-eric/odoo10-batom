# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
import math
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BatomPartsIn(models.Model):
    _name = 'batom.parts_in'
    _description = 'Parts In'
    _order = 'pdate desc'

    active = fields.Boolean(
        'Active', compute='_compute_active', store=True,
        help="If unchecked, it will allow you to hide the record without removing it.")
    origin_id = fields.Integer('Original Parts In ID') # ID
    pdate = fields.Datetime('Parts In Date') # PDate
    supplier = fields.Many2one('res.partner', string='Supplier') # Supplier
    prodid = fields.Many2one('product.product', string='Product') # ProdID
    processid = fields.Many2one('product.product', string='Process') # ProcessID
    wreport = fields.Boolean('') # wReport
    urgency = fields.Selection([
        ('10', u'一般件'),
        ('20', u'下班前'),
        ('30', u'急件'),
        ('40', u'特急件'),
        ], string='Urgency') # Urgency
    priority = fields.Integer('Priority') # Priority
    location = fields.Char('Location') # Location
    inqty = fields.Integer('In Quantity', compute='_compute_inqty', store=True) # InQty
    qdate = fields.Datetime('QC Date') # QDate
    qprogress = fields.Char('QC Progress') # QProgress
    iqcqty = fields.Integer('IQC Quantity') # IQCQty
    result = fields.Char('IQC Result') # Result
    finish = fields.Boolean('Finished') # Finish
    waitca = fields.Boolean('Waiting CA') # WaitCA
    waitgt = fields.Boolean('Waitint GT') # WaitGT
    transfer = fields.Boolean('Transferred') # Transfer
    transtime = fields.Datetime('Time Transferred') # TransTime
    report = fields.Char('Report Number') # Report
    rptpath = fields.Char('Report Path') # RptPath
    ngtype = fields.Selection([
        ('10', u'尺寸不良'),
        ('20', u'外觀不良'),
        ('30', u'幾何不良'),
        ('40', u'規格不符'),
        ('50', u'面粗不良'),
        ('60', u'重修回'),
        ], string='NG Type') # NGType
    ngroot = fields.Selection([
        ('10', u'人'),
        ('20', u'機'),
        ('30', u'料'),
        ('40', u'法'),
        ], string='NG Root Cause') # NGRoot
    ngaction = fields.Selection([
        ('10', u'退修'),
        ('20', u'代修'),
        ('30', u'報廢'),
        ], string='NG Action') # NGAction
    memo = fields.Text('Memo') # Memo
    nextprocessid = fields.Many2one('res.partner', string='Next Process') # NextProcessID
    ntags = fields.Integer('# Tags') # nTags
    remarks = fields.Text('Remarks') # Remarks
    forengdept = fields.Boolean('For Engineering Department') # ForEngDept
    toqcqty = fields.Integer('Quantity to QC', compute='_compute_toqcqty') # ToQCQty
    creator = fields.Many2one('res.users', string='Created By') # Creator
    lastdate = fields.Datetime('Updated At') # LastDate
    lastperson = fields.Many2one('res.users', string='Updated By') # LastPerson
    parts_in_qty_ids = fields.One2many('batom.parts_in.qty', 'parts_in_id', string='Parts In Quantities')
    parts_in_qc_ids = fields.One2many('batom.parts_in.qc', 'parts_in_id', string='Parts In QC')

    @api.one
    @api.depends('finish')
    def _compute_active(self):
        if self.finish:
            self.active = False
        else:
            self.active = True
    
    @api.one
    @api.depends('parts_in_qty_ids', 'parts_in_qty_ids.inqty')
    def _compute_inqty(self):
        self.inqty = sum(self.mapped('parts_in_qty_ids').mapped('inqty'))
    
    @api.one
    @api.depends('inqty')
    def _compute_toqcqty(self):       
        if self.inqty > 3200:
            self.toqcqty = 20
        elif self.inqty > 500:
            self.toqcqty = 13
        elif self.inqty > 150:
            self.toqcqty = 8
        elif self.inqty > 50:
            self.toqcqty = 5
        elif self.inqty > 15:
            self.toqcqty = 3
        elif self.inqty >= 2:
            self.toqcqty = 2
        else:
            self.toqcqty = self.inqty

class BatomPartsInQty(models.Model):
    _name = 'batom.parts_in.qty'
    _description = 'Parts In Quantity'
    _order = 'origin_id, mkordid, mkordser'
    
    origin_id = fields.Integer('Original Parts In Quantity ID') # PID
    parts_in_id = fields.Many2one('batom.parts_in', string='Parts In') # ID
    mvtype = fields.Selection([
        ('10', u'正常品'),
        ('20', u'HT試片'),
        ('30', u'待判品'),
        ('60', u'開發件'),
        ('70', u'量產首件'),
        ('80', u'開發首件'),
        ], string='In Type') # MvType
    mkordid = fields.Char('MO ID') # MkOrdID
    mkordser = fields.Char('MO Sequence') # MkOrdSer
    batch = fields.Char('Batch #') # Batch
    memo = fields.Text('Memo') # Memo
    inqty = fields.Integer('Quantity') # InQty

class BatomPartsInQc(models.Model):
    _name = 'batom.parts_in.qc'
    _description = 'Parts In QC'
    _order = 'stime'
    
    origin_id = fields.Integer('Original Parts In QC ID') # PID
    parts_in_id = fields.Many2one('batom.parts_in', string='Parts In') # ID
    inspector = fields.Many2one('res.users', string='Inspector') # Inspector
    stime = fields.Datetime('Start Time') # STime
    etime = fields.Datetime('End Time') # ETime
    
class BatomShopIn(models.Model):
    _name = "batom.shop_in"
    _description = 'Shop In'
    _order = 'pdate desc'
    
    active = fields.Boolean(
        'Active', compute='_compute_active', store=True,
        help="If unchecked, it will allow you to hide the record without removing it.")
    origin_id = fields.Char('Shop Work Order') # ID
    parts_in_id = fields.Many2one('batom.parts_in', string='Originated Parts In') # SID
    pdate = fields.Datetime('Creation Date') # PDate
    supplier = fields.Many2one('res.partner', string='Supplier') # Supplier
    customer = fields.Many2one('res.partner', string='Customer') # Customer
    prodid = fields.Many2one('product.product', string='Product') # ProdID
    processid = fields.Many2one('product.product', string='Process') # ProcessID
    process = fields.Char('Process Note') # Process
    inqty = fields.Integer('In Quantity') # InQty
    nextprcs = fields.Selection([
        ('310', u'入庫'),
        ('320', u'生管'),
        ('330', u'其他'),
        ('340', u'船務'),
        ], string='Next Process') # NextPrcs
    creator = fields.Many2one('res.users', string='Created By') # Creator
    urgency = fields.Selection([
        ('10', u'一般件'),
        ('20', u'下班前'),
        ('30', u'急件'),
        ('40', u'特急件'),
        ], string='Urgency') # Urgency
    location = fields.Char('Location') # Location
    mkordid = fields.Char('MO ID') # MkOrdID
    batch = fields.Char('Batch #') # Batch
    pnote = fields.Text('Production Note') # PNote
    sdate = fields.Datetime('Factory Completion Date') # SDate
    outqty = fields.Integer('Out Quantity') # OutQty
    ngqty = fields.Integer('NG Quantity') # NGQty
    sprogress = fields.Selection([
        ('0', u''),
        ('10', u'排定'),
        ('20', u'已開單'),
        ('30', u'作業中'),
        ('40', u'完工'),
        ('50', u'退回'),
        ]) # SProgress
    snote = fields.Char('Factory Note') # SNote
    receiver = fields.Char('Responsible') # Receiver
    finish = fields.Boolean('Finished') # Finish
    transfer = fields.Boolean('Transferred') # Transfer
    transtime = fields.Datetime('Time Transferred') # TransTime
    lastdate = fields.Datetime('Updated At') # LastDate
    lastperson = fields.Many2one('res.users', string='Updated By') # LastPerson
    printerdata = fields.Datetime('Printout Date') # PrinterData
    mfbatch = fields.Char('Manufacture Batch') # MfBatch
    indate = fields.Datetime('In Date') # InDate
    qrinfo = fields.Char('QR Info') # QrInfo

    @api.one
    @api.depends('finish')
    def _compute_active(self):
        if self.finish:
            self.active = False
        else:
            self.active = True
    
class BatomPartsOut(models.Model):
    _name = "batom.parts_out"
    _description = 'Parts Out'
    _order = 'pdate desc'

    active = fields.Boolean(
        'Active', compute='_compute_active', store=True,
        help="If unchecked, it will allow you to hide the record without removing it.")
    origin_id = fields.Char('Parts Out Work Order') # ID
    pdate = fields.Datetime('Creation Date') # PDate
    supplier = fields.Many2one('res.partner', string='Supplier') # Supplier
    company = fields.Char('Company') # Company
    mvtype = fields.Selection([
        ('110', u'委外加工單'),
        ('120', u'送貨單'),
        ('130', u'退貨單'),
        ], string='Type') # MvType
    creator = fields.Many2one('res.users', string='Created By') # Creator
    urgency = fields.Selection([
        ('10', u'一般件'),
        ('20', u'下班前'),
        ('30', u'急件'),
        ('40', u'特急件'),
        ], string='Urgency') # Urgency
    lastdate = fields.Datetime('Updated At') # LastDate
    lastperson = fields.Many2one('res.users', string='Updated By') # LastPerson
    memo = fields.Text('Memo') # Memo
    finish = fields.Boolean('Finished') # Finish
    parts_out_qty_ids = fields.One2many('batom.parts_out.qty', 'parts_out_id', string='Parts Out Quantities')

    @api.one
    @api.depends('finish')
    def _compute_active(self):
        if self.finish:
            self.active = False
        else:
            self.active = True
    
class BatomPartsOutQty(models.Model):
    _name = "batom.parts_out.qty"
    _description = 'Parts Out Quantity'
    _order = 'origin_id'

    parts_out_id = fields.Many2one('batom.parts_out', string='Parts Out') # ID
    origin_id = fields.Integer('Original Parts Out Quantity ID') # PID
    prodid = fields.Many2one('product.product', string='Product') # ProdID
    processid = fields.Many2one('product.product', string='Process') # ProcessID
    outqty = fields.Integer('Out Quantity') # OutQty
    mkordid = fields.Char('MO ID') # MkOrdID
    mkordser = fields.Char('MO Sequence') # MkOrdSer
    batch = fields.Char('Batch #') # Batch
    remark = fields.Char('Remark') # Remark
    location = fields.Char('Location') # Location

class BatomMigratePartsIn(models.TransientModel):
    _name = "batom.migrate_parts_in"
    _description = "Migrate PartsIn"
    
    @api.multi
    def migrate_parts_in_by_date(self, dateStart, dateEnd = '99991231'):
        self.ensure_one()
        if len(dateStart) != 8 or not dateStart.isdigit():
            print '"' + dateStart + '" is not a valid date'
            return
        if len(dateEnd) != 8 or not dateEnd.isdigit():
            print '"' + dateEnd + '" is not a valid date'
            return
            
        try:
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            connBatom = dbBatom.conn_open()
            cursorBatom = connBatom.cursor()
            
            sql = (
                "SELECT ID, PDate, Supplier, ProdID, ProcessID, wReport, Urgency, "
                "Priority, Location, QDate, QProgress, IQCQty, Result, "
                "Finish, WaitCA, WaitGT, Transfer, TransTime, Report, NGType, "
                "NGRoot, NGAction, Memo, NextProcessID, nTags, Remarks, ForEngDept, "
                "Creator, LastDate, LastPerson, RptPath "
                "FROM PartsIn "
                "WHERE PDate BETWEEN '" + dateStart + "' AND '" + dateEnd + "'")
            
            partsIns = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            nCount = len(partsIns)
            nDone = 0
            for partsIn in partsIns:
                odooPartsIn = self._create_parts_in(cursorBatom, dict(zip(columns, partsIn)))
                nDone += 1
                if nDone % 10 == 0:
                    print str(nDone) + '/' + str(nCount)
                    self.env.cr.commit()
            self.env.cr.commit()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_parts_in_by_date:', exc_info=True)
            import pdb; pdb.set_trace()
            if connBatom:
                connBatom.close()

    def _create_parts_in(self, cursorBatom, partsIn):
        odooPartsIn = False
        values = {}
        try:
            for key, value in partsIn.iteritems():
                key = key.lower()
                if value:
                    if key in ['supplier', 'nextprocessid']:
                        value = self._getSupplierIdByCode(value)
                    elif key in ['prodid', 'processid']:
                        value = self._getProductIdByCode(value)
                    elif key in ['creator', 'lastperson']:
                        value = self._getUserIdByLoginName(value)
                    elif key in ['urgency', 'ngtype', 'ngroot', 'ngaction']:
                        value = str(value)
                    elif key == 'id':
                        key = 'origin_id'
                    elif key == 'location':
                        value = value.strip()
                    elif isinstance(value, datetime):
                        value = value - timedelta(hours=8) # from UTC+8 to UTC
                    if value:
                        values[key] = value
            odooPartsIns = False if 'origin_id' not in values else self.env['batom.parts_in'].search([
                '|', ('active', '=', True), ('active', '=', False),
                ('origin_id', '=', values['origin_id']),
                ])
            if odooPartsIns:
                odooPartsIn = odooPartsIns[0]
                odooPartsIn.write(values)
            else:
                odooPartsIn = self.env['batom.parts_in'].create(values)
                
            if odooPartsIn:
                self._create_parts_in_qty(cursorBatom, odooPartsIn.id, values['origin_id'])
                self._create_parts_in_qc(cursorBatom, odooPartsIn.id, values['origin_id'])
        except Exception:
            _logger.warning('Exception in _create_parts_in:', exc_info=True)
            import pdb; pdb.set_trace()
            
        return odooPartsIn

    def _create_parts_in_qty(self, cursorBatom, partsInId, originId):
        try:
            sql = (
                "SELECT PID, MvType, MkOrdID, MkOrdSer, Batch, Memo, InQty "
                "FROM PartsInQty "
                "WHERE ID = " + str(originId))
            partsInQtys = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            for partsInQty in partsInQtys:
                values = {}
                values['parts_in_id'] = partsInId
                partsInQtyDict = dict(zip(columns, partsInQty))
                for key, value in partsInQtyDict.iteritems():
                    key = key.lower()
                    if value:
                        if key == 'mvtype':
                            value = str(value)
                        elif key == 'pid':
                            key = 'origin_id'
                        if value:
                            values[key] = value
                odooPartsInQtys = False if 'origin_id' not in values else self.env['batom.parts_in.qty'].search([
                    ('origin_id', '=', values['origin_id']),
                    ])
                if odooPartsInQtys:
                    odooPartsInQty = odooPartsInQtys[0]
                    odooPartsInQty.write(values)
                else:
                    odooPartsInQty = self.env['batom.parts_in.qty'].create(values)
        except Exception:
            _logger.warning('Exception in _create_parts_in_qty:', exc_info=True)
            import pdb; pdb.set_trace()

    def _create_parts_in_qc(self, cursorBatom, partsInId, originId):
        try:
            sql = (
                "SELECT PID, Inspector, STime, ETime "
                "FROM PartsInQc "
                "WHERE ID = " + str(originId))
            partsInQcs = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            for partsInQc in partsInQcs:
                values = {}
                values['parts_in_id'] = partsInId
                partsInQcDict = dict(zip(columns, partsInQc))
                for key, value in partsInQcDict.iteritems():
                    key = key.lower()
                    if value:
                        if key == 'inspector':
                            value = self._getUserIdByLoginName(value)
                        elif key == 'pid':
                            key = 'origin_id'
                        elif isinstance(value, datetime):
                            value = value - timedelta(hours=8) # from UTC+8 to UTC
                        if value:
                            values[key] = value
                odooPartsInQcs = False if 'origin_id' not in values else self.env['batom.parts_in.qc'].search([
                    ('origin_id', '=', values['origin_id']),
                    ])
                if odooPartsInQcs:
                    odooPartsInQc = odooPartsInQcs[0]
                    odooPartsInQc.write(values)
                else:
                    odooPartsInQc = self.env['batom.parts_in.qc'].create(values)
        except Exception:
            _logger.warning('Exception in _create_parts_in_qty:', exc_info=True)
            import pdb; pdb.set_trace()
    
    @api.multi
    def migrate_shop_in_by_date(self, dateStart, dateEnd = '99991231'):
        self.ensure_one()
        if len(dateStart) != 8 or not dateStart.isdigit():
            print '"' + dateStart + '" is not a valid date'
            return
        if len(dateEnd) != 8 or not dateEnd.isdigit():
            print '"' + dateEnd + '" is not a valid date'
            return
            
        try:
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            connBatom = dbBatom.conn_open()
            cursorBatom = connBatom.cursor()
            
            sql = (
                "SELECT ID, SID, PDate, Supplier, Customer, ProdID, ProcessID, "
                "Process, InQty, NextPrcs, Creator, Urgency, Location, MkOrdID, "
                "Batch, PNote, SDate, OutQty, NGQty, SProgress, SNote, Receiver, "
                "Finish, Transfer, TransTime, LastDate, LastPerson, PrinterData, "
                "MfBatch, InDate, QrInfo "
                "FROM ShopIn "
                "WHERE PDate BETWEEN '" + dateStart + "' AND '" + dateEnd + "'")
            
            shopIns = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            nCount = len(shopIns)
            nDone = 0
            for shopIn in shopIns:
                odooShopIn = self._create_shop_in(cursorBatom, dict(zip(columns, shopIn)))
                nDone += 1
                if nDone % 10 == 0:
                    print str(nDone) + '/' + str(nCount)
                    self.env.cr.commit()
            self.env.cr.commit()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_parts_in_by_date:', exc_info=True)
            import pdb; pdb.set_trace()
            if connBatom:
                connBatom.close()

    def _create_shop_in(self, cursorBatom, shopIn):
        odooShopIn = False
        values = {}
        try:
            for key, value in shopIn.iteritems():
                key = key.lower()
                if value:
                    if key == 'supplier':
                        value = self._getSupplierIdByCode(value)
                    elif key == 'customer':
                        value = self._getCustomerIdByCode(value)
                    elif key in ['prodid', 'processid']:
                        value = self._getProductIdByCode(value)
                    elif key in ['creator', 'lastperson']:
                        value = self._getUserIdByLoginName(value)
                    elif key in ['nextprcs', 'urgency', 'sprogress']:
                        value = str(value)
                    elif key == 'id':
                        key = 'origin_id'
                    elif key == 'sid':
                        key = 'parts_in_id'
                        value = self._getPartsInIdByOriginId(value)
                    elif key == 'location':
                        value = value.strip()
                    elif isinstance(value, datetime):
                        value = value - timedelta(hours=8) # from UTC+8 to UTC
                    if value:
                        values[key] = value
            odooShopIns = False if 'origin_id' not in values else self.env['batom.shop_in'].search([
                '|', ('active', '=', True), ('active', '=', False),
                ('origin_id', '=', values['origin_id']),
                ])
            if odooShopIns:
                odooShopIn = odooShopIns[0]
                odooShopIn.write(values)
            else:
                odooShopIn = self.env['batom.shop_in'].create(values)
        except Exception:
            _logger.warning('Exception in _create_shop_in:', exc_info=True)
            import pdb; pdb.set_trace()
            
        return odooShopIn
    
    @api.multi
    def migrate_parts_out_by_date(self, dateStart, dateEnd = '99991231'):
        self.ensure_one()
        if len(dateStart) != 8 or not dateStart.isdigit():
            print '"' + dateStart + '" is not a valid date'
            return
        if len(dateEnd) != 8 or not dateEnd.isdigit():
            print '"' + dateEnd + '" is not a valid date'
            return
            
        try:
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            connBatom = dbBatom.conn_open()
            cursorBatom = connBatom.cursor()
            
            sql = (
                "SELECT ID, PDate, Supplier, Company, MvType, Urgency, "
                "Memo, Finish, Creator, LastDate, LastPerson "
                "FROM PartsOut "
                "WHERE PDate BETWEEN '" + dateStart + "' AND '" + dateEnd + "'")
            
            partsOuts = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            nCount = len(partsOuts)
            nDone = 0
            for partsOut in partsOuts:
                odooPartsOut = self._create_parts_out(cursorBatom, dict(zip(columns, partsOut)))
                nDone += 1
                if nDone % 10 == 0:
                    print str(nDone) + '/' + str(nCount)
                    self.env.cr.commit()
            self.env.cr.commit()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_parts_in_by_date:', exc_info=True)
            import pdb; pdb.set_trace()
            if connBatom:
                connBatom.close()

    def _create_parts_out(self, cursorBatom, partsOut):
        odooPartsOut = False
        values = {}
        try:
            for key, value in partsOut.iteritems():
                key = key.lower()
                if value:
                    if key == 'supplier':
                        value = self._getSupplierIdByCode(value)
                    elif key in ['creator', 'lastperson']:
                        value = self._getUserIdByLoginName(value)
                    elif key in ['mvtype', 'urgency']:
                        value = str(value)
                    elif key == 'id':
                        key = 'origin_id'
                    elif isinstance(value, datetime):
                        value = value - timedelta(hours=8) # from UTC+8 to UTC
                    if value:
                        values[key] = value
            odooPartsOuts = False if 'origin_id' not in values else self.env['batom.parts_out'].search([
                '|', ('active', '=', True), ('active', '=', False),
                ('origin_id', '=', values['origin_id']),
                ])
            if odooPartsOuts:
                odooPartsOut = odooPartsOuts[0]
                odooPartsOut.write(values)
            else:
                odooPartsOut = self.env['batom.parts_out'].create(values)
                
            if odooPartsOut and 'origin_id' in values:
                self._create_parts_out_qty(cursorBatom, odooPartsOut.id, values['origin_id'])
        except Exception:
            _logger.warning('Exception in _create_parts_out:', exc_info=True)
            import pdb; pdb.set_trace()
            
        return odooPartsOut

    def _create_parts_out_qty(self, cursorBatom, partsOutId, originId):
        try:
            sql = (
                "SELECT PID, ProdID, ProcessID, OutQty, MkOrdID, MkOrdSer, Batch, Remark, Location "
                "FROM PartsOutQty "
                "WHERE ID = " + str(originId))
            partsOutQtys = cursorBatom.execute(sql).fetchall()
            columns = [column[0] for column in cursorBatom.description]
            for partsOutQty in partsOutQtys:
                values = {}
                values['parts_out_id'] = partsOutId
                partsOutQtyDict = dict(zip(columns, partsOutQty))
                for key, value in partsOutQtyDict.iteritems():
                    key = key.lower()
                    if value:
                        if key in ['prodid', 'processid']:
                            value = self._getProductIdByCode(value)
                        elif key == 'pid':
                            key = 'origin_id'
                        elif key == 'location':
                            value = value.strip()
                        if value:
                            values[key] = value
                odooPartsOutQtys = False if 'origin_id' not in values else self.env['batom.parts_out.qty'].search([
                    ('origin_id', '=', values['origin_id']),
                    ])
                if odooPartsOutQtys:
                    odooPartsOutQty = odooPartsOutQtys[0]
                    odooPartsOutQty.write(values)
                else:
                    odooPartsOutQty = self.env['batom.parts_out.qty'].create(values)
        except Exception:
            _logger.warning('Exception in _create_parts_out_qty:', exc_info=True)
            import pdb; pdb.set_trace()
            
    def _getSupplierIdByCode(self, supplier_code):
        suppliers = self.env['res.partner'].search([
            ('x_supplier_code', '=', supplier_code),
            ])
        if len(suppliers) > 0:
            return suppliers[0].id
        else:
            return None
            
    def _getCustomerIdByCode(self, customer_code):
        customers = self.env['res.partner'].search([
            ('x_customer_code', '=', customer_code),
            ])
        if len(customers) > 0:
            return customers[0].id
        else:
            return None

    def _getProductIdByCode(self, product_code):
        products = self.env['product.product'].search([
            ('default_code', '=', product_code),
            ])
        if len(products) > 0:
            return products[0].id
        else:
            return None
    
    def _getUserIdByLoginName(self, login_name):
        users = self.env['res.users'].search([
            ('login', '=', login_name),
            ])
        if len(users) > 0:
            return users[0].id
        else:
            return None
    
    def _getPartsInIdByOriginId(self, origin_id):
        partsIns = self.env['batom.parts_in'].search([
            ('origin_id', '=', origin_id),
            ])
        if len(partsIns) > 0:
            return partsIns[0].id
        else:
            return None
    
# -*- coding: utf-8 -*-
# Copyright <2016> <Batom Co., Ltd.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import logging
from odoo import models, fields, api,  _
import odoo
import odoo.addons.base_external_dbsource

_logger = logging.getLogger(__name__)
    
_currencyMapping = ({
    'NTD': 'TWD',
    'GRP': 'GBP',
    })
def _currencyIdConversion(self, currencyId):
    returnedCurrencyId = None
    if currencyId and currencyId.strip():
        if currencyId in _currencyMapping:
            currencyId = _currencyMapping[currencyId]
        currencyIds = self.env['res.currency'].search([('name', '=', currencyId)]).ids
        if len(currencyIds) > 0:
            returnedCurrencyId = currencyIds.pop(0)
    return returnedCurrencyId

_uomMapping = ({
    'Kg': 'kg',
    'M': 'm',
    u'ＰＣ': 'PC',
    u'英呎': 'foot(ft)',
    u'桶': 'barrel',
    })
def _uomIdConversion(self, uom):
    uomId = 1 # uom cannot be null
    if uom and uom.strip():
        if uom in _uomMapping:
            uom = _uomMapping[uom]
        uomIds = self.env['product.uom'].search([('name', '=', uom)]).ids
        if len(uomIds) > 0:
            uomId = uomIds.pop(0)
    return uomId
    
def _updateTranslation(self, name, res_id, src, value):
    lang = 'zh_TW'
    type = 'model'
    state = 'translated'
    translationModel = self.env['ir.translation']
    if not value or not value.strip():
        value = src
    values = ({
        'lang': lang,
        'type': type,
        'name': name,
        'res_id': res_id,
        'src': src,
        'value': value,
        'state': state,
        })
    translations = translationModel.search([
        ('lang', '=', lang),
        ('type', '=', type),
        ('name', '=', name),
        ('res_id', '=', res_id),
        ('src', '=', src),
        ])
    if len(translations) == 0:
        translationModel.create(values)
    else:
        translations[0].write(values)
    
class batom_partner_code(models.Model):
    #_name = 'batom.partner_code'
    _inherit = 'res.partner'
    
    x_customer_code = fields.Char('Customer Code')
    x_supplier_code = fields.Char('Supplier Code')
    x_phone2 = fields.Char('Phone 2')
    x_phone3 = fields.Char('Phone 3')

class batom_partner_category(models.Model):
    #_name = 'batom.partner.category'
    _inherit = 'res.partner.category'
    
    x_flag = fields.Integer('Category Flag')
    x_category_code = fields.Char('Category Code', required=False, size=6)
    x_memo = fields.Char('Memo', required=False)

class BatomAccountType(models.Model):
    _name = "batom.account.type"
    _description = "Batom Account Type"

    code = fields.Char(string='Account Type Code', required=True)
    name = fields.Char(string='Account Type', required=True)

class BatomAccountAccount(models.Model):
    #_name = 'batom.account.account'
    _inherit = 'account.account'

    x_batom_type_id = fields.Many2one('batom.account.type', string='Batom Account Type')
    x_batom_parent_id = fields.Many2one('account.account', string='Batom Parent Account')

class BatomProductTemplate(models.Model):
    #_name = 'batom.product.template'
    _inherit = 'product.template'

    x_is_process = fields.Boolean('Manufacturing Process', default=False)

class _partner_migration:
    def __init__(self, id, shortName, fullName):
        self.id = id
        self.shortName = shortName
        self.fullName = fullName

class _partner_address:
    def __init__(self, zip, address, contactName, title, phone, mobile, fax, email, memo):
        self.zip = zip
        self.city = None
        self.state_id = None
        self.street = address
        self.street2 = None
        self.contactName = contactName
        self.title = title
        self.phone = phone
        self.mobile = mobile
        self.fax = fax
        self.email = email
        self.memo = memo

class BatomPartnerMigrationRefresh(models.TransientModel):
    _name = "batom.partner_migration_refresh"
    _description = "Refresh Partner Data Migration Table"

    def _countryIdConversion(self, areaId):
        areaIds = ["01", "02", "03", "04", "05", "06"]
        countryIds = [229, 235, 233, 49, 105, 199]
        countryId = None
        try:
            idx = areaIds.index(areaId)
            countryId = countryIds[idx]
        except ValueError:
            countryId = None
            
        return countryId
    
    def _partnerCategoryConversion(self, type, classId):
        categoryIds = self.env['res.partner.category'].search([('x_flag', '=', type), ('x_category_code', '=', classId)]).ids
        categoryId = None
        if len(categoryIds) > 0:
            categoryId = categoryIds.pop(0)
        return categoryId
        
    def _contactDisplayName(self, type, companyName, contactName):
        try:
            if contactName != None and contactName and contactName.strip():
                name = companyName + u', ' + contactName.decode('utf8')
            else:
                types = ['contact', 'invoice', 'delivery', 'other']
                names = [u'聯絡人', u'發票地址', u'送貨地址', u'其他地址']
                idx = types.index(type)
                name = companyName + u', ' + names[idx]
        except Exception:
            _logger.warning('Exception in refresh_partner_data:', exc_info=True)
            name = companyName
        return name
    
    def _createPartnerContact(self, type, parentPartner, address):
        partnerModel = self.env['res.partner']
        if address.mobile and address.mobile.strip():
            mobile = address.mobile
        else:
            mobile = parentPartner.mobile if (type == 'contact') else None
        if address.email and address.email.strip():
            email = address.email
        else:
            email = parentPartner.email
        newPartner = partnerModel.create({
            'parent_id': parentPartner.id,
            'type': type,
            'email': email,
            'fax': address.fax,
            'name': address.contactName,
            'commercial_company_name': parentPartner.commercial_company_name,
            'mobile': mobile,
            'phone': address.phone,
            'is_company': 0, # 1 if (type != 'contact') else 0,
            'customer': parentPartner.customer,
            'supplier': parentPartner.supplier,
            'zip': address.zip,
            'city': address.city,
            'state_id': address.state_id,
            'street': address.street,
            'street2': address.street2,
            'comment': address.memo,
            })
        newPartner.write({'display_name': self._contactDisplayName(type, parentPartner.display_name, address.contactName)})
     
    @api.multi
    def refresh_partner_data(self):
        try:
            self.ensure_one()
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            batomCustomers = dbBatom.execute('SELECT ID, ShortName, FullName FROM Customer ORDER BY ID')
            chiCustomers = dbChi.execute('SELECT ID, ShortName, FullName FROM comCustomer WHERE Flag=1 ORDER BY ID')
            odooCustomerIds = self.env['res.partner'].search([('is_company', '=', True), ('customer', '=', True)], order='x_customer_code').ids
            odooPartnerMigration = self.env['batom.partner_migration']
            odooPartnerMigration.search([]).unlink() # delete all migration records
            batomCustomer = None
            chiCustomer = None
            odooCustomer = None
            while (
                    batomCustomer != None or chiCustomer != None or odooCustomer != None or
                    len(batomCustomers) > 0 or len(chiCustomers) > 0 or len(odooCustomerIds) > 0
                    ):
                if batomCustomer == None and len(batomCustomers) > 0:
                    customer = batomCustomers.pop(0)
                    batomCustomer = _partner_migration(customer.ID, customer.ShortName, customer.FullName)
                if chiCustomer == None and len(chiCustomers) > 0:
                    customer = chiCustomers.pop(0)
                    chiCustomer = _partner_migration(customer.ID, customer.ShortName, customer.FullName)
                if odooCustomer == None and len(odooCustomerIds) > 0:
                    customer = self.env['res.partner'].browse(odooCustomerIds.pop(0))
                    odooCustomer = _partner_migration(customer.x_customer_code, customer.display_name, customer.name)
                    
                minId = None
                if batomCustomer != None:
                    minId = batomCustomer.id
                if chiCustomer != None and (minId == None or chiCustomer.id < minId):
                    minId = chiCustomer.id
                if odooCustomer != None and (minId == None or odooCustomer.id < minId):
                    minId = odooCustomer.id

                if batomCustomer != None and batomCustomer.id == minId:
                    in_id = batomCustomer.id
                    in_short_name = batomCustomer.shortName
                    in_full_name = batomCustomer.fullName
                    batomCustomer = None
                else:
                    in_id = None
                    in_short_name = None
                    in_full_name = None
                if chiCustomer != None and chiCustomer.id == minId:
                    chi_id = chiCustomer.id
                    chi_short_name = chiCustomer.shortName
                    chi_full_name = chiCustomer.fullName
                    chiCustomer = None
                else:
                    chi_id = None
                    chi_short_name = None
                    chi_full_name = None
                if odooCustomer != None and odooCustomer.id == minId:
                    odoo_id = odooCustomer.id
                    odoo_short_name = odooCustomer.shortName
                    odoo_full_name = odooCustomer.fullName
                    odooCustomer = None
                else:
                    odoo_id = None
                    odoo_short_name = None
                    odoo_full_name = None

                odooPartnerMigration.create({
                    'type': 1,
                    'in_id': in_id,
                    'in_short_name': in_short_name,
                    'in_full_name': in_full_name,
                    'chi_id': chi_id, 
                    'chi_short_name': chi_short_name,
                    'chi_full_name': chi_full_name,
                    'odoo_id': odoo_id,
                    'odoo_short_name': odoo_short_name,    
                    'odoo_full_name': odoo_full_name,
                    })

            batomSuppliers = dbBatom.execute('SELECT ID, ShortName, FullName FROM Supplier ORDER BY ID')
            chiSuppliers = dbChi.execute('SELECT ID, ShortName, FullName FROM comCustomer where Flag=2 ORDER BY ID')
            odooSupplierIds = self.env['res.partner'].search([('is_company', '=', True), ('supplier', '=', True)], order='x_supplier_code').ids
            batomSupplier = None
            chiSupplier = None
            odooSupplier = None
            while (
                    batomSupplier != None or chiSupplier != None or odooSupplier != None or
                    len(batomSuppliers) > 0 or len(chiSuppliers) > 0 or len(odooSupplierIds) > 0
                    ):
                if batomSupplier == None and len(batomSuppliers) > 0:
                    supplier = batomSuppliers.pop(0)
                    batomSupplier = _partner_migration(supplier.ID, supplier.ShortName, supplier.FullName)
                if chiSupplier == None and len(chiSuppliers) > 0:
                    supplier = chiSuppliers.pop(0)
                    chiSupplier = _partner_migration(supplier.ID, supplier.ShortName, supplier.FullName)
                if odooSupplier == None and len(odooSupplierIds) > 0:
                    supplier = self.env['res.partner'].browse(odooSupplierIds.pop(0))
                    odooSupplier = _partner_migration(supplier.x_supplier_code, supplier.display_name, supplier.name)
                    
                minId = None
                if batomSupplier != None:
                    minId = batomSupplier.id
                if chiSupplier != None and (minId == None or chiSupplier.id < minId):
                    minId = chiSupplier.id
                if odooSupplier != None and (minId == None or odooSupplier.id < minId):
                    minId = odooSupplier.id
            
                if batomSupplier != None and batomSupplier.id == minId:
                    in_id = batomSupplier.id
                    in_short_name = batomSupplier.shortName
                    in_full_name = batomSupplier.fullName
                    batomSupplier = None
                else:
                    in_id = None
                    in_short_name = None
                    in_full_name = None
                if chiSupplier != None and chiSupplier.id == minId:
                    chi_id = chiSupplier.id
                    chi_short_name = chiSupplier.shortName
                    chi_full_name = chiSupplier.fullName
                    chiSupplier = None
                else:
                    chi_id = None
                    chi_short_name = None
                    chi_full_name = None
                if odooSupplier != None and odooSupplier.id == minId:
                    odoo_id = odooSupplier.id
                    odoo_short_name = odooSupplier.shortName
                    odoo_full_name = odooSupplier.fullName
                    odooSupplier = None
                else:
                    odoo_id = None
                    odoo_short_name = None
                    odoo_full_name = None
            
                odooPartnerMigration.create({
                    'type': 2,
                    'in_id': in_id,
                    'in_short_name': in_short_name,
                    'in_full_name': in_full_name,
                    'chi_id': chi_id, 
                    'chi_short_name': chi_short_name,
                    'chi_full_name': chi_full_name,
                    'odoo_id': odoo_id,
                    'odoo_short_name': odoo_short_name,    
                    'odoo_full_name': odoo_full_name,
                    })
            self.env.cr.commit()            
        except Exception:
            _logger.warning('Exception in refresh_partner_data:', exc_info=True)
            
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'batom.partner_migration',
            'target': 'current',
            'res_id': 'view_partner_migration_tree',
            'type': 'ir.actions.act_window'
        }
    
    @api.multi
    def apply_partner_data(self):
        try:
            self.ensure_one()
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            odooPartnerMigration = self.env['batom.partner_migration'].search([('odoo_id', '=', None)])
            partnerModel = self.env['res.partner']
            
            for migration in odooPartnerMigration:
                try:
                    if migration.type == 1:
                        codeColumnName = 'x_customer_code'
                        customerValue = 1
                        supplierValue = 0
                    else:
                        codeColumnName = 'x_supplier_code'
                        customerValue = 0
                        supplierValue = 1
                    if migration.chi_id != None and migration.chi_id and migration.chi_id.strip():
                        sql = (
                            "SELECT ID, ShortName, FullName, LinkMan, LinkManProf, "
                            "AreaID, ClassID, CurrencyID, Email, FaxNo, InvoiceHead, TaxNo, "
                            "MobileTel, Telephone1, Telephone2, Telephone3, WebAddress "
                            "FROM comCustomer "
                            "WHERE Flag=" + str(migration.type) + " AND ID='" + migration.chi_id + "'"
                            )
                        chiPartner = dbChi.execute(sql).pop(0)
                        
                        if chiPartner != None:
                            sql = ("SELECT AddrOfInvo, "
                                "A1.ZipCode AS ZipCode1, A1.Address AS Address1, A1.LinkMan AS LinkMan1, A1.LinkManProf AS LinkManProf1, A1.Telephone AS Telephone1, A1.FaxNo AS FaxNo1, A1.Memo AS Memo1, "
                                "A2.ZipCode AS ZipCode2, A2.Address AS Address2, A2.LinkMan AS LinkMan2, A2.LinkManProf AS LinkManProf2, A2.Telephone AS Telephone2, A2.FaxNo AS FaxNo2, A2.Memo AS Memo2, "
                                "A3.ZipCode AS ZipCode3, A3.Address AS Address3, A3.LinkMan AS LinkMan3, A3.LinkManProf AS LinkManProf3, A3.Telephone AS Telephone3, A3.FaxNo AS FaxNo3, A3.Memo AS Memo3 "
                                "FROM comCustDesc AS C "
                                "LEFT JOIN comCustAddress A1 ON (A1.Flag = C.Flag AND A1.ID = C.ID AND A1.AddrID = C.DeliverAddrID) "
                                "LEFT JOIN comCustAddress A2 ON (A2.Flag = C.Flag AND A2.ID = C.ID AND A2.AddrID = C.AddrID) "
                                "LEFT JOIN comCustAddress A3 ON (A3.Flag = C.Flag AND A3.ID = C.ID AND A3.AddrID = C.EngAddrID) "
                                "WHERE C.Flag=" + str(migration.type) + " AND C.ID='" + migration.chi_id + "'"
                                )
                            addresses = dbChi.execute(sql).pop(0)
                            address = None
                            addressShipping = None
                            addressInvoice = None
                            addressOther = None
                            if addresses != None:
                                if addresses.Address1 != None:
                                    addressShipping = _partner_address(addresses.ZipCode1, addresses.Address1, addresses.LinkMan1, addresses.LinkManProf1, addresses.Telephone1, None, addresses.FaxNo1, None, addresses.Memo1)
                                    address = addressShipping
                                if addresses.Address2 != None:
                                    addressInvoice = _partner_address(addresses.ZipCode2, addresses.Address2, addresses.LinkMan2, addresses.LinkManProf2, addresses.Telephone2, None, addresses.FaxNo2, None, addresses.Memo2)
                                    if address == None:
                                        address = addressInvoice
                                if addresses.Address3 != None:
                                    addressOther = _partner_address(addresses.ZipCode3, addresses.Address3, addresses.LinkMan3, addresses.LinkManProf3, addresses.Telephone3, None, addresses.FaxNo3, None, addresses.Memo3)
                                    if address == None:
                                        address = addressOther
                            
                            categoryId = self._partnerCategoryConversion(migration.type, chiPartner.ClassID)
                            newPartner = partnerModel.create({
                                codeColumnName: chiPartner.ID,
                                'country_id': self._countryIdConversion(chiPartner.AreaID),
                                'category_id': [(4, categoryId, 0)] if (categoryId != None) else None,
                                'property_purchase_currency_id': _currencyIdConversion(self, chiPartner.CurrencyID),
                                'email': chiPartner.Email,
                                'fax': chiPartner.FaxNo if (chiPartner.FaxNo != None and chiPartner.FaxNo and chiPartner.FaxNo.strip()) else (
                                    address.fax if (address != None) else None),
                                'name': chiPartner.FullName,
                                'commercial_company_name': chiPartner.InvoiceHead,
                                'mobile': chiPartner.MobileTel,
                                'vat': chiPartner.TaxNo,
                                'phone': chiPartner.Telephone1 if (chiPartner.Telephone1 != None and chiPartner.Telephone1 and chiPartner.Telephone1.strip()) else (
                                    address.phone if address != None else None),
                                'x_phone2': chiPartner.Telephone2,
                                'x_phone3': chiPartner.Telephone3,
                                'website': None if not chiPartner.WebAddress else chiPartner.WebAddress,
                                'is_company': 1,
                                'customer': customerValue,
                                'supplier': supplierValue,
                                'zip': address.zip if address != None else None,
                                'city': address.city if address != None else None,
                                'state_id': address.state_id if address != None else None,
                                'street': address.street if address != None else None,
                                'street2': address.street2 if address != None else None,
                                })
                            newPartner.write({'display_name': chiPartner.ShortName})
                            
                            if chiPartner.LinkMan != None and chiPartner.LinkMan and chiPartner.LinkMan.strip():
                                contact = _partner_address(None, None, chiPartner.LinkMan, chiPartner.LinkManProf, newPartner.phone, None, newPartner.fax, None, None)
                                self._createPartnerContact('contact', newPartner, contact)
                            if addressShipping != None:
                                self._createPartnerContact('delivery', newPartner, addressShipping)
                            if addressInvoice != None:
                                self._createPartnerContact('invoice', newPartner, addressInvoice)
                            if addressOther != None:
                               self._createPartnerContact('other', newPartner, addressOther)
                            linkMans = dbChi.execute(
                                "SELECT PersonName, ProfTitle, Telephone, Mobile, Email, FaxNo, Memo "
                                "FROM comLinkMan "
                                "WHERE Flag=" + str(migration.type) + " AND CustomID='" + chiPartner.ID + "'"
                                )
                            if len(linkMans) > 0:
                                for linkMan in linkMans:
                                    contact = _partner_address(None, None, linkMan.PersonName, linkMan.ProfTitle, linkMan.Telephone, linkMan.Mobile, linkMan.FaxNo, linkMan.Email, linkMan.Memo)
                                    self._createPartnerContact('contact', newPartner, contact)
                    elif migration.in_id != None and migration.in_id and migration.in_id.strip():
                        if migration.type == 1:
                            inPartner = dbBatom.execute(
                                "select ID, ShortName, FullName "
                                "from Customer where ID='" + migration.in_id + "'"
                                ).pop(0)
                        else:
                            inPartner = dbBatom.execute(
                                "select ID, ShortName, FullName "
                                "from Supplier where ID='" + migration.in_id + "'"
                                ).pop(0)
                        if inPartner != None:
                            newPartner = partnerModel.create({
                                codeColumnName: inPartner.ID,
                                'name': inPartner.FullName,
                                'is_company': 1,
                                'customer': customerValue,
                                'supplier': supplierValue,
                                })
                            newPartner.write({'display_name': inPartner.ShortName})
                except Exception:
                    _logger.warning('Exception in apply_partner_data:', exc_info=True)
                    continue
            self.env.cr.commit()            
        except Exception:
            _logger.warning('Exception in apply_partner_data:', exc_info=True)
            
        self.refresh_partner_data()
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'batom.partner_migration',
            'target': 'current',
            'res_id': 'view_partner_migration_tree',
            'type': 'ir.actions.act_window'
        }
    
class BatomCreatSupplierWarehouses(models.TransientModel):
    _name = "batom.create_supplier_warehouses"
    _description = "Create Supplier Warehouses"
    root_location_id = fields.Integer(string='Root Location ID', required=True)

    @api.multi
    def create_supplier_warehouses(self):
        this = self[0]
        location_id = this.root_location_id
        try:
            self.ensure_one()
            locationModel = self.env['stock.location']
            supplierRootLocation = locationModel.browse(location_id)
            if supplierRootLocation != None:
                partnerLocations = locationModel.search_read([
                    '|', ('active', '=', True), ('active', '=', False),
                    ('partner_id', '!=', None)
                    ], ['partner_id'])
                supplierIdsWithLocations = []
                for partnerLocation in partnerLocations:
                    supplierIdsWithLocations.append(partnerLocation['partner_id'][0])
                suppliers = self.env['res.partner'].search([
                    ('supplier', '=', True),
                    ('x_supplier_code', '!=', None),
                    ('id', 'not in', supplierIdsWithLocations),
                    ])
                for supplier in suppliers:
                    try:
                        name = supplier.display_name + ' (' + supplier.x_supplier_code + ')'
                        newLocation = locationModel.create({
                            'name': name,
                            'partner_id': supplier.id,
                            'location_id': supplierRootLocation.id,
                            'usage': 'supplier',
                        })
                    except Exception:
                        _logger.warning('Exception in create_supplier_warehouses:', exc_info=True)
                self.env.cr.commit()            
        except Exception:
            _logger.warning('Exception in create_supplier_warehouses:', exc_info=True)
    
class BatomMigrateChartOfAccount(models.TransientModel):
    _name = "batom.migrate_chart_of_account"
    _description = "Migrate Chart of Account"

    def _accountTypeIdConversion(self, chiSubClsID, chiSubjectID):
        returnedUserTypeId = None
        if chiSubClsID and chiSubClsID.strip():
            if chiSubClsID == '11':
                if int(chiSubjectID) < 1130000:
                    returnedUserTypeId = 3
                elif int(chiSubjectID) <= 1179000:
                    returnedUserTypeId = 1
            else:
                userTypeIdMap = ({
                    "12": 5,
                    "14": 6,
                    "15": 8,
                    "16": 6,
                    "17": 6,
                    "18": 6,
                    "21": 9,
                    "22": 9,
                    "25": 10,
                    "28": 10,
                    "31": 11,
                    "32": 11,
                    "33": 11,
                    "41": 14,
                    "42": 14,
                    "43": 14,
                    "46": 14,
                    "51": 17,
                    "52": 17,
                    "53": 17,
                    "54": 17,
                    "55": 17,
                    "56": 17,
                    "57": 17,
                    "59": 17,
                    "61": 16,
                    "62": 16,
                    "63": 16,
                    "71": 13,
                    "73": 16,
                    "81": 16,
                    "91": 17,
                    "92": 17,
                    })
                try:
                    returnedUserTypeId = userTypeIdMap[chiSubClsID]
                except Exception:
                    _logger.warning('Exception in migrate_chart_of_account:', exc_info=True)
                
        return returnedUserTypeId
        
    def _odooAccountIdFromCode(self, code):
        accountId = None
        if code and code.strip():
            accountIds = self.env['account.account'].search([('code', '=', code)]).ids
            if len(accountIds) > 0:
                accountId = accountIds.pop(0)
        return accountId
        
    @api.multi
    def migrate_chart_of_account(self):
        try:
            self.ensure_one()
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            batomAccountTypes = self.env['batom.account.type'].search([])
            if len(batomAccountTypes) == 0:
                chiAccountTypes = dbChi.execute('SELECT SubClsID, SubClsName FROM comSubjectCls ORDER BY SubClsID')
                while len(chiAccountTypes) > 0:
                    try:
                        chiAccountType = chiAccountTypes.pop(0)
                        self.env['batom.account.type'].create({
                            'code': chiAccountType.SubClsID,
                            'name': chiAccountType.SubClsName
                            })
                    except Exception:
                        _logger.warning('Exception in migrate_chart_of_account:', exc_info=True)
                        continue
                batomAccountTypes = self.env['batom.account.type'].search([])
                self.env.cr.commit()            
            
            batomAccountTypeIds = {}
            for batomAccountType in batomAccountTypes:
                batomAccountTypeIds[batomAccountType.code] = batomAccountType.id
            # base_external_dbsource seems to have size limit of the query result
            # query the values directly may not returns all qualified records
            # for some reason, '1441000' cannot be retrieved.  ignore it for now
            chiAccountIDs = dbChi.execute('SELECT SubjectID FROM comSubject ORDER BY SubjectID')
            accountModel = self.env['account.account']
            for chiAccountID in chiAccountIDs:
                try:
                    chiAccounts = dbChi.execute("SELECT SubClsID, SubjectID, SubjectName, ParentSubID, CurrID, Description FROM comSubject WHERE SubjectID = '" + chiAccountID.SubjectID + "'")
                    if len(chiAccounts) > 0:
                        chiAccount = chiAccounts.pop(0)
                        currency_id = _currencyIdConversion(self, chiAccount.CurrID)
                        account_type_id = self._accountTypeIdConversion(chiAccount.SubClsID, chiAccount.SubjectID)
                        reconcile = True if (account_type_id in (1, 2)) else False
                        parent_id = self._odooAccountIdFromCode(chiAccount.ParentSubID)
                        if not parent_id:
                            parent_id = None
                        accountValues = ({
                            'name': chiAccount.SubjectName,
                            'currency_id': currency_id,
                            'code': chiAccount.SubjectID,
                            'user_type_id': account_type_id,
                            'note': chiAccount.Description,
                            'reconcile': reconcile,
                            'x_batom_type_id': batomAccountTypeIds[chiAccount.SubClsID],
                            'x_batom_parent_id': parent_id,
                            })
                        
                        odooAccounts = accountModel.search([('code', '=', chiAccount.SubjectID)])
                        if len(odooAccounts) == 0:
                            accountModel.create(accountValues)
                        else:
                            odooAccounts[0].write(accountValues)
                except Exception:
                    _logger.warning('Exception in migrate_chart_of_account:', exc_info=True)
                    continue
            self.env.cr.commit()            
        except Exception:
            _logger.warning('Exception in migrate_chart_of_account:', exc_info=True)
    
class BatomMigrateProduct(models.TransientModel):
    _name = "batom.migrate_product"
    _description = "Migrate Products"
        
    def migrate_chiProduct(self, cursorChi):
        # base_external_dbsource seems to have size limit of the query result
        # query the values directly may not returns all qualified records
        chiProductIDs = cursorChi.execute('SELECT ProdID FROM comProduct ORDER BY ProdID').fetchall()
        productModel = self.env['product.product']
        productIDs = []
        for chiProductID in chiProductIDs:
            productIDs.append(chiProductID.ProdID)
            
        for productID in productIDs:
            try:
                chiProduct = cursorChi.execute(u"SELECT ProdID, ClassID, ProdForm, Unit, ProdName, EngName, ProdDesc, "
                    u"CurrID, CAvgCost, SuggestPrice, NWeight, NUnit "
                    u"FROM comProduct "
                    u"WHERE ProdID = '" + productID.decode('utf-8') + u"'"
                    ).fetchone()
                if chiProduct != None:
                    if chiProduct.EngName and chiProduct.EngName.strip():
                        name = chiProduct.EngName
                    elif chiProduct.ProdName and chiProduct.ProdName.strip():
                        name = chiProduct.ProdName
                    else:
                        name = chiProduct.ProdID
                    currency_id = _currencyIdConversion(self, chiProduct.CurrID)
                    uom_id = _uomIdConversion(self, chiProduct.Unit)
                    # ProdForm: 1-物料，2半成品，3-成品，4-採購件，5-組合品，6-非庫存品，7-非庫存品(管成本)，8-易耗品
                    # ClassID ClassName
                    # --------------
                    # *	特殊科目
                    # 1	運費
                    # 2	雜項支出
                    # 3	包裝費
                    # 4	樣品費
                    # 5	製-包裝費
                    # 6	進料
                    # 7	製-模具費
                    # A	原料
                    # B	半成品
                    # C	成品
                    # D	零配件
                    # E	物料
                    # F	模治具
                    # G	紙箱
                    # H	開發件
                    # I	商品
                    sale_ok = False
                    purchase_ok = False
                    type = 'consu' # 'consu', 'service', 'product'
                    if chiProduct.ProdForm == 3 or chiProduct.ClassID == 'C' or chiProduct.ClassID == 'I':
                        sale_ok = True
                    if chiProduct.ProdForm == 4:
                        purchase_ok = True
                    if chiProduct.ProdForm <= 5:
                        type = 'product'
                    productValues = ({
                        'name': name,
                        'default_code': chiProduct.ProdID,
                        'type': type,
                        'description': chiProduct.ProdDesc,
                        'sale_ok': sale_ok,
                        'purchase_ok': purchase_ok,
                        'currency_id': currency_id,
                        'standard_price': chiProduct.CAvgCost,
                        'price': chiProduct.SuggestPrice,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        'weight': chiProduct.NWeight,
                        # warehouse_id, location_id, routes_id,
                        })
                    
                    odooProducts = productModel.search([('default_code', '=', chiProductID.ProdID)])
                    if len(odooProducts) == 0:
                        odooProduct = productModel.create(productValues)
                    else:
                        odooProduct = odooProducts[0]
                        odooProduct.write(productValues)
                    _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, name, chiProduct.ProdName)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
        self.env.cr.commit()
        
    def migrate_inProduct(self, cursorBatom):
        inProducts = cursorBatom.execute('SELECT ProdID, ProdName, EngName, Remark, Unit FROM Product ORDER BY ProdID').fetchall()
        productModel = self.env['product.product']
        for inProduct in inProducts:
            try:
                odooProducts = productModel.search([('default_code', '=', inProduct.ProdID)])
                if len(odooProducts) == 0:
                    if inProduct.EngName and inProduct.EngName.strip():
                        name = inProduct.EngName
                    elif inProduct.ProdName and inProduct.ProdName.strip():
                        name = inProduct.ProdName
                    else:
                        name = inProduct.ProdID
                    uom_id = _uomIdConversion(self, inProduct.Unit)
                    sale_ok = False
                    purchase_ok = False
                    type = 'product'
                    productValues = ({
                        'name': name,
                        'default_code': inProduct.ProdID,
                        'type': type,
                        'sale_ok': sale_ok,
                        'purchase_ok': purchase_ok,
                        'description': inProduct.Remark,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        })
                    
                    odooProduct = productModel.create(productValues)
                    _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, name, inProduct.ProdName)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
        self.env.cr.commit()
        
    def migrate_chiProcess(self, cursorChi):
        processes = cursorChi.execute('SELECT ProgramID, ProgramName, Remark FROM prdMakeProgram ORDER BY ProgramID').fetchall()
        productModel = self.env['product.product']
        for process in processes:
            try:
                if process.Remark and process.Remark.strip():
                    name = process.Remark
                else:
                    name = process.ProgramName
                sale_ok = False
                purchase_ok = True
                type = 'service'
                productValues = ({
                    'name': name,
                    'default_code': process.ProgramID,
                    'type': type,
                    'sale_ok': sale_ok,
                    'purchase_ok': purchase_ok,
                    'x_is_process': True,
                    })
                
                odooProducts = productModel.search([('default_code', '=', process.ProgramID)])
                if len(odooProducts) == 0:
                    odooProduct = productModel.create(productValues)
                else:
                    odooProduct = odooProducts[0]
                    odooProduct.write(productValues)
                _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, name, process.ProgramName)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
        self.env.cr.commit()
        
    def migrate_inProcess(self, cursorBatom):
        processes = cursorBatom.execute('SELECT ProcessID, ProcessName, Remark FROM Process ORDER BY ProcessID').fetchall()
        productModel = self.env['product.product']
        for process in processes:
            try:
                if process.ProcessID and process.ProcessID.strip():
                    odooProducts = productModel.search([('default_code', '=', process.ProcessID)])
                    if len(odooProducts) == 0:
                        if process.Remark and process.Remark.strip():
                            name = process.Remark
                        else:
                            name = process.ProcessName
                        sale_ok = False
                        purchase_ok = True
                        type = 'service'
                        productValues = ({
                            'name': name,
                            'default_code': process.ProcessID,
                            'type': type,
                            'sale_ok': sale_ok,
                            'purchase_ok': purchase_ok,
                            'x_is_process': True,
                            })
                        
                        odooProduct = productModel.create(productValues)
                        _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, name, process.ProcessName)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
        self.env.cr.commit()
            
    @api.multi
    def migrate_product(self):
        try:
            self.ensure_one()
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            connChi = dbChi.conn_open()
            cursorChi = connChi.cursor()
            connBatom = dbBatom.conn_open()
            cursorBatom = connBatom.cursor()

            self.migrate_chiProduct(cursorChi)
            self.migrate_inProduct(cursorBatom)
            self.migrate_chiProcess(cursorChi)
            self.migrate_inProcess(cursorBatom)
            connChi.close()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_product:', exc_info=True)
            if connChi:
                connChi.close()
            if connBatom:
                connBatom.close()
    
class BatomPartnerMigration(models.Model):
    _name = "batom.partner_migration"
    _description = 'Partner Data Migration'
    
    type = fields.Selection([(1, 'Customer'), (2, 'Sppplier')], string='Type', required=True)
    in_id = fields.Char('入料 ID', required=False, size=20)
    in_short_name = fields.Char('入料 Short Name', required=False, size=12)
    in_full_name = fields.Char('入料 Full Name', required=False, size=80)
    chi_id = fields.Char('正航 ID', required=False, size=20)
    chi_short_name = fields.Char('正航 Short Name', required=False, size=12)
    chi_full_name = fields.Char('正航 Full Name', required=False, size=80)
    odoo_id = fields.Char('Odoo ID', required=False, size=20)
    odoo_short_name = fields.Char('Odoo Short Name', required=False, size=12)
    odoo_full_name = fields.Char('Odoo Full Name', required=False, size=80)

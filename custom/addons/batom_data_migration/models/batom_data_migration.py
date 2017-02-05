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

#BX
#P C
#SET
#桶
#EA
#ＰＣ
#英呎
#M
#PCS
#Kg

_uomMapping = ({
    'Kg': 'kg',
    'M': 'm',
    'P C': 'PC',
    'pc': 'PC',
    'pcs': 'PCS',
    u'ＰＣ': 'PC',
    'set': 'SET',
    })
def _uomIdConversion(self, uom):
    uomModel = self.env['product.uom']
    uomCategoryModel = self.env['product.uom.categ']
    uomId = 1 # uom cannot be null
    if uom and uom.strip():
        uom = uom.strip()
        if uom in _uomMapping:
            uom = _uomMapping[uom]
        uomIds = uomModel.search([('name', '=', uom)]).ids
        if len(uomIds) > 0:
            uomId = uomIds.pop(0)
        else:
            factor = 1
            rounding = 0.01
            uom_type = 'bigger'
            if uom == u'桶':
                category_id = uomCategoryModel.with_context(lang='en_US').search([('name', '=', 'Volume')])[0].id
            else:
                category_id = uomCategoryModel.with_context(lang='en_US').search([('name', '=', 'Unit')])[0].id
            uomValues = ({
                'name': uom,
                'category_id': category_id,
                'factor': factor,
                'rounding': rounding,
                'uom_type': uom_type,
                })
            odooUom = uomModel.create(uomValues)
            if uom == u'桶':
                _updateTranslation(self, 'product.uom,name', odooUom.id, 'barrel', uom)
            
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
        ('src', '=', value),
        ])
    if len(translations) == 0:
        translationModel.create(values)
    else:
        translations[0].write(values)
        
def _getSupplier(self, supplierCode, defaultIfNotFound):
    supplier = None
    if supplierCode != None:
        suppliers = self.env['res.partner'].search([
            ('supplier', '=', True),
            ('x_supplier_code', '=', supplierCode)
            ])
    else:
        suppliers = []
    
    if len(suppliers) > 0:
        supplier =  suppliers[0]
    elif defaultIfNotFound:
        supplierCompany = self.env['res.company']._company_default_get()
        if supplierCompany:
            supplier = supplierCompany.partner_id

    return supplier
        
def _getProduct(self, productCode):
    product = None
    products = self.env['product.product'].search([
        ('default_code', '=', productCode)
        ])
    if len(products) > 0:
        product =  products[0]

    return product
        
def _getProductTemplate(self, productCode):
    product = None
    products = self.env['product.template'].search([
        ('default_code', '=', productCode)
        ])
    if len(products) > 0:
        product =  products[0]

    return product

def _getWorkcenter(self, processCode, supplierCode, createIfNotExist):
    workcenter = None
    try:
        process = self.env['product.template'].search([
            ('x_is_process', '=', True),
            ('default_code', '=', processCode)
            ])[0]
        supplier = _getSupplier(self, supplierCode, True)
        workcenterModel = self.env['mrp.workcenter']
        workcenters = workcenterModel.search([
            ('x_supplier_id', '=', supplier.id),
            ('x_process_id', '=', process.id)
            ])
        if len(workcenters) > 0:
            workcenter =  workcenters[0]
        elif createIfNotExist:
            workcenterValues = ({
                'name': process.name + ' <- ' + supplier.display_name,
                'x_process_id': process.id,
                'x_supplier_id': supplier.id,
                'resource_type': 'material',
                })
            workcenter = workcenterModel.create(workcenterValues);
    except Exception:
        _logger.warning('Exception in migrate_bom:', exc_info=True)

    return workcenter
    
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


class BatomProductProduct(models.Model):
    #_name = 'batom.product.product'
    _inherit = 'product.product'

    seller_ids = fields.One2many('product.supplierinfo', 'product_id', 'Vendors')

class BatomProductTemplate(models.Model):
    #_name = 'batom.product.template'
    _inherit = 'product.template'

    x_is_process = fields.Boolean('Manufacturing Process', default=False)
    x_saved_code = fields.Char('Internal Reference with Variants')
    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',
        inverse='_set_default_code', store=True)

    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.default_code = template.product_variant_ids.default_code
        for template in (self - unique_variants):
            template.default_code = template.x_saved_code

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
                name = companyName + u', ' + contactName.decode('utf-8')
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
            batomCustomers = dbBatom.execute('SELECT Id, ShortName, FullName FROM Customer ORDER BY Id')
            chiCustomers = dbChi.execute('SELECT Id, ShortName, FullName FROM comCustomer WHERE Flag=1 ORDER BY Id')
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
                    batomCustomer = _partner_migration(customer.Id, customer.ShortName, customer.FullName)
                if chiCustomer == None and len(chiCustomers) > 0:
                    customer = chiCustomers.pop(0)
                    chiCustomer = _partner_migration(customer.Id, customer.ShortName, customer.FullName)
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

            batomSuppliers = dbBatom.execute('SELECT Id, ShortName, FullName FROM Supplier ORDER BY Id')
            chiSuppliers = dbChi.execute('SELECT Id, ShortName, FullName FROM comCustomer where Flag=2 ORDER BY Id')
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
                    batomSupplier = _partner_migration(supplier.Id, supplier.ShortName, supplier.FullName)
                if chiSupplier == None and len(chiSuppliers) > 0:
                    supplier = chiSuppliers.pop(0)
                    chiSupplier = _partner_migration(supplier.Id, supplier.ShortName, supplier.FullName)
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
                            "SELECT Id, ShortName, FullName, LinkMan, LinkManProf, "
                            "AreaId, ClassId, CurrencyId, Email, FaxNo, InvoiceHead, TaxNo, "
                            "MobileTel, Telephone1, Telephone2, Telephone3, WebAddress "
                            "FROM comCustomer "
                            "WHERE Flag=" + str(migration.type) + " AND Id='" + migration.chi_id + "'"
                            )
                        chiPartner = dbChi.execute(sql).pop(0)
                        
                        if chiPartner != None:
                            sql = ("SELECT AddrOfInvo, "
                                "A1.ZipCode AS ZipCode1, A1.Address AS Address1, A1.LinkMan AS LinkMan1, A1.LinkManProf AS LinkManProf1, A1.Telephone AS Telephone1, A1.FaxNo AS FaxNo1, A1.Memo AS Memo1, "
                                "A2.ZipCode AS ZipCode2, A2.Address AS Address2, A2.LinkMan AS LinkMan2, A2.LinkManProf AS LinkManProf2, A2.Telephone AS Telephone2, A2.FaxNo AS FaxNo2, A2.Memo AS Memo2, "
                                "A3.ZipCode AS ZipCode3, A3.Address AS Address3, A3.LinkMan AS LinkMan3, A3.LinkManProf AS LinkManProf3, A3.Telephone AS Telephone3, A3.FaxNo AS FaxNo3, A3.Memo AS Memo3 "
                                "FROM comCustDesc AS C "
                                "LEFT JOIN comCustAddress A1 ON (A1.Flag = C.Flag AND A1.Id = C.Id AND A1.AddrId = C.DeliverAddrId) "
                                "LEFT JOIN comCustAddress A2 ON (A2.Flag = C.Flag AND A2.Id = C.Id AND A2.AddrId = C.AddrId) "
                                "LEFT JOIN comCustAddress A3 ON (A3.Flag = C.Flag AND A3.Id = C.Id AND A3.AddrId = C.EngAddrId) "
                                "WHERE C.Flag=" + str(migration.type) + " AND C.Id='" + migration.chi_id + "'"
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
                            
                            categoryId = self._partnerCategoryConversion(migration.type, chiPartner.ClassId)
                            newPartner = partnerModel.create({
                                codeColumnName: chiPartner.Id,
                                'country_id': self._countryIdConversion(chiPartner.AreaId),
                                'category_id': [(4, categoryId)] if (categoryId != None) else None,
                                'property_purchase_currency_id': _currencyIdConversion(self, chiPartner.CurrencyId),
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
                                "WHERE Flag=" + str(migration.type) + " AND CustomId='" + chiPartner.Id + "'"
                                )
                            if len(linkMans) > 0:
                                for linkMan in linkMans:
                                    contact = _partner_address(None, None, linkMan.PersonName, linkMan.ProfTitle, linkMan.Telephone, linkMan.Mobile, linkMan.FaxNo, linkMan.Email, linkMan.Memo)
                                    self._createPartnerContact('contact', newPartner, contact)
                    elif migration.in_id != None and migration.in_id and migration.in_id.strip():
                        if migration.type == 1:
                            inPartner = dbBatom.execute(
                                "select Id, ShortName, FullName "
                                "from Customer where Id='" + migration.in_id + "'"
                                ).pop(0)
                        else:
                            inPartner = dbBatom.execute(
                                "select Id, ShortName, FullName "
                                "from Supplier where Id='" + migration.in_id + "'"
                                ).pop(0)
                        if inPartner != None:
                            newPartner = partnerModel.create({
                                codeColumnName: inPartner.Id,
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
    root_location_id = fields.Integer(string='Root Location Id', required=True)

    @api.multi
    def create_supplier_warehouses(self):
        this = self[0]
        location_id = this.root_location_id
        try:
            self.ensure_one()
            locationModel = self.env['stock.location']
            supplierRootLocation = locationModel.browse(location_id)
            if supplierRootLocation != None:
                partnerLocations = locationModel.search([
                    '|', ('active', '=', True), ('active', '=', False),
                    ('partner_id', '!=', None)
                    ], ['partner_id'])
                supplierIdsWithLocations = []
                for partnerLocation in partnerLocations:
                    supplierIdsWithLocations.append(partnerLocation.partner_id)
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

    def _accountTypeIdConversion(self, chiSubClsId, chiSubjectId):
        returnedUserTypeId = None
        if chiSubClsId and chiSubClsId.strip():
            if chiSubClsId == '11':
                if int(chiSubjectId) < 1130000:
                    returnedUserTypeId = 3
                elif int(chiSubjectId) <= 1179000:
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
                    returnedUserTypeId = userTypeIdMap[chiSubClsId]
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
                chiAccountTypes = dbChi.execute('SELECT SubClsId, SubClsName FROM comSubjectCls ORDER BY SubClsId')
                while len(chiAccountTypes) > 0:
                    try:
                        chiAccountType = chiAccountTypes.pop(0)
                        self.env['batom.account.type'].create({
                            'code': chiAccountType.SubClsId,
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
            chiAccountIds = dbChi.execute('SELECT SubjectId FROM comSubject ORDER BY SubjectId')
            accountModel = self.env['account.account']
            for chiAccountId in chiAccountIds:
                try:
                    chiAccounts = dbChi.execute("SELECT SubClsId, SubjectId, SubjectName, ParentSubId, CurrId, Description FROM comSubject WHERE SubjectId = '" + chiAccountId.SubjectId + "'")
                    if len(chiAccounts) > 0:
                        chiAccount = chiAccounts.pop(0)
                        currency_id = _currencyIdConversion(self, chiAccount.CurrId)
                        account_type_id = self._accountTypeIdConversion(chiAccount.SubClsId, chiAccount.SubjectId)
                        reconcile = True if (account_type_id in (1, 2)) else False
                        parent_id = self._odooAccountIdFromCode(chiAccount.ParentSubId)
                        if not parent_id:
                            parent_id = None
                        accountValues = ({
                            'name': chiAccount.SubjectName,
                            'currency_id': currency_id,
                            'code': chiAccount.SubjectId,
                            'user_type_id': account_type_id,
                            'note': chiAccount.Description,
                            'reconcile': reconcile,
                            'x_batom_type_id': batomAccountTypeIds[chiAccount.SubClsId],
                            'x_batom_parent_id': parent_id,
                            })
                        
                        odooAccounts = accountModel.search([('code', '=', chiAccount.SubjectId)])
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
        
    def _migrate_chiProduct(self, cursorChi):
        # base_external_dbsource seems to have size limit of the query result
        # query the values directly may not returns all qualified records
        chiProductIds = cursorChi.execute('SELECT ProdId FROM comProduct ORDER BY ProdId').fetchall()
        productModel = self.env['product.product']
        productIds = []
        for chiProductId in chiProductIds:
            productIds.append(chiProductId.ProdId)
            
        nCount = len(productIds)
        nDone = 0
        for productId in productIds:
            try:
                chiProduct = cursorChi.execute(u"SELECT ProdId, ClassId, ProdForm, Unit, ProdName, EngName, ProdDesc, "
                    u"CurrId, CAvgCost, SuggestPrice, NWeight, NUnit "
                    u"FROM comProduct "
                    u"WHERE ProdId = '" + productId.decode('utf-8') + u"'"
                    ).fetchone()
                if chiProduct != None:
                    if chiProduct.ProdName and chiProduct.ProdName.strip():
                        name = chiProduct.ProdName
                    else:
                        name = chiProduct.ProdId
                    currency_id = _currencyIdConversion(self, chiProduct.CurrId)
                    uom_id = _uomIdConversion(self, chiProduct.Unit.decode('utf-8'))
                    # ProdForm: 1-物料，2半成品，3-成品，4-採購件，5-組合品，6-非庫存品，7-非庫存品(管成本)，8-易耗品
                    # ClassId ClassName
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
                    tracking = 'none'
                    if chiProduct.ProdForm == 3 or chiProduct.ClassId == 'C' or chiProduct.ClassId == 'I':
                        sale_ok = True
                    if chiProduct.ProdForm in [1, 2, 4]:
                        purchase_ok = True
                    if chiProduct.ProdForm <= 5:
                        type = 'product'
                        tracking = 'lot'
                    productValues = ({
                        'name': name,
                        'default_code': chiProduct.ProdId,
                        'x_saved_code': chiProduct.ProdId,
                        'type': type,
                        'tracking': tracking,
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
                    
                    odooProducts = productModel.search([('default_code', '=', chiProduct.ProdId)])
                    if len(odooProducts) == 0:
                        odooProduct = productModel.create(productValues)
                    else:
                        odooProduct = odooProducts[0]
                        odooProduct.write(productValues)
                    if chiProduct.EngName and chiProduct.EngName.strip():
                        engName = chiProduct.EngName
                        _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, engName, name)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                import pdb; pdb.set_trace()
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
        
    def _migrate_inProduct(self, cursorBatom):
        inProducts = cursorBatom.execute('SELECT ProdId, ProdName, EngName, Remark, Unit FROM Product ORDER BY ProdId').fetchall()
        productModel = self.env['product.product']
        nCount = len(inProducts)
        nDone = 0
        for inProduct in inProducts:
            try:
                odooProducts = productModel.search([('default_code', '=', inProduct.ProdId)])
                if len(odooProducts) == 0:
                    if inProduct.ProdName and inProduct.ProdName.strip():
                        name = inProduct.ProdName
                    else:
                        name = inProduct.ProdId
                    uom_id = _uomIdConversion(self, inProduct.Unit.decode('utf-8'))
                    sale_ok = False
                    purchase_ok = False
                    type = 'product'
                    tracking = 'lot'
                    productValues = ({
                        'name': name,
                        'default_code': inProduct.ProdId,
                        'x_saved_code': inProduct.ProdId,
                        'type': type,
                        'tracking': tracking,
                        'sale_ok': sale_ok,
                        'purchase_ok': purchase_ok,
                        'description': inProduct.Remark,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        })
                    
                    odooProduct = productModel.create(productValues)
                    if inProduct.EngName and inProduct.EngName.strip():
                        engName = inProduct.EngName
                        _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, engName, name)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
        
    def _migrate_chiProcess(self, cursorChi):
        processes = cursorChi.execute('SELECT ProgramId, ProgramName, Remark FROM prdMakeProgram ORDER BY ProgramId').fetchall()
        productModel = self.env['product.product']
        nCount = len(processes)
        nDone = 0
        for process in processes:
            try:
                name = process.ProgramName
                sale_ok = False
                purchase_ok = True
                type = 'service'
                productValues = ({
                    'name': name,
                    'default_code': process.ProgramId,
                    'x_saved_code': process.ProgramId,
                    'type': type,
                    'sale_ok': sale_ok,
                    'purchase_ok': purchase_ok,
                    'x_is_process': True,
                    })
                
                odooProducts = productModel.search([('default_code', '=', process.ProgramId)])
                if len(odooProducts) == 0:
                    odooProduct = productModel.create(productValues)
                else:
                    odooProduct = odooProducts[0]
                    odooProduct.write(productValues)
                if process.Remark and process.Remark.strip():
                    engName = process.Remark
                    _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, engName, name)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
        
    def _migrate_inProcess(self, cursorBatom):
        processes = cursorBatom.execute('SELECT ProcessId, ProcessName, Remark FROM Process ORDER BY ProcessId').fetchall()
        productModel = self.env['product.product']
        nCount = len(processes)
        nDone = 0
        for process in processes:
            try:
                if process.ProcessId and process.ProcessId.strip():
                    odooProducts = productModel.search([('default_code', '=', process.ProcessId)])
                    if len(odooProducts) == 0:
                        name = process.ProcessName
                        sale_ok = False
                        purchase_ok = True
                        type = 'service'
                        productValues = ({
                            'name': name,
                            'default_code': process.ProcessId,
                            'type': type,
                            'sale_ok': sale_ok,
                            'purchase_ok': purchase_ok,
                            'description': process.Remark,
                            'x_is_process': True,
                            })
                        
                        odooProduct = productModel.create(productValues)
                        if process.Remark and process.Remark.strip():
                            engName = process.Remark
                            _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, engName, name)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
        
    def _migrate_inShopProcess(self, cursorBatom):
        processes = cursorBatom.execute('SELECT ProcessId, ShopProcess, Type FROM ShopProcess ORDER BY ProcessId').fetchall()
        productModel = self.env['product.product']
        for process in processes:
            try:
                if process.ProcessId and process.ProcessId.strip():
                    odooProducts = productModel.search([('default_code', '=', process.ProcessId)])
                    if len(odooProducts) == 0:
                        name = process.ShopProcess
                        sale_ok = False
                        purchase_ok = True
                        type = 'service'
                        productValues = ({
                            'name': name,
                            'default_code': process.ProcessId,
                            'type': type,
                            'sale_ok': sale_ok,
                            'purchase_ok': purchase_ok,
                            'description': process.Type,
                            'x_is_process': True,
                            })
                        
                        odooProduct = productModel.create(productValues)
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

            self._migrate_chiProduct(cursorChi)
            self._migrate_inProduct(cursorBatom)
            self._migrate_chiProcess(cursorChi)
            self._migrate_inProcess(cursorBatom)
            self._migrate_inShopProcess(cursorBatom)
            connChi.close()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_product:', exc_info=True)
            if connChi:
                connChi.close()
            if connBatom:
                connBatom.close()
    
class BatomMigrateBom(models.TransientModel):
    _name = "batom.migrate_bom"
    _description = "Migrate BoM"
    _defaultMaterialAcquisitionProcess = None
    _defaultMaterialAcquisitionWorkcenter = None
    
    def _getDefaultMaterialAcquisitionProcess(self):
        process = None
        code = 'MTAC'
        name = '領料'
        try:
            processes = self.env['product.template'].search([
                ('x_is_process', '=', True),
                ('default_code', '=', code)
                ])
            if len(processes) > 0:
                process = processes[0]
            else:
                sale_ok = False
                purchase_ok = True
                type = 'service'
                process = self.env['product.product'].create({
                    'name': name,
                    'default_code': code,
                    'x_saved_code': code,
                    'type': type,
                    'sale_ok': sale_ok,
                    'purchase_ok': purchase_ok,
                    'x_is_process': True,
                    })
                _updateTranslation(self, 'product.template,name', process.product_tmpl_id.id, 'material acquisition', name)
        except Exception:
            _logger.warning('Exception in migrate_bom:', exc_info=True)
            
        return process
    
    def _getDefaultMaterialAcquisitionWorkcenter(self):
        if self._defaultMaterialAcquisitionProcess == None:
            self._defaultMaterialAcquisitionProcess = self._getDefaultMaterialAcquisitionProcess()
        return _getWorkcenter(self, self._defaultMaterialAcquisitionProcess.default_code, None, True)
    
    def _createRouting(self, chiBom, chiBomMaterials, chiBomProcesses):
        odooRouting = None
        try:
            routingModel = self.env['mrp.routing']
            productTemplate = _getProductTemplate(self, chiBom.ProductId)
            if productTemplate == None:
                _logger.warning('Product template ' + chiBom.ProductId + ' not found in migrate_bom:', exc_info=True)
            else:
                odooRoutings = routingModel.search([
                    ('x_product_id', '=', productTemplate.id),
                    ('x_batom_bom_no', '=', chiBom.ItemNo),
                    ])
                if len(odooRoutings) <= 0:
                    routingValues = ({
                        'code': u'~' + chiBom.ProductId.decode('utf-8') + u"#" + str(chiBom.ItemNo),
                        'name': u'RO/' + chiBom.ProductName.decode('utf-8') + u" #" + str(chiBom.ItemNo),
                        'x_product_id': productTemplate.id,
                        'x_batom_bom_no': chiBom.ItemNo,
                        'note': u'由正航 ' + chiBom.ProductId.decode('utf-8') + u'(' + chiBom.ProductName.decode('utf-8') + u') BoM自動產生的製程路徑',
                        })
                    odooRouting = routingModel.create(routingValues)
                    routingWorkcenterModel = self.env['mrp.routing.workcenter']
                    sequence = 0
                    if len(chiBomMaterials) > 0:
                        if self._defaultMaterialAcquisitionWorkcenter == None:
                            self._defaultMaterialAcquisitionWorkcenter = self._getDefaultMaterialAcquisitionWorkcenter()
                        odooWorkcenter = self._defaultMaterialAcquisitionWorkcenter
                        time_cycle_manual = 1
                        sequence += 5
                        routingWorkcenterValues = ({
                            'sequence': sequence,
                            'name': odooWorkcenter.x_process_id.name,
                            'workcenter_id': odooWorkcenter.id,
                            'routing_id': odooRouting.id,
                            'note': u'由正航 ' + chiBom.ProductId.decode('utf-8') + u'(' + chiBom.ProductName.decode('utf-8') + u') BoM自動產生的' + odooWorkcenter.x_process_id.name + u'作業',
                            'time_mode': 'manual',
                            'time_cycle_manual': time_cycle_manual,
                            })
                        routingWorkcenter = routingWorkcenterModel.create(routingWorkcenterValues)
                    for chiBomProcess in chiBomProcesses:
                        odooWorkcenter = _getWorkcenter(self, chiBomProcess.MkPgmId, chiBomProcess.Producer, True)
                        import pdb; pdb.set_trace()
                        time_cycle_manual = (
                            1 if (chiBomProcess.WorkTimeOfBatch == None or chiBomProcess.WorkTimeOfBatch <= 0)
                            else chiBomProcess.WorkTimeOfBatch
                            )
                        sequence += 5
                        routingWorkcenterValues = ({
                            'sequence': sequence,
                            'name': odooWorkcenter.x_process_id.name,
                            'workcenter_id': odooWorkcenter.id,
                            'routing_id': odooRouting.id,
                            'note': u'由正航 ' + chiBom.ProductId.decode('utf-8') + u'(' + chiBom.ProductName.decode('utf-8') + u') BoM自動產生的' + odooWorkcenter.x_process_id.name + u'作業',
                            'time_mode': 'manual',
                            'time_cycle_manual': time_cycle_manual,
                            })
                        routingWorkcenter = routingWorkcenterModel.create(routingWorkcenterValues)
        except Exception:
            _logger.warning('Exception in migrate_bom:', exc_info=True)
            
        return odooRouting
    
    def _createBomLines(self, odooBom, odooRouting, chiBom, chiBomMaterials, chiBomProcesses):
        bomLineModel = self.env['mrp.bom.line']
        bomLineModel.search([('bom_id', '=', odooBom.id)]).unlink()
        routingWorkcenterModel = self.env['mrp.routing.workcenter']
        routingWorkcenters = routingWorkcenterModel.search([
            ('routing_id', '=', odooRouting.id)],
            order='sequence',
            )
        if self._defaultMaterialAcquisitionProcess == None:
            self._defaultMaterialAcquisitionProcess = self._getDefaultMaterialAcquisitionProcess()
        idxMaterials = 0
        idxProcesses = 0
        sequence = 0
        while idxMaterials < len(chiBomMaterials) or idxProcesses < len(chiBomProcesses):
            try:
                bomLineValues = None
                if sequence == 0 and len(chiBomMaterials) > 0:
                    # add the material acquisition process as the first process
                    product = self._defaultMaterialAcquisitionProcess
                    if product == None:
                        _logger.warning('_defaultMaterialAcquisitionProcess not found in migrate_bom:', exc_info=True)
                    else:
                        routing_id = None
                        operation_id = None
                        # first routingWorkcenter is the added material acquisition workcenter
                        if len(routingWorkcenters) > 0:
                            routing_id = odooRouting.id
                            operation_id = routingWorkcenters[0].id
                        sequence += 5
                        bomLineValues = ({
                            'bom_id': odooBom.id,
                            'sequence': sequence,
                            'product_id': product.id,
                            'product_qty': 1,
                            'product_uom_id': product.uom_id.id,
                            'routing_id': routing_id,
                            'operation_id': operation_id,
                            })
                elif (idxMaterials < len(chiBomMaterials) and
                        (idxProcesses >= len(chiBomProcesses) or 
                        chiBomMaterials[idxMaterials].SerNo <= chiBomProcesses[idxProcesses].SerNo
                        )):
                    product = _getProduct(self, chiBomMaterials[idxMaterials].SubProdId)
                    if product == None:
                        _logger.warning('Product template ' + chiBomMaterials[idxMaterials].SubProdId + ' not found in migrate_bom:', exc_info=True)
                    else:
                        routing_id = None
                        operation_id = None
                        # first routingWorkcenter is the added material acquisition workcenter
                        if len(routingWorkcenters) > 0:
                            routing_id = odooRouting.id
                            operation_id = routingWorkcenters[0].id
                        sequence += 5
                        bomLineValues = ({
                            'bom_id': odooBom.id,
                            'sequence': sequence,
                            'product_id': product.id,
                            'product_qty': chiBomMaterials[idxMaterials].QtyOfBatch,
                            'product_uom_id': product.uom_id.id,
                            'routing_id': routing_id,
                            'operation_id': operation_id,
                            })
                    idxMaterials += 1
                else:
                    product = _getProduct(self, chiBomProcesses[idxProcesses].MkPgmId)
                    if product == None:
                        _logger.warning('Product template ' + chiBomProcesses[idxProcesses].MkPgmId + ' not found in migrate_bom:', exc_info=True)
                    else:
                        routing_id = None
                        operation_id = None
                        # assuming routingWorkcenters got one to one correspondence with chiBomProcesses
                        # skipping the first routingWorkcenter as it is the added material acquisition workcenter
                        if idxProcesses + 1 < len(routingWorkcenters):
                            routing_id = odooRouting.id
                            operation_id = routingWorkcenters[idxProcesses + 1].id
                        sequence += 5
                        bomLineValues = ({
                            'bom_id': odooBom.id,
                            'sequence': sequence,
                            'product_id': product.id,
                            'product_qty': 1,
                            'product_uom_id': product.uom_id.id,
                            'routing_id': routing_id,
                            'operation_id': operation_id,
                            })
                    idxProcesses += 1
                if bomLineValues != None:
                    bomLineModel.create(bomLineValues)
            except Exception:
                _logger.warning('Exception in migrate_bom:', exc_info=True)
                continue
                
    def _migrate_chiBom(self, cursorChi):
        chiBoms = cursorChi.execute('SELECT ProductId, ProductName, ItemNo, CurVersion, Flag, NorProdtMode, BatchAmount FROM prdBOMMain ORDER BY ProductId, ItemNo').fetchall()
        bomModel = self.env['mrp.bom']
        productTemplateModel = self.env['product.template']
        
        nCount = len(chiBoms)
        nDone = 0
        for chiBom in chiBoms:
            try:
                template = productTemplateModel.search([('default_code', '=', chiBom.ProductId)])[0]
                chiBomMaterials = cursorChi.execute(
                    u"SELECT SerNo, SubProdId, QtyOfBatch "
                    u"FROM prdBOMMats "
                    u"WHERE ProductId='" + chiBom.ProductId.decode('utf-8') + u"' and ItemNo=" + str(chiBom.ItemNo) + u" "
                    u"ORDER BY SerNo").fetchall()
                chiBomProcesses = cursorChi.execute(
                    u"SELECT SerNo, MkPgmId, ProdtClass, Producer, DailyProdtQty, PrepareDays, WorkTimeOfBatch, PriceOfProc "
                    u"FROM prdBOMPgms "
                    u"WHERE MainProdId='" + chiBom.ProductId.decode('utf-8') + u"' and ItemNo=" + str(chiBom.ItemNo) + u" "
                    u"ORDER BY SerNo").fetchall()
                odooRouting = self._createRouting(chiBom, chiBomMaterials, chiBomProcesses)
                bomValues = ({
                    'code': u'~' + chiBom.ProductId.decode('utf-8') + u"#" + str(chiBom.ItemNo),
                    'product_tmpl_id': template.id,
                    'x_batom_bom_no': chiBom.ItemNo,
                    'x_version_description': chiBom.CurVersion,
                    'product_qty': chiBom.BatchAmount,
                    'type': 'normal',
                    'routing_id': odooRouting.id,
                    })
                
                odooBoms = bomModel.search([
                    ('product_tmpl_id', '=', template.id),
                    ('x_batom_bom_no', '=', chiBom.ItemNo),
                    ])
                if len(odooBoms) == 0:
                    odooBom = bomModel.create(bomValues)
                else:
                    odooBom = odooBoms[0]
                    odooBom.write(bomValues)
                self._createBomLines(odooBom, odooRouting, chiBom, chiBomMaterials, chiBomProcesses)
            except Exception:
                _logger.warning('Exception in migrate_bom:', exc_info=True)
                import pdb; pdb.set_trace()
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
                
    def _createProcessPrice(self, applicableProductAttribute, chiBom, chiBomProcesses):
        productModel = self.env['product.product']
        productTemplateModel = self.env['product.template']
        productAttributeValueModel = self.env['product.attribute.value']
        productAttributeLineModel = self.env['product.attribute.line']
        productSupplierInfoModel = self.env['product.supplierinfo']
        
        dummyProductAttributeValues = productAttributeValueModel.search([('name', '=', '*')])
        if len(dummyProductAttributeValues) > 0:
            dummyProductAttributeValue = dummyProductAttributeValues[0]
        else:
            # dummy service product variant
            dummyProductAttributeValue = productAttributeValueModel.create({
                'attribute_id': applicableProductAttribute.id,
                'name': '*',
                })
        productAttributeValues = productAttributeValueModel.search([('name', '=', chiBom.ProductId)])
        if len(productAttributeValues) > 0:
            productAttributeValue = productAttributeValues[0]
        else:
            productAttributeValue = productAttributeValueModel.create({
                'attribute_id': applicableProductAttribute.id,
                'name': chiBom.ProductId,
                })
        for chiBomProcess in chiBomProcesses:
            try:
                supplier = _getSupplier(self, chiBomProcess.Producer, True)
                processProductTemplate = _getProductTemplate(self, chiBomProcess.MkPgmId)
                if supplier != None and processProductTemplate != None:
                    addedVariantValueIds = []
                    productAttributeLines = productAttributeLineModel.search([
                        ('product_tmpl_id', '=', processProductTemplate.id),
                        ('attribute_id', '=', applicableProductAttribute.id),
                        ])
                    if len(productAttributeLines) > 0:
                        productAttributeLine = productAttributeLines[0]
                        if productAttributeValue not in productAttributeLine.value_ids:
                            productAttributeLine.write({
                                'value_ids': [(4, productAttributeValue.id)]
                                })
                            addedVariantValueIds = [productAttributeValue.id]
                    else:
                        productAttributeLine = productAttributeLineModel.create({
                            'product_tmpl_id': processProductTemplate.id,
                            'attribute_id': applicableProductAttribute.id,
                            # it needs 2 or more attribute values for creating product variants
                            'value_ids': [(6, 0, [dummyProductAttributeValue.id, productAttributeValue.id])],
                            })
                        addedVariantValueIds = [dummyProductAttributeValue.id, productAttributeValue.id]
                    addedVariantProduct = None
                    if len(addedVariantValueIds) > 0: 
                        # create the per product process product variant
                        processProductTemplate.create_variant_ids()
                        for addedVariantValueId in addedVariantValueIds:
                            addedVariantValue = productAttributeValueModel.browse(addedVariantValueId)
                            perProductProcessCode = processProductTemplate.default_code + u'->' + addedVariantValue.name
                            perProductProcessName = processProductTemplate.name + u'->' + chiBom.ProductName.decode('utf-8')
                            for product in addedVariantValue.product_ids:
                                product.write({
                                    'default_code': perProductProcessCode,
                                    'name': None if (addedVariantValue.name == '*') else perProductProcessName
                                    })
                                if addedVariantValue.name != '*':
                                    addedVariantProduct = product
                    if addedVariantProduct != None:
                        productSupplierInfos = productSupplierInfoModel.search([
                            ('name', '=', supplier.id),
                            ('product_code', '=', addedVariantProduct.default_code),
                            ('price', '=', chiBomProcess.PriceOfProc),
                            '|', ('date_start', '=', chiBom.EffectDate), ('price', '=', 0),
                            ('product_id', '=', addedVariantProduct.id),
                            ])
                        if len(productSupplierInfos) <= 0:
                            productSupplierInfoValues = ({
                                'name': supplier.id,
                                'product_name': supplier.display_name + ' -> ' + addedVariantProduct.name,
                                'product_code': addedVariantProduct.default_code,
                                'price': chiBomProcess.PriceOfProc,
                                'date_start': chiBom.EffectDate,
                                'product_id': addedVariantProduct.id,
                                'product_tmpl_id': addedVariantProduct.product_tmpl_id.id,
                                })
                            productSupplierInfoModel.create(productSupplierInfoValues)
            except Exception:
                _logger.warning('Exception in migrate_bom:', exc_info=True)
                continue
        
    def _migrate_chiProcessPrice(self, cursorChi):
        chiBoms = cursorChi.execute('SELECT ProductId, ProductName, ItemNo, CurVersion, Flag, NorProdtMode, BatchAmount, EffectDate FROM prdBOMMain ORDER BY ProductId, ItemNo').fetchall()
        productAttributeModel = self.env['product.attribute']
        
        # applicable products for a specific process
        applicableProductAttributes = productAttributeModel.search([('name', '=', u'適用產品')])
        if len(applicableProductAttributes) > 0:
            applicableProductAttribute = applicableProductAttributes[0]
        else:
            applicableProductAttribute = productAttributeModel.create({
                'name': u'適用產品',
                })
        
        nCount = len(chiBoms)
        nDone = 0
        for chiBom in chiBoms:
            try:
                chiBomProcesses = cursorChi.execute(
                    u"SELECT SerNo, MkPgmId, ProdtClass, Producer, DailyProdtQty, PrepareDays, WorkTimeOfBatch, PriceOfProc "
                    u"FROM prdBOMPgms "
                    u"WHERE MainProdId='" + chiBom.ProductId.decode('utf-8') + u"' and ItemNo=" + str(chiBom.ItemNo) + u" "
                    u"ORDER BY SerNo").fetchall()
                self._createProcessPrice(applicableProductAttribute, chiBom, chiBomProcesses)
            except Exception:
                _logger.warning('Exception in migrate_bom:', exc_info=True)
                continue
            nDone += 1
            if nDone % 10 == 0:
                print str(nDone) + '/' + str(nCount)
                self.env.cr.commit()
        self.env.cr.commit()
        
    def _migrate_inRouting(self, cursorBatom):
        inProducts = cursorBatom.execute('SELECT ProdId, ProdName, EngName, Remark, Unit FROM Product ORDER BY ProdId').fetchall()
        productModel = self.env['product.product']
        for inProduct in inProducts:
            try:
                odooProducts = productModel.search([('default_code', '=', inProduct.ProdId)])
                if len(odooProducts) == 0:
                    if inProduct.ProdName and inProduct.ProdName.strip():
                        name = inProduct.ProdName
                    else:
                        name = inProduct.ProdId
                    uom_id = _uomIdConversion(self, inProduct.Unit.decode('utf-8'))
                    sale_ok = False
                    purchase_ok = False
                    type = 'product'
                    productValues = ({
                        'name': name,
                        'default_code': inProduct.ProdId,
                        'type': type,
                        'sale_ok': sale_ok,
                        'purchase_ok': purchase_ok,
                        'description': inProduct.Remark,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        })
                    
                    odooProduct = productModel.create(productValues)
                    if inProduct.EngName and inProduct.EngName.strip():
                        engName = inProduct.EngName
                        _updateTranslation(self, 'product.template,name', odooProduct.product_tmpl_id.id, engName, name)
            except Exception:
                _logger.warning('Exception in migrate_product:', exc_info=True)
                continue
        self.env.cr.commit()
            
    @api.multi
    def migrate_bom(self):
        try:
            self.ensure_one()
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            connChi = dbChi.conn_open()
            cursorChi = connChi.cursor()
            connBatom = dbBatom.conn_open()
            cursorBatom = connBatom.cursor()

            self._migrate_chiBom(cursorChi)
            #self._migrate_chiProcessPrice(cursorChi)
            # self._migrate_inRouting(cursorBatom)
            connChi.close()
            connBatom.close()
        except Exception:
            _logger.warning('Exception in migrate_bom:', exc_info=True)
            if connChi:
                connChi.close()
            if connBatom:
                connBatom.close()
    
class BatomPartnerMigration(models.Model):
    _name = "batom.partner_migration"
    _description = 'Partner Data Migration'
    
    type = fields.Selection([(1, 'Customer'), (2, 'Sppplier')], string='Type', required=True)
    in_id = fields.Char('入料 Id', required=False, size=20)
    in_short_name = fields.Char('入料 Short Name', required=False, size=12)
    in_full_name = fields.Char('入料 Full Name', required=False, size=80)
    chi_id = fields.Char('正航 Id', required=False, size=20)
    chi_short_name = fields.Char('正航 Short Name', required=False, size=12)
    chi_full_name = fields.Char('正航 Full Name', required=False, size=80)
    odoo_id = fields.Char('Odoo Id', required=False, size=20)
    odoo_short_name = fields.Char('Odoo Short Name', required=False, size=12)
    odoo_full_name = fields.Char('Odoo Full Name', required=False, size=80)

# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import logging
from odoo import models, fields, api,  _
import odoo
import odoo.addons.base_external_dbsource

_logger = logging.getLogger(__name__)

class _partner_migration:
    def __init__(self, id, shortName, fullName):
        self.id = id
        self.shortName = shortName
        self.fullName = fullName

class _partner_address:
    def __init__(self, zip, address, contactName, title, phone, fax, memo):
        self.zip = zip
        self.city = None
        self.state_id = None
        self.street = address
        self.street2 = None
        self.contactName = contactName
        self.title = title
        self.phone = phone
        self.fax = fax
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
    
    def _currencyIdConversion(self, currencyID):
        currencyIds = self.env['res.currency'].search([('name', '=', currencyID)]).ids
        returnedCurrencyId = None
        if len(currencyIds) > 0:
            returnedCurrencyId = currencyIds.pop(0)
        return returnedCurrencyId
        
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
        newPartner = partnerModel.create({
            'parent_id': parentPartner.id,
            'type': type,
            'email': parentPartner.email,
            'fax': address.fax,
            'name': address.contactName,
            'commercial_company_name': parentPartner.commercial_company_name,
            'mobile': parentPartner.mobile if (type == 'contact') else None,
            'phone': address.phone,
            'is_company': 1 if (type != 'contact') else 0,
            'customer': parentPartner.customer,
            'supplier': parentPartner.supplier,
            'zip': address.zip,
            'city': address.city,
            'state_id': address.state_id,
            'street': address.street,
            'street2': address.street2,
            })
        newPartner.write({'display_name': self._contactDisplayName(type, parentPartner.name, address.contactName)})
     
    @api.multi
    def refresh_partner_data(self):
        try:
            self.ensure_one()
            dbBatom = self.env['base.external.dbsource'].search([('name', '=', 'Batom')])
            dbChi = self.env['base.external.dbsource'].search([('name', '=', 'CHIComp01')])
            batomCustomers = dbBatom.execute('SELECT ID, ShortName, FullName FROM Customer ORDER BY ID')
            chiCustomers = dbChi.execute('SELECT ID, ShortName, FullName FROM comCustomer WHERE Flag=1 ORDER BY ID')
            odooCustomerIds = self.env['res.partner'].search([('is_company', '=', True), ('customer', '=', True)], order='id').ids
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
            odooSupplierIds = self.env['res.partner'].search([('is_company', '=', True), ('supplier', '=', True)], order='id').ids
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
                                    addressShipping = _partner_address(addresses.ZipCode1, addresses.Address1, addresses.LinkMan1, addresses.LinkManProf1, addresses.Telephone1, addresses.FaxNo1, addresses.Memo1)
                                    address = addressShipping
                                if addresses.Address2 != None:
                                    addressInvoice = _partner_address(addresses.ZipCode2, addresses.Address2, addresses.LinkMan2, addresses.LinkManProf2, addresses.Telephone2, addresses.FaxNo2, addresses.Memo2)
                                    if address == None:
                                        address = addressInvoice
                                if addresses.Address3 != None:
                                    addressOther = _partner_address(addresses.ZipCode3, addresses.Address3, addresses.LinkMan3, addresses.LinkManProf3, addresses.Telephone3, addresses.FaxNo3, addresses.Memo3)
                                    if address == None:
                                        address = addressOther
                            
                            newPartner = partnerModel.create({
                                codeColumnName: chiPartner.ID,
                                'country_id': self._countryIdConversion(chiPartner.AreaID),
                                'category_id': (6, 0, [self._partnerCategoryConversion(migration.type, chiPartner.ClassID)]),
                                'property_purchase_currency_id': self._currencyIdConversion(chiPartner.CurrencyID),
                                'email': chiPartner.Email,
                                'fax': chiPartner.FaxNo if (chiPartner.FaxNo != None and chiPartner.FaxNo and chiPartner.FaxNo.strip()) else (
                                    address.fax if address != None else None),
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
                                contact = _partner_address(None, None, chiPartner.LinkMan, chiPartner.LinkManProf, newPartner.phone, newPartner.fax, None)
                                self._createPartnerContact('contact', newPartner, contact)
                            if addressShipping != None:
                                self._createPartnerContact('delivery', newPartner, addressShipping)
                            if addressInvoice != None:
                                self._createPartnerContact('invoice', newPartner, addressInvoice)
                            if addressOther != None:
                               self._createPartnerContact('other', newPartner, addressOther)
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
            
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'batom.partner_migration',
            'target': 'current',
            'res_id': 'view_partner_migration_tree',
            'type': 'ir.actions.act_window'
        }

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

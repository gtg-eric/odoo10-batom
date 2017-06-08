# -*- coding: utf-8 -*-
# © 2012 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import re

from odoo import models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from ldap.filter import filter_format
except ImportError:
    _logger.debug('Can not `from ldap.filter import filter_format`.')


class BatomCompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    @api.multi
    def action_populate(self):
        """
        Prepopulate the user table from one or more LDAP resources.

        Obviously, the option to create users must be toggled in
        the LDAP configuration.

        Return the number of users created (as far as we can tell).
        """
        users_pool = self.env['res.users']
        users_no_before = users_pool.search_count([])
        logger = logging.getLogger('orm.ldap')
        logger.debug("action_populate called on res.company.ldap ids %s",
                     self.ids)

        for conf in self.get_ldap_dicts():
            if not conf['create_user']:
                continue
            attribute_match = re.search(
                r'([a-zA-Z_]+)=\%s', conf['ldap_filter'])
            if attribute_match:
                login_attr = attribute_match.group(1)
            else:
                raise UserError(
                    _("No login attribute found: "
                      "Could not extract login attribute from filter %s") %
                    conf['ldap_filter'])
            ldap_filter = filter_format(conf['ldap_filter'] % '*', ())
            for result in self.query(conf, ldap_filter.encode('utf-8')):
                try:
                    if login_attr in result[1]:
                        mail = result[1]['mail'][0].strip() if 'mail' in result[1] else None
                        if mail:
                            user_id = self.get_or_create_user(conf, result[1][login_attr][0], result)
                            displayName = re.sub(r'[\x00-\x1F]', '', result[1]['displayName'][0]) if 'displayName' in result[1] else 'NoName' 
                            
                            # 搜尋 "res.users" table(users結果為list)，如果存在則寫入真實姓名
                            users = self.env['res.users'].search([('id', '=', user_id)])
                            if users:
                                users[0].write({'name': displayName})   
                                
                            departmentName = re.sub(r'[\x00-\x1F]', '', result[1]['department'][0]) if 'department' in result[1] else 'NoName'
                            departmentId = self.getDepartmentId(re.sub(r'[\x00-\x1F]', '', departmentName))
                            self.get_or_create_employee(user_id, result[1][login_attr][0], mail, displayName, departmentId)
                            
                except Exception:
                    _logger.warning('Exception in get_or_create_employee:', exc_info=True)

        users_no_after = users_pool.search_count([])
        users_created = users_no_after - users_no_before
        logger.debug("%d users created", users_created)
        
        return users_created
    
    def get_or_create_employee(self, user_id, login, email, displayName, departmentId):
        
        employee = False
        try:
            employee_values = {}
            employee_values['user_id'] = user_id
            employee_values['code'] = login
            employee_values['work_email'] = email
            employee_values['name'] = displayName
            if departmentId:
                employee_values['department_id'] = departmentId
            employees = self.env['hr.employee'].search([
                ('code', '=', login)
                ])
            if employees:
                employee = employees[0]
                # 檢查人事資料並補齊
                self.submitEmployeeInfo(employee, employee_values)
            else:
                employee = self.env['hr.employee'].create(employee_values)
                  
            self.env.cr.commit()
        except Exception:
            _logger.warning('Exception in get_or_create_employee:', exc_info=True)
        return employee
    
    def getDepartmentId(self, name):
        department = False
        try:
            departments = self.env['hr.department'].search([
                ('name', '=', name)
                ])
            if departments:
                department = departments[0]
        except Exception:
            pass
        
        return department.id if department else None
        
    # 補齊人事資料
    def submitEmployeeInfo(self, employee, employee_values):
        if not employee.work_email:
            employee.write({'work_email': employee_values['work_email']}) 
        return True
# -*- coding: utf-8 -*-

from openerp import models, fields, api

class batom_res_company(models.Model):
    #_name = 'batom_res_company.batom_res_company'
    
    _inherit = 'res.company'
    x_code = fields.Char('Company Code')
    _order = 'x_code' 

class batom_res_user(models.Model):
    #_name = 'batom_res_user.batom_res_user'
    
    _inherit = 'res.users'
    _order = 'login' 




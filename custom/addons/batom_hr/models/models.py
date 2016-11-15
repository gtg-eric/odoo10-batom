# -*- coding: utf-8 -*-

from openerp import models, fields, api

class batom_hr_department(models.Model):
    #_name = 'batom_hr_department.batom_hr_department'
    
    _inherit = 'hr.department'
    x_code = fields.Char('Department Code')
    _order = 'x_code' 

class batom_hr_employee(models.Model):
    #_name = 'batom_hr_department.batom_hr_employee'
    
    _inherit = 'hr.employee'
    x_code = fields.Char('Employee Code')
    x_on_board_date = fields.Date('On-board Date')
    x_resignation_date = fields.Date('Resignation Date')
    _order = 'x_code' 




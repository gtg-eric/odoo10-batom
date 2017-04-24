# -*- coding: utf-8 -*-

from openerp import models, fields, api

class batom_hr_department(models.Model):
    _inherit = 'hr.department'
    x_code = fields.Char('Department Code')
    _order = 'x_code' 

class batom_hr_employee(models.Model):
    _inherit = 'hr.employee'
    x_on_board_date = fields.Date('On-board Date')
    x_resignation_date = fields.Date('Resignation Date')
    _order = 'code' 

class batom_resource_resource(models.Model):
    _inherit = 'resource.resource'
    x_english_name = fields.Char('English Name')

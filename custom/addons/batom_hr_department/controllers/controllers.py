# -*- coding: utf-8 -*-
from openerp import http

# class BatomHrDepartment(http.Controller):
#     @http.route('/batom_hr_department/batom_hr_department/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/batom_hr_department/batom_hr_department/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('batom_hr_department.listing', {
#             'root': '/batom_hr_department/batom_hr_department',
#             'objects': http.request.env['batom_hr_department.batom_hr_department'].search([]),
#         })

#     @http.route('/batom_hr_department/batom_hr_department/objects/<model("batom_hr_department.batom_hr_department"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('batom_hr_department.object', {
#             'object': obj
#         })
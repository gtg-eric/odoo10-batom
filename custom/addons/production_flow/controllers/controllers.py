# -*- coding: utf-8 -*-
from openerp import http

# class ProductionFlow(http.Controller):
#     @http.route('/production_flow/production_flow/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/production_flow/production_flow/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('production_flow.listing', {
#             'root': '/production_flow/production_flow',
#             'objects': http.request.env['production_flow.production_flow'].search([]),
#         })

#     @http.route('/production_flow/production_flow/objects/<model("production_flow.production_flow"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('production_flow.object', {
#             'object': obj
#         })
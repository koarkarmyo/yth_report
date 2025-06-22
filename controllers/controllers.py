# -*- coding: utf-8 -*-
# from odoo import http


# class PadethaReports(http.Controller):
#     @http.route('/padetha_reports/padetha_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/padetha_reports/padetha_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('padetha_reports.listing', {
#             'root': '/padetha_reports/padetha_reports',
#             'objects': http.request.env['padetha_reports.padetha_reports'].search([]),
#         })

#     @http.route('/padetha_reports/padetha_reports/objects/<model("padetha_reports.padetha_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('padetha_reports.object', {
#             'object': obj
#         })


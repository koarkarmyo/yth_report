from odoo import models, api

class SaleA5Report(models.AbstractModel):
    _name = 'report.padetha_reports.sales_customize_report'
    _description = 'Sales Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }

class SalesAddressPrint(models.AbstractModel):
    _name = 'report.padetha_reports.address_print_template'
    _description = 'Address Print'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }

class SalesPanSar(models.AbstractModel):
    _name = 'report.padetha_reports.pan_sar_template'
    _description = 'Pan Sar Print'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }
from odoo import models, api

class SalesWithPhoto(models.AbstractModel):
    _name = 'report.padetha_reports.report_sales_order_with_photo'
    _description = 'Sales With Photo Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
        }
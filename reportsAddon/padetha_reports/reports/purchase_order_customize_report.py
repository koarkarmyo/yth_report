from odoo import models, api

class PurchaseOrderCustom(models.AbstractModel):
    _name = 'report.padetha_reports.report_customize_purchase_order'
    _description = 'Purchase Order Customize Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
        }
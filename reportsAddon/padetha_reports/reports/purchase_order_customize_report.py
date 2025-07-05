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

class PurchaseQuotationCustom(models.AbstractModel):
    _name = 'report.padetha_reports.report_customize_purchase_quotation'
    _description = 'Purchase Quotation Customize Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
        }

class PurchaseWithPhoto(models.AbstractModel):
    _name = 'report.padetha_reports.report_purchase_order_with_photo'
    _description = 'Purchase With Photo Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
        }
from odoo import models, api

class SaleA5Report(models.AbstractModel):
    _name = 'report.padetha_reports.a5_voucher_batch_order_list_template'
    _description = 'Batch Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking.batch'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking.batch',
            'docs': docs,
        }
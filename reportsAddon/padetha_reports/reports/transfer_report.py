from odoo import models, api


class TransferReport(models.AbstractModel):
    _name = 'report.padetha_reports.transfer_report_template'
    _description = 'Transfer Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }

from odoo import models, api


class DeliveryReturnReport(models.AbstractModel):
    _name = 'report.padetha_reports.delivery_return_report_template'
    _description = 'Delivery Return Print'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }

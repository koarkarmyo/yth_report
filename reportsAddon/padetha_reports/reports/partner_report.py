from odoo import models, api


class SalesAddressPrint(models.AbstractModel):
    _name = 'report.padetha_reports.address_print_template_for_partner'
    _description = 'Address Print'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
        }

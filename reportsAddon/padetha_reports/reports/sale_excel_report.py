# -*- coding: utf-8 -*-
from odoo import models


class SaleExcelReport(models.AbstractModel):
    # The _name MUST match the 'report_name' in the XML action
    _name = 'report.padetha_reports.sales_excel_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        """
        This is the main method that generates the Excel file.
        :param workbook: The active xlsxwriter workbook.
        :param data: Data from a wizard (if any).
        :param objects: The recordset of the selected models (e.g., sale.order records).
        """
        # Loop through each selected object (sale order) if you want a sheet per order
        # For this example, we'll put all selected orders on one sheet.

        worksheet = workbook.add_worksheet('Sales Orders')

        # Define styles/formats
        header_format = workbook.add_format({
            'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter',
            'fg_color': '#D3D3D3', 'border': 1
        })
        cell_format = workbook.add_format({'border': 1})

        # Write headers
        headers = ['Order Number', 'Customer', 'Order Date', 'Total Amount', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        worksheet.set_column('A:E', 20)  # Set column widths

        # Write data rows
        row = 1
        # 'objects' contains all the sale orders selected by the user
        for order in objects:
            worksheet.write(row, 0, order.name, cell_format)
            worksheet.write(row, 1, order.partner_id.name, cell_format)
            worksheet.write(row, 2, order.date_order.strftime('%Y-%m-%d'), cell_format)
            worksheet.write(row, 3, order.amount_total, cell_format)
            worksheet.write(row, 4, dict(order._fields['state'].selection).get(order.state), cell_format)
            row += 1
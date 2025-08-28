import base64
import json
from datetime import datetime
from io import BytesIO

from pytz import timezone

from odoo import http
from odoo.http import request, content_disposition

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class SaleExcelController(http.Controller):

    def _get_multi_uom_string(self, product, quantity, env):
        if not product or quantity <= 0:
            return '0'

        parts = []
        remaining_qty = quantity

        uoms_in_category = env['uom.uom'].search([
            ('category_id', '=', product.uom_id.category_id.id)
        ])

        sorted_uoms = sorted(uoms_in_category, key=lambda u: u.ratio, reverse=True)

        for uom in sorted_uoms:
            if remaining_qty <= 1e-6:
                break

            if uom.ratio == 0:
                continue

            qty_in_current_uom = remaining_qty / uom.ratio

            if int(qty_in_current_uom) > 0:
                parts.append(f"{int(qty_in_current_uom)} {uom.name}")
                remaining_qty %= uom.ratio

        return " ".join(parts) if parts else '0'

    @http.route('/reports/sale_order/excel', type='http', auth='user', csrf=False)
    def download_sale_order_excel(self, model, ids, **kwargs):
        # Convert the string of IDs to a list of integers
        record_ids = json.loads(ids)

        sale_orders = request.env[model].browse(record_ids)

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # --- General formats ---
        header_format = workbook.add_format({
            'bold': True, 'font_size': 11, 'fg_color': '#E0E0E0',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        normal_format = workbook.add_format({'valign': 'left'})

        company_format = workbook.add_format({'bold': True, 'font_size': 12})
        bold_format = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})

        # =================================================================
        # Create Summary Sheet
        # =================================================================
        summary_sheet = workbook.add_worksheet('Summary')

        # Set column widths
        summary_sheet.set_column('A:A', 15)
        summary_sheet.set_column('B:B', 30)
        summary_sheet.set_column('D:D', 15)
        summary_sheet.set_column('E:E', 15)
        summary_sheet.set_column('I:I', 15)
        summary_sheet.set_column('J:J', 18)

        myanmar_tz = timezone('Asia/Yangon')
        now = datetime.now(myanmar_tz).replace(tzinfo=None)
        summary_sheet.write('I1', 'Date & Time', bold_format)
        summary_sheet.write_datetime('J1', now, date_format)

        summary_headers = ['Order Number', 'Customer', 'No', 'Description','UoMC','Qty','Unit Price', 'Dis%', 'Subtotal','Available Qty']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(1, col, header, header_format)

        row = 2
        line_index = 1
        for line in sale_orders.mapped('order_line'):
            summary_sheet.write(row, 0, line.order_id.name, cell_format)
            summary_sheet.write(row, 1, line.order_id.partner_id.name, cell_format)
            summary_sheet.write(row, 2, line_index, cell_format)
            summary_sheet.write(row, 3, line.product_id.name, cell_format)
            summary_sheet.write(row, 4, line.product_id.uom_category_id.name , cell_format)
            summary_sheet.write(row, 5, line.product_uom_qty, cell_format)
            summary_sheet.write(row, 6, line.price_unit, cell_format)
            summary_sheet.write(row, 7, line.discount, cell_format)
            summary_sheet.write(row, 8, line.price_subtotal, cell_format)
            product_in_total_context = line.product_id.with_context(warehouse=None)
            total_qty = product_in_total_context.virtual_available

            multi_uom_string = self._get_multi_uom_string(line.product_id, total_qty, request.env)

            summary_sheet.write(row, 9, multi_uom_string, cell_format)
            line_index += 1
            row += 1

        # =================================================================
        # Create Individual Sheets for each Sale Order
        # =================================================================
        for order in sale_orders:
            order_sheet = workbook.add_worksheet(order.name)

            # --- Set column widths ---
            order_sheet.set_column('A:B', 25)
            order_sheet.set_column('C:C', 5)
            order_sheet.set_column('D:D', 35)
            order_sheet.set_column('E:F', 15)
            order_sheet.set_column('G:H', 12)
            order_sheet.set_column('I:J', 18)
            order_sheet.set_column('H:H', 19)

            order_sheet.set_row(0, 60)
            order_sheet.set_row(1, 20)
            order_sheet.set_row(2, 15)

            company = order.company_id
            if company.logo:
                image_data = base64.b64decode(company.logo)
                image_file = BytesIO(image_data)

                order_sheet.insert_image('C1', 'logo.png', {'image_data': image_file, 'x_scale': 0.3, 'y_scale': 0.3,
                                                            'object_position': 1})
            order_sheet.write('C4', company.name, company_format)
            address_parts = [company.street, company.street2, company.city, company.state_id.name,
                             company.country_id.name]
            address = ', '.join(part for part in address_parts if part)
            order_sheet.write('C5', address)

            myanmar_tz = timezone('Asia/Yangon')
            now = datetime.now(myanmar_tz).replace(tzinfo=None)
            order_sheet.write('I1', 'Date & Time', bold_format)
            order_sheet.write_datetime('J1',  now, date_format)

            order_sheet.write('I2', order.name, company_format)

            order_sheet.write('I3', order.partner_id.name, bold_format)

            phone_numbers = ' / '.join(p for p in [order.partner_id.phone, order.partner_id.mobile] if p)
            order_sheet.write('I4', phone_numbers)

            order_sheet.write('I5', order.partner_id.street or '')

            customer = order.partner_id

            address_parts_records = [
                # customer.ward_id,
                # customer.township_id,
                customer.city,
                customer.state_id,
                customer.country_id
            ]

            existing_parts = [part for part in address_parts_records if part]

            final_name_list = []
            for part in existing_parts:
                if hasattr(part, 'name'):
                    final_name_list.append(part.name)
                else:
                    final_name_list.append(str(part))
            full_address = ", ".join(final_name_list)

            order_sheet.write('I6', full_address or '')

            row_before_table = 7
            order_sheet.write(row_before_table, 3, 'Sale Man', bold_format)
            order_sheet.write(8, 3, order.employee_id.name,normal_format)

            order_sheet.write(row_before_table, 4, 'Delivery Man', bold_format)
            order_sheet.write(8, 4,order.delivery_man.name ,normal_format)

            order_sheet.write(row_before_table, 5, 'Vehicle', bold_format)
            order_sheet.write(8, 5, order.delivery_location.name, normal_format)

            order_sheet.write(row_before_table, 7, 'Batch', bold_format)
            order_sheet.write_datetime(8, 7, order.batch_no.name, normal_format)

            order_sheet.write(row_before_table, 9, 'Order Date', bold_format)
            order_sheet.write_datetime(8, 9, order.date_order, date_format)


            table_header_row = 9
            order_headers = [
                'SO Number', 'Customer Name', 'No.', 'Product', 'UoMC',
                'Qty', 'Unit Price', 'Dis%', 'Sub Total', 'Available Qty'
            ]
            for col, header in enumerate(order_headers):
                order_sheet.write(table_header_row, col, header, header_format)

            line_row_num = table_header_row + 1
            line_no = 1
            for line in order.order_line:
                order_sheet.write(line_row_num, 0, order.name, cell_format)
                order_sheet.write(line_row_num, 1, order.partner_id.name, cell_format)
                order_sheet.write(line_row_num, 2, line_no, cell_format)
                order_sheet.write(line_row_num, 3, line.product_id.name, cell_format)
                order_sheet.write(line_row_num, 4, line.uom_category_id.name , cell_format)
                order_sheet.write(line_row_num, 5, line.product_uom_qty, cell_format)
                order_sheet.write(line_row_num, 6, line.price_unit, cell_format)
                order_sheet.write(line_row_num, 7, line.discount, cell_format)
                order_sheet.write(line_row_num, 8, line.price_subtotal, cell_format)

                # Calculate Multi UoM

                product_in_total_context = line.product_id.with_context(warehouse=None)
                total_qty = product_in_total_context.virtual_available

                multi_uom_string = self._get_multi_uom_string(line.product_id, total_qty, request.env)

                order_sheet.write(line_row_num, 9, multi_uom_string, cell_format)

                line_row_num += 1
                line_no += 1

        workbook.close()
        output.seek(0)
        file_content = output.read()

        filename = "Sales_Report.xlsx"
        if sale_orders:
            filename = f'Sales_Excel_Report_{sale_orders[0].name}.xlsx'

        return request.make_response(
            file_content,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )
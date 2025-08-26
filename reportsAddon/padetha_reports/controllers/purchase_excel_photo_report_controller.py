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
try:
    from PIL import Image
except ImportError:
    Image = None


class PurchaseExcelPhotoController(http.Controller):

    def _get_multi_uom_string(self, product, quantity, env):
        if not product or quantity <= 0:
            return '0'
        parts = []
        remaining_qty = quantity
        uoms_in_category = env['uom.uom'].search([('category_id', '=', product.uom_id.category_id.id)])
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

    @http.route('/reports/purchase_order_photo/excel', type='http', auth='user', csrf=False)
    def download_purchase_order_excel(self, model, ids, **kwargs):
        # model should be 'purchase.order'
        record_ids = json.loads(ids)

        purchase_orders = request.env[model].browse(record_ids)

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # --- General formats ---
        header_format = workbook.add_format(
            {'bold': True, 'font_size': 11, 'fg_color': '#E0E0E0', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        cell_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        company_format = workbook.add_format({'bold': True, 'font_size': 12})
        bold_format = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})
        address_format = workbook.add_format({'align': 'left', 'valign': 'vcenter'})
        normal_format = workbook.add_format({'valign': 'left'})
        image_cell_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'align': 'center'
        })

        # =================================================================
        # Create Summary Sheet
        # =================================================================
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.set_column('A:A', 20)  # PO Number
        summary_sheet.set_column('B:B', 30)  # Supplier
        summary_sheet.set_column('C:C', 5)  # No
        summary_sheet.set_column('D:D', 35)  # Product Description
        summary_sheet.set_column('E:F', 15)  # UoM, Qty
        summary_sheet.set_column('G:I', 15)  # Prices, Subtotal
        summary_sheet.set_column('J:J', 25)  # Available Qty

        myanmar_tz = timezone('Asia/Yangon')
        now = datetime.now(myanmar_tz).replace(tzinfo=None)
        summary_sheet.write('I1', 'Date & Time', bold_format)
        summary_sheet.write_datetime('J1', now, date_format)

        summary_headers = ['PO Number', 'Supplier', 'No.','Photo', 'Product', 'UoMC', 'Qty', 'Unit Price', 'Taxes', 'Subtotal',
                           'Total Available Qty']
        for col, header in enumerate(summary_headers):
            summary_sheet.write(1, col, header, header_format)

        row = 2
        line_index = 1
        # Loop through all lines of all selected purchase orders
        for line in purchase_orders.mapped('order_line'):
            summary_sheet.write(row, 0, line.order_id.name, cell_format)
            summary_sheet.write(row, 1, '', image_cell_format)
            if line.product_id.image_1920:
                image_data = base64.b64decode(line.product_id.image_1920)
                image_file = BytesIO(image_data)

                im = Image.open(image_file)
                image_width, image_height = im.size

                row_height = 90
                col_width = 18

                summary_sheet.set_row(row, row_height)
                summary_sheet.set_column('D:D', col_width)

                cell_width_px = col_width * 8
                cell_height_px = row_height * 1

                x_scale = cell_width_px / image_width
                y_scale = cell_height_px / image_height
                scale = min(x_scale, y_scale)

                scaled_width = image_width * scale
                scaled_height = image_height * scale
                x_offset = (cell_width_px - scaled_width) / 2
                y_offset =  ((cell_height_px - scaled_height) / 2) + 7


                summary_sheet.insert_image(
                    row, 1, 'product.png',
                    {
                        'image_data': image_file,
                        'x_scale': scale,
                        'y_scale': scale,
                        'x_offset': x_offset,
                        'y_offset': y_offset,
                        'object_position': 1
                    }
                )
            summary_sheet.write(row, 2, line.order_id.partner_id.name, cell_format)
            summary_sheet.write(row, 3, line_index, cell_format)
            summary_sheet.write(row, 4, line.name, cell_format)  # Use line description
            summary_sheet.write(row, 5,line.name , cell_format)#line.uom_category_id.name
            summary_sheet.write(row, 6, line.product_qty, cell_format)
            summary_sheet.write(row, 7, line.price_unit, cell_format)
            # Combine tax names
            tax_names = ', '.join(t.name for t in line.taxes_id)
            summary_sheet.write(row, 8, tax_names, cell_format)
            summary_sheet.write(row, 9, line.price_subtotal, cell_format)

            # Calculate total available stock for the product
            product_in_total_context = line.product_id.with_context(warehouse=None)
            total_qty = product_in_total_context.virtual_available
            multi_uom_string = self._get_multi_uom_string(line.product_id, total_qty, request.env)
            summary_sheet.write(row, 10, multi_uom_string, cell_format)

            line_index += 1
            row += 1

        # =================================================================
        # Create Individual Sheets for each Purchase Order
        # =================================================================
        for order in purchase_orders:
            order_sheet = workbook.add_worksheet(order.name)
            order_sheet.set_column('A:B', 25)
            order_sheet.set_column('C:C', 5)
            order_sheet.set_column('D:D', 35)
            order_sheet.set_column('E:F', 15)
            order_sheet.set_column('G:H', 12)
            order_sheet.set_column('I:J', 18)
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

            # --- PO and Supplier Info ---
            myanmar_tz = timezone('Asia/Yangon')
            now = datetime.now(myanmar_tz).replace(tzinfo=None)
            order_sheet.write('I1', 'Date & Time', bold_format)
            order_sheet.write_datetime('J1', now, date_format)
            order_sheet.write('I2', order.name, company_format)
            order_sheet.write('I3', order.partner_id.name, bold_format)
            phone_numbers = ' / '.join(p for p in [order.partner_id.phone, order.partner_id.mobile] if p)
            order_sheet.write('I4', phone_numbers)

            supplier_address = [order.partner_id.street, order.partner_id.street2, order.partner_id.city]
            order_sheet.write('I5', ', '.join(p for p in supplier_address if p))

            # --- Other Details ---
            row_before_table = 7
            order_sheet.write(row_before_table, 3, 'Buyer', bold_format)
            order_sheet.write(8, 3, order.user_id.name or '', normal_format)


            # --- Table Headers ---
            table_header_row = 9
            order_headers = [
                'PO Number', 'Supplier Name', 'No.','Photo', 'Product', 'UoMC',
                'Qty', 'Unit Price', 'Tax', 'Sub Total', 'Available Qty'
            ]
            for col, header in enumerate(order_headers):
                order_sheet.write(table_header_row, col, header, header_format)

            line_row_num = table_header_row + 1
            line_no = 1
            for line in order.order_line:
                order_sheet.write(line_row_num, 0, order.name, cell_format)
                order_sheet.write(line_row_num, 1, '', image_cell_format)
                if line.product_id.image_1920:
                    image_data = base64.b64decode(line.product_id.image_1920)
                    image_file = BytesIO(image_data)

                    im = Image.open(image_file)
                    image_width, image_height = im.size

                    row_height = 90
                    col_width = 18

                    order_sheet.set_row(line_row_num, row_height)
                    order_sheet.set_column('D:D', col_width)

                    # Excel units ကို pixels အဖြစ် ခန့်မှန်းပြောင်းလဲခြင်း
                    cell_width_px = col_width * 8
                    cell_height_px = row_height * 1

                    # ပုံကို Cell ထဲမှာ အချိုးကျ passthrough ဝင်အောင် scale တွက်ချက်ခြင်း
                    x_scale = cell_width_px / image_width
                    y_scale = cell_height_px / image_height
                    scale = min(x_scale, y_scale)

                    # 2. ပုံကို Cell ရဲ့ အလယ်တည့်တည့်ရောက်အောင် offset တွက်ချက်ခြင်း
                    scaled_width = image_width * scale
                    scaled_height = image_height * scale
                    x_offset = (cell_width_px - scaled_width) / 2
                    y_offset = ((cell_height_px - scaled_height) / 2) + 7

                    order_sheet.insert_image(
                        line_row_num, 1, 'product.png',
                        {
                            'image_data': image_file,
                            'x_scale': scale,
                            'y_scale': scale,
                            'x_offset': x_offset,
                            'y_offset': y_offset,
                            'object_position': 1
                        }
                    )
                order_sheet.write(line_row_num, 2, order.partner_id.name, cell_format)
                order_sheet.write(line_row_num, 3, line_no, cell_format)
                order_sheet.write(line_row_num, 4, line.product_id.name, cell_format)
                order_sheet.write(line_row_num, 5, line.product_id.name, cell_format)#line.uom_category_id.name
                order_sheet.write(line_row_num, 6, line.product_qty, cell_format)
                order_sheet.write(line_row_num, 7, line.price_unit, cell_format)
                tax_names = ', '.join(t.name for t in line.taxes_id)
                order_sheet.write(line_row_num, 8, tax_names, cell_format)
                order_sheet.write(line_row_num, 9, line.price_subtotal, cell_format)

                # Calculate total available stock for the product
                product_in_total_context = line.product_id.with_context(warehouse=None)
                total_qty = product_in_total_context.virtual_available
                multi_uom_string = self._get_multi_uom_string(line.product_id, total_qty, request.env)
                order_sheet.write(line_row_num, 10, multi_uom_string, cell_format)

                line_row_num += 1
                line_no += 1

        workbook.close()
        output.seek(0)
        file_content = output.read()

        filename = "Purchase_Report_Photo.xlsx"
        if purchase_orders:
            filename = f'Purchase_Excel_Report_{purchase_orders[0].name}.xlsx'

        return request.make_response(
            file_content,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )
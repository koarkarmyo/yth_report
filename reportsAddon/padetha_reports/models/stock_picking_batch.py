from datetime import datetime
from odoo import fields, models, api
import math
from collections import defaultdict


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    def get_order_total_amount(self, picking_ids):
        amount = sum(pick.sale_id.amount_total for pick in picking_ids)

        return int(amount)

    def get_total_sku_count(self, move_line_ids):
        products = []
        for pd in move_line_ids:
            if not pd.product_id.name in products:
                products.append(pd.product_id.name)
        return len(products)



    def get_product_list(self, product_lines):

        category_aggregator = {}
        total_amount = 0.0

        for line in product_lines:
            product = line.product_id
            category = product.categ_id

            # Ensure category entry exists in our aggregator
            if category.id not in category_aggregator:
                category_aggregator[category.id] = {
                    'category_name': category.name,
                    'order': category.id,  # Keep id for stable sorting later
                    'products': {}  # Using a dict for product aggregation is O(1)
                }

            order_qty = line.quantity
            total_amount += line.move_id.sale_line_id.price_subtotal

            product_aggregator = category_aggregator[category.id]['products']

            if product.id not in product_aggregator:
                product_aggregator[product.id] = {
                    "name": product.name,
                    "qty": order_qty,
                    "uom": line.product_uom_id.name,
                    "amount": line.move_id.sale_line_id.price_subtotal,
                    "barcode": product.barcode,
                    "product_obj": product
                }
            else:
                product_aggregator[product.id]['qty'] += order_qty
                product_aggregator[product.id]['amount'] = line.move_id.sale_line_id.price_subtotal

        final_category_list = []

        sorted_category_ids = sorted(category_aggregator.keys(),
                                     key=lambda cid: category_aggregator[cid]['category_name'])

        for category_id in sorted_category_ids:
            category_data = category_aggregator[category_id]

            # Convert the aggregated product dictionary to the required list format
            product_list = list(category_data['products'].values())

            # Calculate final values like 'bal_qty' for each product
            for prod_dict in product_list:
                product_obj = prod_dict.pop('product_obj')
                prod_dict['bal_qty'] = prod_dict['qty']
                # prod_dict['bal_qty'] = product_obj._get_multi_uom_long_form(prod_dict['qty'])

            final_category_list.append({
                'category_name': category_data['category_name'],
                'product_list': sorted(product_list, key=lambda p: p['name'])
            })

        # total_qty_str = self.get_total_loading(product_lines)

        return {
            'datas': final_category_list,
            # 'total_qty': total_qty_str,
            'total_amount': total_amount
        }
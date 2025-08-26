from datetime import datetime
import math
import pytz
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    def is_discount_line(self, order_line):
        discount_list = []
        for line in order_line:
            if line.discount:
                discount_list.append(line)
        return len(discount_list)

    def get_total_sku_count_for_draft_voucher(self, order_lines):
        products = []
        for line in order_lines:
            if not line.product_id.name in products:
                products.append(line.product_id.name)
        return len(products)

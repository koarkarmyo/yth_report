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

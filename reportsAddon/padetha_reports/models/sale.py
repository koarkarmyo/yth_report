from datetime import datetime
import math
import pytz
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    def get_current_page(self, order_lines):
        return math.ceil(len(order_lines) / 13)

    def is_discount_line(self, order_line):
        discount_list = []
        for line in order_line:
            if line.discount:
                discount_list.append(line)
        return len(discount_list)

    @api.model
    def get_current_datetime_myanmar(self):
        myanmar_tz = pytz.timezone('Asia/Yangon')
        now_utc = datetime.now(pytz.utc)
        now_myanmar = now_utc.astimezone(myanmar_tz)
        return now_myanmar.strftime('%d/%m/%Y %H:%M:%S')